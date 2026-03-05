import chromadb
from chromadb.utils import embedding_functions
import os
import chromadb.utils.embedding_functions as embedding_functions


def get_vector_collection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    chroma_dir = os.path.join(project_root,"src","database","chroma_data")

    client = chromadb.PersistentClient(path=chroma_dir)

    huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.get_or_create_collection(
        name="job_offers",
        embedding_function=huggingface_ef
    )
    return collection

def add_to_vector_db(collection, offer_data):
    text_to_vector = f"{offer_data["name"]} {offer_data["description"]}"
    collection.add(
        ids=[offer_data["job_id"]],
        documents=[text_to_vector],
        metadatas=[{
            "company": offer_data["company"],
            "link": offer_data["link"],
            "website": offer_data["website"],
            "city": offer_data["city"]
        }]
    )

def clear_vector_collection(collection):
    data = collection.get()
    ids = data['ids']
    if ids:
        collection.delete(ids = ids)
    else:
        print("Base chromadb déjà vide")

if __name__ == "__main__":
    col = get_vector_collection()
    # add_to_vector_db(col,{
    #     "job_id": "test1",
    #     "name": "dev ia",
    #     "description": "poste de dev ia python nlp",
    #     "company": "company",
    #     "link": "link",
    #     "website": "website",
    #     "city": "city"
    # })
    # add_to_vector_db(col,{
    #     "job_id": "test2",
    #     "name": "assistant maçonnerie",
    #     "description": "Triade de maison, rénovez avec nous !",
    #     "company": "company",
    #     "link": "link",
    #     "website": "website",
    #     "city": "city"
    # })
    query = "Développeur Python junior avec des connaissances en Machine Learning"
    results = col.query(
        query_texts=[query],
        n_results=2
    )

    for i in range(len(results['ids'][0])):
        print(f"Match {i+1}: {results['documents'][0][i][:100]}...")
        print(f"Score de distance: {results['distances'][0][i]}")

    clear_vector_collection(col)