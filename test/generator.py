from langchain_openai import ChatOpenAI
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain_experimental.tabular_synthetic_data.openai import (
    OPENAI_TEMPLATE,
    create_openai_data_generator,
)
from langchain_experimental.tabular_synthetic_data.prompts import (
    SYNTHETIC_FEW_SHOT_PREFIX,
    SYNTHETIC_FEW_SHOT_SUFFIX,
)
import json
import sys
import time

sys.path.append("..")
from server.chatbot import getRAGQuery, searchRAG


class studentInfo(BaseModel):
    degree_program: str
    department: str
    interest: str
    goal: str
    course_taken: str
    course_to_take: str
    experience: str
    extra_info: str


examples = [
    {
        "example": """degree_program: Bachelor in Social Sciences, department: Faculty of Art & Science, interest: human behavior and societal dynamics, goal: GPA of 3.8 or higher; pursue a master's degree in Social Psychology and work in the field of social research, focusing on communities' well-being and social justice issues, course_taken: Introduction to Sociology; sychology of Human Behavior; Statistics for Social Sciences; Cultural Anthropology; Social Research Methods, course_to_take: Advanced Social Psychology; Economics of Inequality; Advanced Research Methods, experience: Research Assistant: Research project investigating the impact of socioeconomic factors on access to healthcare; Led a community-driven initiative to provide educational support to underprivileged children; Internship at a Non-Profit to assisted in developing programs aimed at empowering women from marginalized backgrounds. extra_info: love literature and have published several short stories."""
    },
    {
        "example": """degree_program: Master of Engineering (MEng), department: Electrical and Computer Engineering, interest: Logic and Machine Learning; Distributed Systems; Data Analytics and Visualization, goal: want to learn distributed machine learning system; Gain practical experience through projects; Build a strong foundation for a future career in tech industry, course_taken: Trustworthy Machine Learning; Introduction to Artificial Intelligence; Advanced Programming Concepts; Data Structures and Algorithms, course_to_take: Advanced Topics in the Theory of Distributed Computing; Topics in Software Engineering: Software engineering for machine learning; Advanced Robotics and Autonomous Systems, experience: Bachelor's degree in computer engineering; Project to build a predictive models for public flow forecasts based on computer vision; Research experience in school's AI lab to build Event Tracking models on social media reviews using NLTK and Pytorch, extra_info: win the first prize in American Mathematical Competition."""
    },
    {
        "example": """degree_program: Master of Applied Science (MASc), department: Department of Computer Science, interest: Compilers and code generation; Operating Systems, goal: Publish influential papers in top computer science journals and conferences; Pursue a PhD in Computer Systems and Architecture, course_taken: Compilers and Interpreters; Operating Systems; Topics in Database Management: Database System Technology, course_to_take: Advances in Operating Systems; Parallel Computer Architecture and Programming; Topics in the Design and Implementation of Operating Systems; Research Topics in Database Management: Database System Technology,  experience: BASc in Mechanical & Industrial Engineering; Volunteered in student health education centre; Published papers in optimizing 3D printing, extra_info: won Dean's Honors List in 2018."""
    },
    {
        "example": """degree_program: Doctor of Philosophy (PhD) in Medical Science, department: Institute of Medical Science, interest: Genetic Research; Epidemiology; Neurology; Interactive and experimental learning styles, goal: Contribute to genetic therapy research; Pursue a career in medical research focusing on neurological disorders; Attend and present at international medical conferences; Develop future study plans for post-doctoral research, course_taken: Advanced Molecular Biology Techniques; Principles of Epidemiology; Neuroscience Fundamentals; Clinical Research Methods; Biostatistics for Public Health; Genetic Engineering and Biotechnology; Ethics in Medical Research, course_to_take: Advanced Neurogenetics; Innovative Therapies in Genetic Disorders; Public Health Policy and Management, experience: Bachelor's and Master's degree in Biomedical Sciences; Research assistant in a lab focusing on genetic markers for Alzheimer's disease; Volunteer experience in community health programs; Contributed to a published paper on the epidemiology of infectious diseases; Summer internship at a pharmaceutical company in drug development, extra_info: Active member of the university chess club and has attended several medical science conferences as a student representative"""
    },
]

