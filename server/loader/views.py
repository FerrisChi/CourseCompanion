from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
import chromadb
from chromadb.config import Settings

class Loader(APIView):
    def post(self, request, file_path):
        res = load_database(file_path)
        return JsonResponse({"message": res})

def split_course_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        chunks = []
        current_chunk = []

        for line in file:
            if line.strip():  # Check if the line is not empty
                current_chunk.append(line)
            else:
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                    current_chunk = []

        if current_chunk:
            chunks.append(''.join(current_chunk))

    return chunks

def load_database(file):
    try:
        chroma_client = chromadb.HttpClient(host="localhost", port = 8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
        documents = []
        metadatas = []
        ids = []

        result_chunks = split_course_data(file)
        for i, chunk in enumerate(result_chunks, start=1):
            metadata = {'source': chunk.split('\n')[0].strip()}
            course_description = chunk.replace('\n', '.')

            ids.append(str(i+1))
            documents.append(course_description)
            metadatas.append(metadata)
        print('Number of Courses:')
        print(len(documents))
        collection_status = False
        while collection_status != True:
            try:
                document_collection = chroma_client.get_or_create_collection(name="sample_collection")
                collection_status = True
            except Exception as e:
                pass

        document_collection.add(documents=documents, metadatas=metadatas, ids=ids)
        return f"Successfully Index {file}"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    load_database()
    print("Done")