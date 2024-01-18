import chromadb
from chromadb.config import Settings


def searchRAG(query, level='undergrad_collection', n_results=10, return_description=True):
    chroma_client = chromadb.HttpClient(
        host="localhost",
        port=8000,
        settings=Settings(allow_reset=True, anonymized_telemetry=False),
    )
    collection_status = False
    while collection_status != True:
        try:
            document_collection = chroma_client.get_or_create_collection(
                name=level
            )
            collection_status = True
        except Exception as e:
            pass

    query = f"{query}"
    results = document_collection.query(query_texts=query, n_results=n_results)
    result_documents = results["documents"][0]
    print("RAG Search Results:")
    courseStr = ""
    i = 0
    for elem in result_documents:
        if return_description is False:
            elem = elem.split(".")[0]
        i += 1
        courseStr += str(i) + ".) " + elem
        courseStr += "\n\n"
    print(courseStr)
    return courseStr

if __name__ == "__main__":
    q = "BA, International Relations, Political Science, Global affairs, Diplomacy, Political theory, Public speaking, Debate, United Nations, NGO, Diplomatic service, International policy, Peace and conflict studies"
    print(searchRAG(q))