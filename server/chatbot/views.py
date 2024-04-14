from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from .models import Message, Conversation
from .serializer import ConversationSerializer, MessageSerializer, ConversationsListSerializer
from .tasks import send_gpt_request
from langchain.memory import ConversationBufferMemory
from PyPDF2 import PdfFileReader


User = get_user_model()

class SessionState:
    def __init__(self, session_id) -> None:
        self.session_id = session_id
        self.state = "INTRO"
        self.course_ctx = ""
        self.student_ctx = ""
        self.intro_memory = ConversationBufferMemory(
            memory_key="intro_history", return_messages=True, input_key="question"
        )
        self.recommend_memory = ConversationBufferMemory(
            memory_key="recommend_history", return_messages=True, input_key="question"
        )
        self.transcript = None


class SessionStatePool:
    def __init__(self) -> None:
        self.session_states = {}

    def get_session_state(self, session_id):
        if session_id not in self.session_states:
            print("new session state")
            self.session_states[session_id] = SessionState(session_id)
        return self.session_states.get(session_id, None)

    def set_session_state(self, session_id, state):
        self.session_states[session_id] = state

    def clear_session_state(self, session_id):
        if session_id in self.session_states:
            # self.session_states.pop(session_id)
            self.session_states[session_id] = SessionState(session_id)


session_state_pool = SessionStatePool()

class ChatLog(APIView):
    def get(self, request):
        user = request.user
        logs = Message.objects.filter(user=user)
        return Response({"message": logs}, status=status.HTTP_200_OK)

class ChatReset(APIView):
    def post(self, request):
        sess_id = request.session.session_key
        session_state_pool.clear_session_state(sess_id)
        # request.session.flush()
        return JsonResponse({"message": "Session cleared."})


class ChatUpload(APIView):
    def post(self, request):
        sess_id = request.session.session_key
        sess_state = session_state_pool.get_session_state(sess_id)

        print("FILES:", request.FILES)
        file = request.FILES.get("file")

        if not file:
            return JsonResponse({"message": "No file found."})
        # Save the file temporarily
        file_name = default_storage.save(file.name, file)
        file_path = default_storage.path(file_name)

        try:
            with open(file_path, "rb") as f:
                reader = PdfFileReader(f)
                pages = [reader.getPage(i).extract_text() for i in range(reader.getNumPages())]

                sess_state.transcript = pages
                session_state_pool.set_session_state(sess_id, sess_state)

            return JsonResponse({"message": "File uploaded."})
        except Exception as e:
            print(e)
            return JsonResponse({"message": "File upload failed."})
        finally:
            default_storage.delete(file_path)


class ChatState(APIView):
    def get(self, request):
        sess_id = request.session.session_key
        sess_state = session_state_pool.get_session_state(sess_id)
        print("state: ", sess_state.state)
        print("course_ctx: ", sess_state.course_ctx)
        print("student_ctx: ", sess_state.student_ctx)
        print("intro_memory: ", sess_state.intro_memory.load_memory_variables({}))
        print(
            "recommend_memory: ", sess_state.recommend_memory.load_memory_variables({})
        )
        print("transcript: ", sess_state.transcript)
        return JsonResponse({"message": "Success."})


class Visit(APIView):
    def get(self, request):
        visit = request.session.get('visit',0) + 1
        request.session['visit'] = visit
        print('visit count: ', visit)
        print('session: ', request.session.session_key)
        return JsonResponse({"message": f"Visit count:{request.session['visit']}"})
    
# List and create conversations
class ConversationCreate(generics.CreateAPIView):
    """
    Create conversations.
    """
    serializer_class = ConversationSerializer

    # def get_queryset(self):
    #     return Conversation.objects.filter(user=self.request.user).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # create the hello message
        conversation = serializer.instance
        message = None
        try:
            message = Message(
                conversation_id=conversation.id,
                content = "Hi there! How can I assist you today with Course Recommendations?",
                is_from_user=False,
            )
            message.save()
        except ObjectDoesNotExist:
            error = f"Conversation not created correctly."
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_mgs = str(e)
            error = f"Failed to save hello as a message: {error_mgs}"
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

class ConversationList(generics.ListAPIView):
    """
    List conversations.
    """
    serializer_class = ConversationsListSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('created_at')

class ConversationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a conversation.
    """
    serializer_class = ConversationSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # Provide a suitable queryset that doesn't rely on the actual user
            return Conversation.objects.none()
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        return Conversation.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        conversation = self.get_object()
        if conversation.user != self.request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return super().delete(request, *args, **kwargs)
    
    
class ConversationFavourite(APIView):
    """
    Favourite a conversation.
    """

    def patch(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk, user=request.user)
        if conversation.favourite:
            conversation.favourite = False
            conversation.save()
            return Response({"message": "remove from favourite"}, status=status.HTTP_200_OK)
        else:
            conversation.favourite = True
            conversation.save()
            return Response({"message": "add to favourite"}, status=status.HTTP_200_OK)


# List messages in a conversation
class MessageList(generics.ListAPIView):
    """
    List messages in a conversation.
    """
    serializer_class = MessageSerializer
    # pagination_class = LastMessagesPagination

    def get_queryset(self):
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'], user=self.request.user)

        return Message.objects.filter(conversation=conversation).order_by('created_at')

class MessageCreate(generics.CreateAPIView):
    """
    Create a message in a conversation.
    """
    serializer_class = MessageSerializer

    def perform_create(self, message, is_graduate):
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'], user=self.request.user)
        # Retrieve the last 20 messages from the conversation
        messages = Message.objects.filter(conversation=conversation).order_by('-created_at')[:20][::-1]
        # Build the list of dictionaries containing the message data
        message_list = []
        for msg in messages:
            if msg.is_from_user:
                message_list.append(('human', msg.content))
            else:
                message_list.append(('ai', msg.content))

        question = message['content']

        # Call the Celery task to get a response
        task = send_gpt_request.apply_async(args=(conversation.status, message_list, self.request.user.id, self.request.user.profile, question, is_graduate))
        # print(message_list)
        res, new_user_profile, new_status = task.get()
        self.request.user.profile = new_user_profile
        self.request.user.save()
        conversation.status = new_status
        conversation.save()
        return res, conversation

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_from_user=True)
        
        assistant_response, conversation = self.perform_create(serializer.validated_data, request.data['isGraduate'])

        message = None
        try:
            # Store GPT response as a message
            message = Message(
                conversation=conversation,
                content=assistant_response,
                is_from_user=False,
            )
            message.save()
        except ObjectDoesNotExist:
            error = f"Conversation with id {conversation.id} does not exist"
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_mgs = str(e)
            error = f"Failed to save GPT response as a message: {error_mgs}"
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(MessageSerializer(message).data, status=status.HTTP_200_OK, headers=headers)


