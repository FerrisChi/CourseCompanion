from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.conf import settings

import os
import json
import PyPDF2
from .gptView import getIntro, getRAGQuery, Recommend, ExtractCourse, getCandid
from .search_client import searchRAG
from .models import Message, Conversation
from users.models import UserFile
from .serializer import ConversationSerializer, MessageSerializer

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader
from langchain.schema import HumanMessage, AIMessage

from celery import shared_task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)

MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name=MODEL_NAME, openai_api_key=OPENAI_API_KEY, verbose=True)

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


# Create your views here.
class Chat(APIView):
    throttle_scope = "chatbot"
    # permission_classes = [IsAuthenticated,]

    def post(self, request):
        json_string = request.body.decode('utf-8')
        user_input = json.loads(json_string)['message']
        is_graduate_student = json.loads(json_string)['isGraduate']
        
        request.session['is_graduate'] = is_graduate_student

        # bug not can run in local
        sess_id = request.session.session_key
        print(request.session.keys(), request.session.session_key)
        sess_state = session_state_pool.get_session_state(sess_id)

        state, course_ctx, student_ctx, intro_memory, recommend_memory, transcript = (
            sess_state.state,
            sess_state.course_ctx,
            sess_state.student_ctx,
            sess_state.intro_memory,
            sess_state.recommend_memory,
            sess_state.transcript,
        )

        print(user_input)
        print(state)

        if state == "INTRO":
            res, end_flag, intro_memory = getIntro(user_input, llm, intro_memory)
            # End quiry
            if end_flag == True:
                query = getRAGQuery(res, llm)
                
                level = "undergrad_collection"
                if (is_graduate_student):
                    level = "grad_collection"
                course_ctx = searchRAG(query, level, 30, True)
                student_ctx = res
                state = "RECOMMEND"
                user_input = "Hi! Can you recommend courses for me?"
                # Add transcript into course_taken
                if transcript is not None:
                    stu = json.loads(student_ctx)
                    courses = ExtractCourse(transcript, query, llm)
                    stu["course_taken"] += courses
                    student_ctx = json.dumps(stu)

        if state == "RECOMMEND":
            course_list = course_ctx.split("\n\n")
            course_names = [
                course.split(".)")[1].split(".")[0].strip()
                for course in course_list
                if ".)" in course
            ]
            candids = getCandid(course_names, student_ctx, llm)
            print("candids:", candids)
            candid_course_context = "\n\n".join(
                [
                    course_list[i].split(".)")[1]
                    for i in range(len(course_names))
                    if course_names[i].split("-")[0] in candids
                ]
            )
            print("candid_course_context:", candid_course_context)
            res, recomend_flag, recommend_memory = Recommend(
                user_input, candid_course_context, student_ctx, llm, recommend_memory
            )
            if recomend_flag == True:
                state = "END"

        sess_state.state = state
        sess_state.course_ctx = course_ctx
        sess_state.student_ctx = student_ctx
        sess_state.intro_memory = intro_memory
        sess_state.recommend_memory = recommend_memory
        session_state_pool.set_session_state(sess_id, sess_state)

        print(res)
        return JsonResponse({"message": res})

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
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            docu = " ".join([page.page_content for page in pages])

            sess_state.transcript = docu
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
class ConversationListCreate(generics.ListCreateAPIView):
    """
    List and create conversations.
    """
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # create the hello message
        conversation = Conversation.objects.get(id=serializer.data['id'])
        say_hi = "Hi there! How can I assist you today with Course Recommendations?",
        try:
            message = Message(
                conversation_id=conversation.id,
                content = say_hi,
                is_from_user=False,
            )
            message.save()
        except ObjectDoesNotExist:
            error = f"Conversation not created correctly."
            Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_mgs = str(e)
            error = f"Failed to save hello as a message: {error_mgs}"
            Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response({"message": say_hi}, status=status.HTTP_200_OK, headers=headers)


class ConversationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a conversation.
    """
    serializer_class = ConversationSerializer
    lookup_field = 'pk'

    def get_queryset(self):
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

        # return Message.objects.filter(conversation=conversation).select_related('conversation')
        return Message.objects.filter(conversation=conversation)

class MessageCreate(generics.CreateAPIView):
    """
    Create a message in a conversation.
    """
    serializer_class = MessageSerializer

    def perform_create(self, serializer, is_graduate):
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'], user=self.request.user)
        # Retrieve the last 20 messages from the conversation
        messages = Message.objects.filter(conversation=conversation).order_by('-created_at')[:20][::-1]
        # Build the list of dictionaries containing the message data
        message_list = []
        for msg in messages:
            if msg.is_from_user:
                message_list.append(HumanMessage(content=msg.content))
            else:
                message_list.append(AIMessage(content=msg.content))

        question = serializer.data['content']

        # Call the Celery task to get a response
        task = send_gpt_request.apply_async(args=(conversation, message_list, self.request.user, question, is_graduate))
        # print(message_list)
        response = task.get()

        serializer.save(conversation=conversation, is_from_user=True)
        return [response, conversation.id, messages[0].id]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        json_string = request.body.decode('utf-8')
        is_graduate = json.loads(json_string)['isGraduate']
        response_list = self.perform_create(serializer, is_graduate)

        assistant_response = response_list[0]
        conversation_id = response_list[1]
        last_user_message_id = response_list[2]

        try:
            # Store GPT response as a message
            message = Message(
                conversation_id=conversation_id,
                content=assistant_response,
                is_from_user=False,
            )
            message.save()
        except ObjectDoesNotExist:
            error = f"Conversation with id {conversation_id} does not exist"
            Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_mgs = str(e)
            error = f"Failed to save GPT response as a message: {error_mgs}"
            Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response({"response": assistant_response}, status=status.HTTP_200_OK, headers=headers)


@shared_task
def send_gpt_request(conversation, memory_list, user, user_input, is_graduate):
    
    print(user_input)
    print(conversation.status)

    if conversation.status == "started":
        res, end_flag, _ = getIntro(user_input, llm, memory_list)
        if end_flag == True:
            user.profile = res
            conversation.status = "recommend"

            # Add transcript into course_taken
            if UserFile.objects.filter(user_id=user.id).exists():
                query = getRAGQuery(user.profile, llm)
                files = UserFile.objects.filter(user=user, file__endswith=".pdf")
                transcript = ""
                for user_file in files:
                    file_path = os.path.join(settings.MEDIA_ROOT, user_file.file.name)
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfFileReader(f)
                        for page in range(reader.numPages):
                            transcript = transcript + reader.getPage(page).extractText() + ' '
                courses = ExtractCourse(transcript, query, llm)

                stu = json.loads(user.profile)
                stu["course_taken"] += courses
                user.profile = json.dumps(stu)

    if conversation.status == "recommend":
        query = getRAGQuery(user.profile, llm)
        level = "grad_collection" if is_graduate else "undergrad_collection"
        course_ctx = searchRAG(query, level, 30, True)
        course_list = course_ctx.split("\n\n")
        course_names = [
            course.split(".)")[1].split(".")[0].strip()
            for course in course_list
            if ".)" in course
        ]
        candids = getCandid(course_names, user.profile, llm)
        print("candids:", candids)
        candid_course_context = "\n\n".join(
            [
                course_list[i].split(".)")[1]
                for i in range(len(course_names))
                if course_names[i].split("-")[0] in candids
            ]
        )
        print("candid_course_context:", candid_course_context)

        user_input = "Hi! Can you recommend courses for me?"
        res, recomend_flag, _ = Recommend(
            user_input, candid_course_context, user.profile, llm, []
        )
        if recomend_flag == True:
            conversation.status = "ended"

    user.save()
    conversation.save()
    print(res)
    return JsonResponse({"message": res})
