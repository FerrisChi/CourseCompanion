from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

intro_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            """Act as an career counselor at the University of Toronto. Engage in a short conversation to conduct an assessment of a student through questions. NEVER MAKE ANY RECOMMENDATION. You need to explore the student's degree program, department, interests, academic goals, research, volunteer, industry experience and courses taken other than those on the transcript, and if they enjoyed those courses. Ask questions that encourage the student to share without feeling directly interrogated. You can provide choices or suggestions to help the studnet answer in more detail.
If you gathered enough information for assessment, output in the following format:
Degree Program: {{student's degree program}}
Department: {{department the student is in}}
Interest: {{student's interst}}
Goal: {{student's academic goal}}
Experience: {{student's experience}}
Course Taken: {{courses the student took before}}
Extra Information: {{ extra information about the student}}

Otherwise, ask a new question to the student. Keep questions under 30 words.
"""
        ),
        # The `variable_name` here is what must align with memory
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
)

rag_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
           """Format a RAG search query to look for other similar courses based on the following summarization text, skills, interests, academic goals, and courses taken, exand to include other relevant terms. This will be a search query so only include relevant terms, it doesn't need to be a full sentence. The output MUST include department code.
Input: I am in History and I am interested in Roman history, and other ancient civilizations. I am also working part time as I am in a graduate program
Output: Hist, Roman History, Ancient Civilizations, Ancient History, Ancient Greece, Roman Empire
"""
        ),
        HumanMessagePromptTemplate.from_template("{content}"),
    ],
)

candid_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            """Act as an advisor at the University of Toronto. You select {candid_size} courses from the provided course list as recommended course candidates based on their alignment with the student's personal interests, relevance to their goals, and suitability to their experience.
Output in the following format and do not provide anything else:
{{Course code #1 - Course name #1, Course code #2 - Course name #2, ..., Course code #{candid_size} - Course name #{candid_size}}}

{input_documents}

"""
        ),
        HumanMessagePromptTemplate.from_template("{question}"),
    ],
    input_variables=["input_documents", "question", "candid_size"],
)

recommend_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            """Act as an advisor at the University of Toronto. You select five courses from the provided course list as recommended course candidates based on both student and course information. Next, you score all the course candidates between 0 and 100 based on their alignment with the student's personal interests, relevance to their academic goals, and suitability to their experience. Finally, output the sorted list of courses and their corresponding scores. The course cannot be something the student has already taken, if the course name sounds very similar do not include it as it is probably a match. Do not ask questions or provide anything else.
At last, Output in the following format if you can make recommendations:
Success!
[1. {{course code #1}} {{course name #1}}; {{score #1}}; {{reason #1}}
2; {{course code #2}}; {{course name #2}}; {{score #2}}; {{reason #2}}
...
5; {{course code #5}}; {{course name #5}}; {{score #5}}; {{reason #5}}
]
Otherwise, use the following format:
Fail!
{{Other information you need to make recommendations.}}
{input_documents}

"""
        ),
        # The `variable_name` here is what must align with memory
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}"),
    ],
    input_variables=["input_documents", "question"],
)

