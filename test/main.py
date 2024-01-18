from langchain.chat_models import ChatOpenAI
from test_intro import getIntroConversation
from test_recommend import getRecommend
from stuModel import StuModel


def main():
    # load_database()
    llm = ChatOpenAI(model_name="gpt-4-1106-preview")
    student_context = getIntroConversation(llm)
    stu = StuModel(llm, llm, student_context)
    recommendation_list = getRecommend(stu, llm)
    print(recommendation_list)


if __name__ == "__main__":
    main()
