import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

file_path = './CourseData.txt' 
course_distributions = {}
chunks = []
current_chunk = []
with open(file_path, 'r', encoding='utf-8') as file:

    for line in file:
        if line.strip():  # Check if the line is not empty
            current_chunk.append(line)
        else:
            if current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = []

    if current_chunk:
        chunks.append(''.join(current_chunk))


    print(len(chunks))
    for elem in chunks:
        course_code = str(elem[:3])
        course_distributions[course_code] = course_distributions.get(course_code, 0) + 1

file_path = './GradCourseData.txt' 
with open(file_path, 'r', encoding='utf-8') as file:

    for line in file:
        if line.strip():  # Check if the line is not empty
            current_chunk.append(line)
        else:
            if current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = []

    if current_chunk:
        chunks.append(''.join(current_chunk))


    print(len(chunks))
    for elem in chunks:
        course_code = str(elem[:3])
        course_distributions[course_code] = course_distributions.get(course_code, 0) + 1
    
    data = {k: v for k, v in course_distributions.items() if v > 100}
    # data['Other'] = sum(v for k, v in course_distributions.items() if v < 25)
    df = pd.DataFrame(list(data.items()), columns=['Course Code', 'Number of Courses'])
    plt.figure(figsize=(15, 8))
    sns.barplot(x='Course Code', y='Number of Courses', data=df, palette='viridis')
    plt.xlabel('Course Codes')
    plt.ylabel('Number of Courses')
    plt.title('Top Courses By Course Code')
    plt.xticks(rotation=90)
    plt.show()


    description_lengths = [len(description.split()) for description in chunks]

    # Plot histogram
    plt.figure(figsize=(10, 6))
    sns.set_palette("viridis")
    sns.histplot(description_lengths, bins=20, kde=False, edgecolor='black')
    plt.title('Histogram of Course Description Lengths in Words')
    plt.xlabel('Number of Words')
    plt.ylabel('Frequency')
    plt.show()
