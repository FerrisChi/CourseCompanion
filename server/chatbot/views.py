from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.core.files.storage import default_storage

import os
import json
from .gptView import getIntro, getRAGQuery, Recommend, ExtractCourse, getCandid
from .search_client import searchRAG
from .models import Message

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader


MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name=MODEL_NAME, openai_api_key=OPENAI_API_KEY, verbose=True)


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