cot_recommend_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            """Act as an advisor at the University of Toronto. You select five courses from the provided course list as recommended course candidates. You should consider if the student meet the written and underlying prerequsite of the course, its alignment with the student's personal interests, relevance to the student's academic goals and suitability to the student's experience. Next, you score all the course candidates between 0 and 100. Finally, output the sorted list of courses and their corresponding scores. The course cannot be something the student has already taken, if the course name sounds very similar do not include it as it is probably a match. Do not ask questions or provide anything else.
At last, Output in the following format if you can make recommendations:
Success!
[1. {{course code #1}} {{course name #1}}; {{score #1}}; {{reason #1}}
2; {{course code #2}}; {{course name #2}}; {{score #2}}; {{reason #2}}
...
5; {{course code #5}}; {{course name #5}}; {{score #5}}; {{reason #5}}
]
Otherwise, use the following format:
Fail!
{{Other information you need to make recommendations.}}

{input_documents}

Example:
Input: Hi! Can you recommend courses for me?

Course information:
ECE1786H - Creative Applications of Natural Language Processing
Course: Creative Applications of Natural Language Processing
Department Code: ECE
Department: Electrical and Computer Engineering
.Prerequisites: APS360H, CSC311H, ECE324H, ECE1513H, or equivalent.There has been truly remarkable progress in the capabilities of computers to process and generate language. This course covers Deep Learning approaches in Natural Language Processing (NLP), from word vectors to Transformers, including chatGPT and GPT-4. It is a project-based course that teaches the fundamentals of neural-network-based NLP and gives students the opportunity to pursue a unique project..The course lecture material begins with the basics of word-level embeddings - their properties and training. These form the basis of neural-network-based classifiers employed to do classification of sentiment, named entity recognition and many other language tasks. A significant part of the course is about the Transformer architecture - its structure, training and how it generates language. This will include the use of the transformer as a classifier, but also as in generative mode, in which language is produced in response to input language. Much of the learning will be applied in four hands-on programming assignments and in a major project. Students will work in groups of 2 to propose a project of their own choosing that makes use of these capabilities. They will execute the project and both present it formally and write a report on it..

CSC413H1 - Neural Networks and Deep Learning
Course: Neural Networks and Deep Learning
Department Code: CSC
Department: Computer Science
.It is very hard to hand-design programs to solve many real-world problems, e.g. distinguishing images of cats vs. dogs. Machine learning algorithms allow computers to learn from example data, and produce a program that does the job. Neural networks are a class of machine learning algorithms originally inspired by the brain, but which have recently have seen a lot of success at practical applications. They’re at the heart of production systems at companies like Google and Facebook for image processing, speech-to-text, and language understanding. This course gives an overview of both the foundational ideas and the recent advances in neural net algorithms..

ECE1513H - Introduction to Machine Learning
Course: Introduction to Machine Learning
Department Code: ECE
Department: Electrical and Computer Engineering
.Prerequisites: STA286H1, ECE302H1 or equivalent.Exclusions: ECE421H, ECE521H1, CSC411H1/CSC2515H, ECE1504H.An Introduction to the basic theory, the fundamental algorithms, and the computational toolboxes of machine learning. The focus is on a balanced treatment of the practical and theoretical approaches, along with hands on experience with relevant software packages. Supervised learning methods covered in the course will include: the study of linear models for classification and regression and  neural networks. Unsupervised learning methods covered in the course will include: principal component analysis, k-means clustering, and Gaussian mixture models. Techniques to control overfitting, including regularization and validation, will be covered..

CSC401H1 - Natural Language Computing
Course: Natural Language Computing
Department Code: CSC
Department: Computer Science
.Introduction to techniques involving natural language and speech in applications such as intelligent Web searching; speech recognition and synthesis; and multi-lingual systems including machine translation. N-grams, POS-tagging, semantic distance metrics, neural models of language, corpus analysis. Python and other software..Prerequisite: CSC207H1/ CSC209H1; STA247H1/ STA255H1/ STA257H1.

ECE1724H - Special Topics in Software Systems: Artificial Intelligence
Course: Special Topics in Software Systems: Artificial Intelligence
Department Code: ECE
Department: Electrical and Computer Engineering
.This course focuses on a variety of topics at the intersection of artificial intelligence, biology, and neuroscience. The goal is to explore the intersection of these related fields via both discussions with experts as well as dedicated student projects. During each week, experts (from within the University or outside) will be invited to present on a specific topic related to AI. Afterwards, a class discussion about the topic will ensue where students will have a chance to ask questions and participate in the conversations. Students will focus on a particular topic arising from one of the discussions to write a research paper (50% of their course grade), and to make a final course presentation (another 50% of their grade). There will be a weekly 1-hour time slot dedicated to instructor interactions with the students about their research paper and course presentation..

ECE1784H - Trustworthy Machine Learning
Course: Trustworthy Machine Learning
Department Code: ECE
Department: Electrical and Computer Engineering
.The deployment of machine learning in real-world systems calls for a set of complementary technologies that will ensure that machine learning is trustworthy. Here, the notion of trust is used in its broad meaning: the course covers different topics in emerging research areas related to the broader study of security and privacy in machine learning. Students will learn about attacks against computer systems leveraging machine learning, as well as defense techniques to mitigate such attacks..The course assumes students already have a basic understanding of machine learning. Students will familiarize themselves with the emerging body of literature from different research communities investigating these questions. The class is designed to help students explore new research directions and applications. Most of the course readings will come from seminal papers in the field..

CSC2511HS - Natural Language Computing
Course: Natural Language Computing
Department Code: CSC
Department: Computer Science
.Introduction to techniques involving natural language and speech in applications such as intelligent Web searching; speech recognition and synthesis; and multi-lingual systems including machine translation. N-grams, POS-tagging, semantic distance metrics, neural models of language, corpus analysis. Python and other software..Prerequisite: CSC207H1/ CSC209H1; STA247H1/ STA255H1/ STA257H1.

CSC2125HF - Topics in Software Engineering: Software engineering for machine learning
Course: Topics in Software Engineering: Software engineering for machine learning
Department Code: CSC
Department: Computer Science
.The course discusses software engineering challenges and explores state of the art solutions for building software systems with significant machine learning or AI components.  Rather than modeling and learning itself, this course focuses on issues of design, implementation, operation, validation and assurance and how these interact with the ML perspective.  The course is a mix of lectures and student presentations..

CSC2524HS - Topics in Interactive Computing: Large Language Models for Intelligent User Interfaces
Course: Topics in Interactive Computing: Large Language Models for Intelligent User Interfaces
Department Code: CSC
Department: Computer Science
.In this course we will examine Human Computer Interaction research on the use of Large Language Models (LLMs) for the development of intelligent user interfaces. We will look at how LLMs can enhance interactive systems across three specific usage domains: Education, Human-Robot Interaction, and Creativity Support Tools. This course is targeting students wishing to design new interactive systems that leverage AI technologies, or students interested in conducting studies to explore how LLMs will impact the ways we interact with technology. Students will conduct weekly readings, with student led presentations and discussions each week. A final project will make up most of the grade, while student presentation skills and participation in class and in readings will also be emphasized..

CSC485HF - Computational Linguistics
Course: Computational Linguistics
Department Code: CSC
Department: Computer Science
.Computational linguistics and the processing of language by computer. Topics include: language models; context-free grammars; chart parsing, statistical parsing; semantics and semantic interpretation; ambiguity resolution techniques; reference resolution. Emphasis on statistical learning methods for lexical, syntactic, and semantic knowledge..Prerequisite: STA247H1/ STA255H1/ STA257H1 or familiarity with basic probability theory, including Bayes’s theorem; CSC207H1/ CSC209H1 or proficiency in Python and software development..

Student information:
degree: Master of Engineering (MEng), department: Electrical and Computer Engineering, interest: Natural Language Processing, large language models, goal: To build applications using Natural Language Processing, experience: Research in graph neural networks, projects on campus navigation systems and number recognition using Transformers, volunteering in school online forum development, course_taken: Deep learning and neural network course, extra_info: Enjoyed learning about various models, including diffusion models.

Chain of thought:
ECE1786H - Creative Applications of Natural Language Processing. This course is about Natural Language Processing and large language models, which matches the interest. This courses perfectly aligns with the goal to build applications with NLP. The written prerequesite is APS360H, CSC311H, ECE324H, ECE1513H, first three of them are undergraduate courses and the last one is graduate course and these prerequiste courses are likely to be met according to the experience in the related field. Recommend it.
CSC413H1 - Neural Networks and Deep Learning. This course is about Neural Networks, which matches the interest. This course doesn't align to the goal because it's a course about theory but not application. There's no written prerequesite but the underlying prerequesite is linear algebra and calculus, which is likely to be met according to the experience in the related field. This course was taken before accroding to the course_taken information. Not recommend it.
ECE1513H - Introduction to Machine Learning. This course is about machine learning, which matches the interest. This course doesn't align to the goal because it's a basic introductory course but not an advanced course. The written prerequesite is STA286H1, ECE302H1, which is likely to be met according to the experience in the related field. This course is likely be taken before according to the project experience in this field. Not recommend it.
CSC401H1 - Natural Language Computing. This course is about Natural Language, which matches interest. This courses aligns to the goal to build applications with NLP but in a theory way. The written prerequesite is CSC207H1/ CSC209H1; STA247H1/ STA255H1/ STA257H1, which are all undergraduate courses and likely to be met in the future. Recommend it.
ECE1724H - Special Topics in Software Systems: Artificial Intelligence. This course is about Artificial Intelligence, which broadly matches the field of interest. This course aligns to the goal in the way that it's a course based on project and research paper. The underlying prerequesite is the basic knowledge of programming and machine learning, which is likely to be met according to the experience. Not Recommend it.
ECE1784H - Trustworthy Machine Learning. This course is about Machine Learning, which matches the interest but in a broader way. This course aligns little to the goal in the way becuase it focus on the notion of trust but it's a course based on project and research paper. The underlying prerequesite is the basic knowledge of machine learning and skills in paper reading, which is likely to be met according to the experience. Recommend it.
CSC2511HS - Natural Language Computing. Alghough having differnet course code, this course is the same with the CSC401H1 - Natural Language Computing. Not Recommend it.
CSC2125HF - Topics in Software Engineering: Software engineering for machine learning. This course is about software engineering and machine learning, which broadly matches the interest. The content of this course aligns to the goal in the way that it's combined the engineering challenges for machine learning but it's not a project based course. The underlying prerequesite is basic machine learning knowledge and skills for software design and development, which are likely to be met according to the course_taken and experience. Not Recommend it.
CSC2524HS - Topics in Interactive Computing: Large Language Models for Intelligent User Interfaces. This course is about Large Language Models, which perfectly matches the interest. This course aligns to the goal bacause it's a project based course and it let student to use large language model to enhance systems. The underlying prerequesite is basic knowledge of machine learning and Human Computer Interaction, which are likely to be met according to the experience and course_taken. Recommend it.
CSC485HF - Computational Linguistics. This course is about Natural Language Processing and language model, which prefectly matches the interest. This course aligns to the goal in the way that it's about the core in NLP, but it focuses on the theory. The written prerequesite is STA247H1/ STA255H1/ STA257H1 or familiarity with basic probability theory, including Bayes's theorem; CSC207H1/ CSC209H1 or proficiency in Python and software development;. These prerequsite are likely to be met in the experience or in the future. Recommend it.

Output:
rank, code, name, score, reason
1, ECE1786H, Creative Applications of Natural Language Processing, 95, This course aligns perfectly with your interest in Natural Language Processing and large language models and directly relates to your goal of building applications using NLP. It covers advanced topics such as word vectors, Transformers, and hands-on project work that would benefit from your background in graph neural networks and Transformers.
2, CSC2524HS, Topics in Interactive Computing: Large Language Models for Intelligent User Interfaces, 90, The course focuses on the use of Large Language Models in interactive systems, which is highly relevant to your interest in large language models and your goal to utilize NLP in application development.
3, CSC485HF, Computational Linguistics, 85, Computational Linguistics is core to understanding and building NLP applications, and this course includes topics that would deepen your knowledge in this area, complementing your existing experience with practical and theoretical knowledge.
4, CSC401H1, Natural Language Computing, 80, This introductory course to NLP and speech techniques is relevant to your interests and would provide foundational knowledge that could help in building diverse NLP applications, despite your previous experience which might make some of the content a review.
5, ECE1784H, Trustworthy Machine Learning, 75, While not directly focused on NLP, this course addresses the important aspects of security and privacy in machine learning, which are crucial when deploying NLP applications. Your experience in neural networks and volunteering in online forum development may give you a unique perspective on these topics.

"""
        ),
        # The `variable_name` here is what must align with memory
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}"),
    ],
    input_variables=["input_documents", "question"],
)

