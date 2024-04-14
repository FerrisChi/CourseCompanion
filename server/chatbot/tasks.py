import os
import json
import PyPDF2

from django.conf import settings
from django.http import JsonResponse

from celery import shared_task
from celery.utils.log import get_task_logger

from langchain.schema import HumanMessage, AIMessage

from .gptView import getIntro, getRAGQuery, Recommend, ExtractCourse, getCandid
from .search_client import searchRAG
from .models import Message, Conversation
from users.models import UserFile
from .serializer import ConversationSerializer, MessageSerializer, ConversationsListSerializer

from langchain_openai import ChatOpenAI

logger = get_task_logger(__name__)

MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name=MODEL_NAME, openai_api_key=OPENAI_API_KEY, verbose=True)

@shared_task
def send_gpt_request(status, memory_list, user_id, user_profile, user_input, is_graduate):
    print(user_input)
    print(status)

    memory = []
    for (memory_type,memory_item) in memory_list:
        print(memory_type, memory_item)
        if memory_type == 'human':
            memory.append(HumanMessage(content=memory_item))
        elif memory_type == 'ai':
            memory.append(AIMessage(content=memory_item))

    if status == "started":
        res, end_flag, _ = getIntro(user_input, llm, memory)
        if end_flag == True:
            user_profile = res
            status = "recommend"

            # Add transcript into course_taken
            if UserFile.objects.filter(user_id=user_id).exists():
                query = getRAGQuery(user_profile, llm)
                files = UserFile.objects.filter(user_id=user_id, file__endswith=".pdf")
                transcript = ""
                for user_file in files:
                    file_path = os.path.join(settings.MEDIA_ROOT, user_file.file.name)
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfFileReader(f)
                        for page in range(reader.numPages):
                            transcript = transcript + reader.getPage(page).extractText() + ' '
                courses = ExtractCourse(transcript, query, llm)

                stu = json.loads(user_profile)
                stu["course_taken"] += courses
                user_profile = json.dumps(stu)

    if status == "recommend":
        query = getRAGQuery(user_profile, llm)
        level = "grad_collection" if is_graduate else "undergrad_collection"
        course_ctx = searchRAG(query, level, 30, True)
        course_list = course_ctx.split("\n\n")
        course_names = [
            course.split(".)")[1].split(".")[0].strip()
            for course in course_list
            if ".)" in course
        ]
        candids = getCandid(course_names, user_profile, llm)
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
            user_input, candid_course_context, user_profile, llm, []
        )
        if recomend_flag == True:
            status = "ended"

    print(res)
    return res, user_profile, status