examples_ba = [
    {
        "example": """degree_program: Bachelor in Social Sciences, department: Faculty of Art & Science, interest: human behavior and societal dynamics, goal: GPA of 3.8 or higher; pursue a master's degree in Social Psychology and work in the field of social research, focusing on communities' well-being and social justice issues, course_taken: Introduction to Sociology; sychology of Human Behavior; Statistics for Social Sciences; Cultural Anthropology; Social Research Methods, course_to_take: Advanced Social Psychology; Economics of Inequality; Advanced Research Methods, experience: Research Assistant: Research project investigating the impact of socioeconomic factors on access to healthcare; Led a community-driven initiative to provide educational support to underprivileged children; Internship at a Non-Profit to assisted in developing programs aimed at empowering women from marginalized backgrounds. extra_info: love literature and have published several short stories."""
    },
    {
        "example": """degree_program: Bachelor in Computer Engineering. department: School of Engineering. interest: Robotics, artificial intelligence, and software development; Prefers hands-on learning and interactive projects. Goal: Achieve a GPA of 3.5 or higher; secure an internship at a leading tech company; ultimately work in AI development; Plans to pursue a Master's degree in Artificial Intelligence. Courses_taken: Introduction to Computer Science; Data Structures and Algorithms; Computer Organization and Architecture; Discrete Mathematics; Operating Systems; Introduction to Robotics; Database Management Systems. Courses_to_take: Advanced Artificial Intelligence; Machine Learning; Human-Computer Interaction; Software Engineering; Embedded Systems Design; Robotics Design Lab. Experience: Internship at a local tech startup focusing on software development; Volunteered at a community center teaching basic computer skills to children; Participated in a university research project on machine learning algorithms. Extra_info: Enjoys participating in coding hackathons and has won several awards; Active member of the university's robotics club. """
    },
    {
        "example": """degree_program: Bachelor of Science in Electrical and Computer Engineering, department: Electrical and Computer Engineering, interest: Robotics, embedded systems, IoT, machine learning, goal: Develop expertise in robotics and IoT applications, work in robotics industry, achieve a GPA of 3.8 or higher, experience: Internship at tech startup focusing on IoT devices, member of university robotics club, course_taken: Digital Logic Design, Microprocessors, Introduction to Robotics, Machine Learning, Signals and Systems, Electronic Circuits, course_to_take: Advanced Robotics, Embedded Systems Design, Wireless Sensor Networks, Artificial Intelligence, Advanced IoT Applications, extra_info: Strong inclination towards practical applications of ECE in modern technologies, good balance of software and hardware skills."""
    },
    {
        "example": """degree_program: Bachelor in Business Administration, department: School of Business, interest: Finance, marketing, and entrepreneurship; Enjoys collaborative projects and case study analyses, goal: Graduate with at least a 3.6 GPA; start a business or join a Fortune 500 company in a management role; MBA in the future, courses_taken: Principles of Management; Microeconomics; Macroeconomics; Financial Accounting; Marketing Fundamentals; Business Statistics; Organizational Behavior, courses_to_take: Corporate Finance; International Business; Digital Marketing Strategies; Entrepreneurship and Venture Initiation; Business Ethics and Corporate Responsibility; Advanced Leadership, experience: Internship at a financial services firm; Co-founder of a small online retail business; Leadership role in the university's business society, extra_info: Avid reader of business journals and books; Participated in and won several business plan competitions; Enjoys networking and attending business conferences."""
    },
]

OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")


def generate(num_runs=2, file_path="student_info.json"):
    llm = ChatOpenAI(model="gpt-4-1106-preview")

    prompt_template = FewShotPromptTemplate(
        prefix=SYNTHETIC_FEW_SHOT_PREFIX,
        examples=examples_ba,
        suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
        input_variables=["subject", "extra"],
        example_prompt=OPENAI_TEMPLATE,
    )

    synthetic_data_generator = create_openai_data_generator(
        output_schema=studentInfo,
        llm=llm,
        prompt=prompt_template,
    )

    synthetic_results = synthetic_data_generator.generate(
        subject="studentInfo",
        extra="degree_program should be bachelor. Interest can include subjects of interest; learning styles. Goals can include academic goals; career goals; desired grades; learning objectives; future study plans. Courses_taken should include more than 6 courses taken in university. Experience can include related work experience; research experience; volunteer experience. Course_to_take should include the five courses that student is most likely to choose based on their interests, goals, and experience, ensuring no duplication with courses already taken.",
        runs=num_runs,
    )

    # transfer to real courses
    getCoursePrompt = PromptTemplate(
        input_variables=["course_pool", "fake_course"],
        template="For each course in the source, find one target course that is the same as or very similar to it in the course list. If no such course exists, skip it. Do not output the source course or anything else.\nOutput format: {{target_course_code #1}} - {{target_course_name #1}}; {{target_course_code #2}} - {{target_course_name #2}}; ... ;{{target_course_code #n}} - {{target_course_name #n}}\n\nsources:\n{fake_course}\n\ncourse list:\n{course_pool}",
    )

    with open(file_path, "w") as f:
        f.write("[\n")
        for i, stu in enumerate(synthetic_results):
            query = getRAGQuery(
                stu.degree_program + stu.department + stu.course_taken, llm
            )
            lowercased_query = query.lower()
            # is_graduate = (
            #     "graduate" in lowercased_query
            #     or "grad" in lowercased_query
            #     or "master" in lowercased_query
            # )
            level = "undergrad_collection"
            # if is_graduate:
            #     level = "grad_collection"
            course_pool = searchRAG(query, level, 50, return_description=False)
            chain = getCoursePrompt | llm
            formal_course_taken = chain.invoke(
                {"fake_course": stu.course_taken, "course_pool": course_pool}
            )
            stu.course_taken = formal_course_taken.content

            query = getRAGQuery(
                stu.degree_program + stu.department + stu.course_to_take, llm
            )
            course_pool = searchRAG(query, level, 50, return_description=False)
            formal_course_to_take = chain.invoke(
                {"fake_course": stu.course_to_take, "course_pool": course_pool}
            )
            course_to_take = formal_course_to_take.content

            to_take_str = ""

            # max 2 courses
            cnt = 0
            for course in course_to_take.split(";"):
                if cnt >= 3:
                    break
                if course.split(" - ")[0].strip() not in stu.course_taken:
                    if to_take_str != "":
                        to_take_str += "; "
                    to_take_str += course.strip()
                    cnt += 1
            stu.course_to_take = to_take_str

            if cnt < 3:
                continue

            print(stu)
            if i != 0:
                f.write(",\n")
            json.dump(stu.dict(), f, indent=2)

            time.sleep(10)
        f.write("\n]")

    return synthetic_results


if __name__ == "__main__":
    res = generate(num_runs=20, file_path="ba_12.8.json")
    print(res)
