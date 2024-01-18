from langchain.chat_models import ChatOpenAI
from stuModel import StuModel
import sys
import time
from langchain.memory import ConversationBufferMemory

sys.path.append("..")
from server.chatbot import Recommend, getCandid, searchRAG, getRAGQuery
import json


def getRecommend(stu, llm):
    query = getRAGQuery(stu.getProfileForRAG(), llm)
    level = "undergrad_collection"
    course_context = searchRAG(query, level, 30, True)
    course_list = course_context.split("\n\n")
    course_names = [
        course.split(".)")[1].split(".")[0].strip()
        for course in course_list
        if ".)" in course
    ]
    candids = getCandid(course_names, stu.getProfileWithoutCourse(), llm)

    candid_course_context = "\n\n".join(
        [
            course_list[i].split(".)")[1]
            for i in range(len(course_names))
            if course_names[i].split("-")[0] in candids
        ]
    )
    question = "Hi! Can you recommend courses for me?"
    memory = ConversationBufferMemory(
        memory_key="recommend_history", return_messages=True, input_key="question"
    )
    recommend_list, flag, memory = Recommend(
        question,
        candid_course_context,
        stu.getProfileWithTakenCourse(),
        llm,
        memory,
    )
    return recommend_list


def test(student_info, llm, eval_llm, out_path):
    f = open(out_path, "w")
    f.write("[\n")
    recalls = 0
    tots = 0
    for i, student in enumerate(student_info):
        stu = StuModel(llm, eval_llm, student)
        recommend_list = getRecommend(stu, llm)
        recommend_list = json.loads(recommend_list)
        recall, tot = stu.eval_recommd(recommend_list)
        recalls += recall
        tots += tot

        profile = stu.getProfileDict()
        profile["recommendaion"] = recommend_list
        profile["recall"] = recall / tot
        if i != 0:
            f.write(",\n")
        json.dump(profile, f, indent=2)

        print(profile)

        time.sleep(10)
    print("Tot Recall rate: ", recalls / tots)

    f.write("\n]")
    f.close()


# intro
# gpt4-1106-preview 8.325
# gpt-3.5-turbo 6.937499999999999

# recomd
# 5 attempt in 3 actual courses
# gpt-4-1106-preview 1.13
# gpt-3.5-turbo 0.79
if __name__ == "__main__":
    student_info_path = "ba.json"
    out_path = "result_4_cot.json"
    with open(student_info_path, "r") as f:
        student_info = json.load(f)

    llm = ChatOpenAI(model_name="gpt-4-1106-preview")
    eval_llm = ChatOpenAI(model_name="gpt-4-1106-preview")

    test(student_info, llm, eval_llm, out_path)