extract_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            """Extract the course name from the provided text. Output courses that directly related to the {{field}}. Do not output the course code or grades. Output in the following format: course_name1, course_name2 ...
            {{field}}: {profile}
            {document}"""
        ),
    ],
    input_variables=["document", "profile"],
)


"""

Course information:
MGT230H1 - Introduction to Financial Markets
Course: Introduction to Financial Markets
Department Code: MGT
Department: Management
Year of Study: 2
.Hours: 24L.This course is an introduction to financial securities and financial markets. It discusses the structure and function of financial markets, financial institutions and market participants, as well as some tools for market analysis. The objective of the course is to provide students with basic knowledge required to understand the nature of financial securities and markets and current financial issues. Not open to Rotman Commerce students..Prerequisite: MGT100H1Exclusion: RSM230H1, ECO358H1Distribution Requirements: Social Science.Breadth Requirements: Society and its Institutions (3).

ECO356H1 - Special Topics in Financial Economics
Course: Special Topics in Financial Economics
Department Code: ECO
Department: Economics
Year of Study: 3
.Hours: 24L/12T.Courses may be offered in one or more subjects each year. Students must meet the prerequisites announced by the Department..Prerequisite: See the Department of Economics website for details.Distribution Requirements: Social Science.Breadth Requirements: Society and its Institutions (3).

RSM230H1 - Financial Markets
Course: Financial Markets
Department Code: RSM
Department: Rotman School of Management, Commerce, and Business
Year of Study: 2
.Hours: 24L.Introduction to Canadian and international financial markets. This course provides an overview of the major financial institutions, financial markets, financial securities, and an introduction to valuation and trading of securities. Securities discussed include stocks and bonds, as well as some content on derivatives. Not eligible for CR/NCR option. Contact Rotman Commerce for details..Note: This course is normally taken in first year..Distribution Requirements: Social Science.Breadth Requirements: Society and its Institutions (3).

ECO359H1 - Financial Economics II: Corporate Finance
Course: Financial Economics II: Corporate Finance
Department Code: ECO
Department: Economics
Year of Study: 3
.Hours: 24L/12T.Agency and incomplete information problems inherent in financial transactions; the role of contractual arrangements in overcoming them. Financial constraints on investment decisions of firms; the financial system in economic growth; the legal system in the functioning of financial markets. A look at theoretical and empirical literature covering these issues..Prerequisite: ECO358H1Exclusion: ACT349H1, ECO359H5, MGT232H5, RSM333H1Distribution Requirements: Social Science.Breadth Requirements: Society and its Institutions (3).

ACT230H1 - Mathematics of Finance for Non-Actuaries
Course: Mathematics of Finance for Non
Department Code: ACT
Department: Accounting
Year of Study: 2
.Hours: 24L/12T.Introduction to financial mathematics, interest measurement, present value calculation, annuity valuation, loan amortization, consumer financing arrangements, bond valuation. The course is aimed at a general audience who will not be continuing in the actuarial science program. Course manuals fee: $30..Prerequisite: First-year CalculusExclusion: ACT240H1Distribution Requirements: Science.Breadth Requirements: The Physical and Mathematical Universes (5).

ECO102H1 - Principles of Macroeconomics
Course: Principles of Macroeconomics
Department Code: ECO
Department: Economics
Year of Study: 1
.Hours: 24L/12T.An introduction to economic analysis and its applications from a macroeconomic (economy-wide) perspective. Topics covered include international trade and finance, role of money and the banking system, monetary and fiscal policy. Note: graphical and quantitative analysis are used extensively..Prerequisite: ECO101H1/ ECO101H5/ MGEA02H3Exclusion: ECO105Y1, ECO100Y5, ECO102H5, MGEA05H3, MGEA06H3Recommended Preparation: MCV4U (Calculus & Vectors) and MHF4U (Advanced Functions), or equivalent secondary school mathematics creditsDistribution Requirements: Social Science.Breadth Requirements: Society and its Institutions (3).

RSM338H1 - Applications of Machine Learning in Finance
Course: Applications of Machine Learning in Finance
Department Code: RSM
Department: Rotman School of Management, Commerce, and Business
Year of Study: 3
.Hours: 24L/12T.This course provides an overview of the basic tools in data analysis and machine learning, with emphasis on their applications in finance. Data analysis and machine learning play an important role in FinTech. Individual investors and financial institutions who are able to leverage these new tools and technology will have a significant advantage. This course discusses these new opportunities and challenges. It seeks to equip students with these highly coveted skills in the market..Prerequisite: ECO220Y1/ ECO227Y1/( STA220H1, STA255H1)/( STA237H1, STA238H1)/( STA257H1, STA261H1); CSC108H1/ CSC148H1Exclusion: RSM358H1; RSM316H1 (Special Topics in Management: Machine Learning), offered in Winter 2020/Fall 2020/Winter 2021Distribution Requirements: Social Science.Breadth Requirements: The Physical and Mathematical Universes (5).

Student information:
degree: Bachelor in English Literature, department: English, interest: Applied Math, Finance, Investment Banking, goal: To work as an Investment Banking Analyst, experience: None in math or finance, course_taken: None mentioned outside of the English Literature program, extra_info: Created a podcast series on English literature genres; conducted a research project on narrative techniques in detective fiction.

chain of thought:
MGT230H1 - Introduction to Financial Markets is an introduction to finncial market, which match the interest. The written prerequesite is MGT100H1, which is likely to be met in future because MGT100H1 is a first year course.

"""