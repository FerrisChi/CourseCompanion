from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import time
import json
import sys
from stuModel import StuModel
sys.path.append("..")
from server.chatbot import getIntro, intro_prompt, student_schema


def getIntroConversation(llm, student=None):
    memory = ConversationBufferMemory(
        memory_key="intro_history", return_messages=True, input_key="question"
    )
    question = "Hi! Can you recommend a course for me?"

    while True:
        res, flag, memory = getIntro(question, llm, memory)
        if flag:
            print("Student profile:\n", res)
            break
        else:
            print("\nAdvisor: ", res)
            if student is None:
                question = input("Input:\n")
            else:
                question = student.getResponse(res)
    return res


def test_intro(student_info, llm, eval_llm):
    intro_scores = []
    for student in student_info:
        stu = StuModel(llm, eval_llm, student)
        profile = getIntroConversation(llm, stu)
        intro_score = stu.eval_profile(profile)
        print("Intro score: ", intro_score)
        intro_scores.append(intro_score)
        time.sleep(10)
    print("Total Intro score: ", sum(intro_scores) / len(intro_scores))


if __name__ == "__main__":
    student_info_path = "ba.json"
    with open(student_info_path, "r") as f:
        student_info = json.load(f)

    llm = ChatOpenAI(model_name="gpt-4-1106-preview")
    eval_llm = ChatOpenAI(model_name="gpt-4-1106-preview")

    test_intro(student_info, llm, eval_llm)
