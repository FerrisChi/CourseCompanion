from operator import itemgetter
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.chains import create_extraction_chain
from langchain.evaluation import EvaluatorType, load_evaluator
from json import dumps

from .models import student_schema, course_schema
from .prompts import (
    intro_prompt,
    rag_prompt,
    recommend_prompt,
    cot_recommend_prompt,
    extract_prompt,
    candid_prompt,
)


def getIntro(question, llm, memory) -> tuple[str | dict, bool, any]:
    stu_ext_chain = create_extraction_chain(schema=student_schema, llm=llm)

    chain = (
        RunnablePassthrough.assign(
            chat_history=RunnableLambda(memory.load_memory_variables)
            | itemgetter("intro_history")
        )
        | intro_prompt
        | llm
    )
    inputs = {"question": question}
    res = chain.invoke(inputs)

    memory.save_context({"question": question}, {"output": res.content})

    criterion = {
        "question": "Does the output contains degree program, department, interest, goal, experience and course taken?"
    }
    evaluator = load_evaluator(EvaluatorType.CRITERIA, criteria=criterion)
    eval_result = evaluator.evaluate_strings(prediction=res.content, input=question)

    if eval_result["score"] == 1:
        stu = stu_ext_chain.run(res.content)[0]
        res = dumps(stu)
        flag = True
        print("Student profile:\n", stu)
    else:
        res = res.content
        flag = False

    return res, flag, memory


def getCandid(course_names, student_context, llm, candid_size=10):
    if type(course_names) is list:
        course_names = ", ".join(course_names)
    if type(student_context) is dict:
        student_context = dumps(student_context)

    context = (
        "Course lists:\n" + course_names + "\nStudent information:\n" + student_context
    )
    question = "Hi! Can you recommend courses for me?"
    chain = candid_prompt | llm
    inputs = {
        "input_documents": context,
        "question": question,
        "candid_size": candid_size,
    }
    res = chain.invoke(inputs)
    res = res.content
    return res


def getRAGQuery(content, llm) -> str:
    chain = rag_prompt | llm
    input = {"content": content}
    res = chain.invoke(input)

    print("Generated RAG search query:\n", res.content)
    return res.content


def Recommend(question, course_context, student_context, llm, memory) -> tuple[str, bool, any]:
    if type(course_context) is list:
        course_context = ",".join(course_context)
    elif type(course_context) is dict:
        course_context = dumps(course_context)
    if type(student_context) is dict:
        student_context = dumps(student_context)

    course_ext_chain = create_extraction_chain(schema=course_schema, llm=llm)

    context = (
        "Course information:\n"
        + course_context
        + "\nStudent information:\n"
        + student_context
    )

    chain = (
        RunnablePassthrough.assign(
            chat_history=RunnableLambda(memory.load_memory_variables)
            | itemgetter("recommend_history")
        )
        | cot_recommend_prompt
        | llm
    )
    inputs = {"input_documents": context, "question": question}
    res = chain.invoke(inputs)
    memory.save_context({"question": question}, {"output": res.content})
    recommendation_list = []
    if "Success!" in res.content:
        rec_str = res.content.replace("Success!", "", 1)
        recommendation_list = course_ext_chain.run(rec_str)
        res = dumps(recommendation_list)
        flag = True
    else:
        res = "Failed to find recommendations"
        flag = False

    if recommendation_list is not []:
        print("Recommendation generated.")
        print("rank, code, name, score, reason")
        for i, course in enumerate(recommendation_list):
            print(
                f"{i+1}, {course['code']}, {course['name']}, {course['score']}, {course['reason']}"
            )

    return res, flag, memory


def ExtractCourse(docu, profile, llm):
    chain = extract_prompt | llm

    res = chain.invoke({"document": docu, "profile": profile})
    print("Extracted courses:\n", res.content)
    return res.content
