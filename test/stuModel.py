from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.evaluation import load_evaluator, EvaluatorType
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough

import json

W = {"interest": 0.3, "goal": 0.3, "experience": 0.3, "extra_info": 0.1}


class StuModel:
    def __init__(self, llm, eval_llm, profile: dict):
        self.degree_program = profile["degree_program"]
        self.department = profile["department"]
        self.course_taken = [
            course.strip() for course in profile["course_taken"].split(";")
        ]
        self.course_to_take = [
            course.strip() for course in profile["course_to_take"].split(";")
        ]
        self.interest = profile["interest"]
        self.goal = profile["goal"]
        self.experience = profile["experience"]
        self.extra_info = profile["extra_info"]

        # print("program:", self.degree_program)
        # print("department:", self.department)
        # print("course_taken:", self.course_taken)
        # print("interest:", self.interest)
        # print("goal:", self.goal)
        # print("experience:", self.experience)
        # print("extra_info:", self.extra_info)

        self.llm = llm
        self.eval_llm = eval_llm
        self.memory = ConversationBufferMemory(return_messages=True)
        prompt = ChatPromptTemplate(
            input_variables=["input"],
            messages=[
                SystemMessagePromptTemplate.from_template(
                    f"You are a student in the University of Toronto. You're asked questions by advisors to help recommend course for you. You know nothing about the course provided this term or what course to take. Simply answer the question and do NOT provide other information.\nYour degree program: {self.degree_program}\n Your department: {self.department}\nYour interest: {self.interest}\nYour academic goal: {self.goal}\nYour experience: {self.experience}\nYour took courses: {self.course_taken}\nYour extra information: {self.extra_info}"
                ),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ],
        )

        self.chain = (
            RunnablePassthrough.assign(
                history=RunnableLambda(self.memory.load_memory_variables)
                | itemgetter("history")
            )
            | prompt
            | self.llm
        )

    def getProfileForRAG(self) -> str:
        return f"{self.degree_program} {self.department} {self.interest} {self.goal}"

    def getProfileWithoutCourse(self) -> str:
        return f"{self.degree_program} {self.department} {self.interest} {self.goal} {self.experience}"

    def getProfileWithTakenCourse(self) -> str:
        return f"{self.degree_program} {self.department} {self.interest} {self.goal} {self.experience} {' '.join(self.course_taken)}"

    def getProfile(self) -> str:
        return f"{self.degree_program} {self.department} {self.interest} {self.goal} {self.experience} {' '.join(self.course_taken)} {' '.join(self.course_to_take)}"

    def getProfileDict(self) -> dict:
        return {
            "program": self.degree_program,
            "department": self.department,
            "interest": self.interest,
            "goal": self.goal,
            "experience": self.experience,
            "course_taken": self.course_taken,
            "course_to_take": self.course_to_take,
        }

    def getResponse(self, message):
        response = self.chain.invoke({"input": message})
        self.memory.save_context({"input": message}, {"output": response.content})
        print("\nStudent: ", response.content)
        return response.content

    def eval_profile(self, profile):
        print("profile", profile)
        accuracy_criteria = {
            "accuracy": """
Score 1: The answer is completely unrelated to the reference.
Score 3: The answer has minor relevance but does not align with the reference.
Score 5: The answer has moderate relevance but contains inaccuracies.
Score 7: The answer aligns with the reference but has minor errors or omissions.
Score 10: The answer is completely accurate and aligns perfectly with the reference."""
        }

        evaluator = load_evaluator(
            "labeled_score_string", criteria=accuracy_criteria, llm=self.eval_llm
        )
        interest_result = evaluator.evaluate_strings(
            prediction=profile["interest"],
            reference=self.interest,
            input="What's the interest of the student?",
        )
        goal_result = evaluator.evaluate_strings(
            prediction=profile["goal"],
            reference=self.goal,
            input="what's the academic goal of the student?",
        )
        experience_result = evaluator.evaluate_strings(
            prediction=profile["experience"],
            reference=self.experience,
            input="what's the experience of the student?",
        )
        extra_info_result = evaluator.evaluate_strings(
            prediction=profile["extra_info"],
            reference=self.extra_info,
            input="what's the extra information of the student?",
        )
        score = (
            interest_result["score"] * W["interest"]
            + goal_result["score"] * W["goal"]
            + experience_result["score"] * W["experience"]
            + extra_info_result["score"] * W["extra_info"]
        )
        return score

    def eval_recommd(self, recommend_list: list[dict]) -> tuple[int, int]:
        criterion = {
            "contain": "Does the name of the input course contained in the output?"
        }

        eval_chain = load_evaluator(
            EvaluatorType.CRITERIA,
            criteria=criterion,
            llm=self.eval_llm,
        )
        recommed_courses = [course["name"] for course in recommend_list]

        hit = 0
        for course in self.course_to_take:
            query = course
            eval_result = eval_chain.evaluate_strings(
                prediction=recommed_courses, input=query
            )
            hit += eval_result["score"]
            print(eval_result)
        print(f"total hit {hit} in {len(self.course_to_take)}")
        return hit, len(self.course_to_take)
