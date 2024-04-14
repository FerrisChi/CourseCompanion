# Start with a Python base image
FROM python:3.10

# Set the working directory to /code
WORKDIR /server

# Add the current directory contents into the container at /code
ADD . /server


RUN echo Django >> requirements.txt \
    && echo djangorestframework >> requirements.txt \
    && echo django-cors-headers >> requirements.txt \
    && echo django-oauth-toolkit >> requirements.txt \
    && echo pyOpenSSL >> requirements.txt \
    && echo PyPDF2 >> requirements.txt \
    && echo django-extensions >> requirements.txt \
    && echo Werkzeug >> requirements.txt \
    && echo pillow >> requirements.txt \
    && echo social-auth-app-django >> requirements.txt \
    && echo django-celery-results >> requirements.txt \
    && echo celery >> requirements.txt \
    && echo chromadb >> requirements.txt \
    && echo tiktoken >> requirements.txt \
    && echo langchain >> requirements.txt \
    && echo langchain_openai >> requirements.txt \
    && echo openai >> requirements.txt \
    && echo drf-yasg >> requirements.txt


# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Make port 3000 available to the world outside this container
EXPOSE 3000

# The default command to run when the container starts. Here it's Django's runserver.
CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]
