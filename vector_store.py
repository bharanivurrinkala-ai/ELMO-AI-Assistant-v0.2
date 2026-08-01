import logging

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# =====================================
# Logging
# =====================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("ELMO-VECTOR")


# =====================================
# Configuration
# =====================================

VECTOR_DB_PATH = "chroma_db"

COLLECTION_NAME = "elmo_documents"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# =====================================
# Embedding Model
# =====================================

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


# =====================================
# Vector Database
# =====================================

vector_db = None



def get_vector_store():

    global vector_db


    if vector_db is not None:

        return vector_db


    try:

        vector_db = Chroma(

            collection_name=COLLECTION_NAME,

            persist_directory=VECTOR_DB_PATH,

            embedding_function=embeddings

        )


        logger.info(
            "ChromaDB loaded successfully."
        )


        return vector_db


    except Exception as e:


        logger.error(
            f"Chroma loading error: {e}"
        )


        return None



# =====================================
# Add Documents
# =====================================


def add_documents(chunks):

    db = get_vector_store()


    if db is None:

        logger.error(
            "Vector database unavailable."
        )

        return False



    try:

        texts = []

        metadatas = []


        for chunk in chunks:

            texts.append(
                chunk["page_content"]
            )

            metadatas.append(
                chunk["metadata"]
            )



        db.add_texts(

            texts=texts,

            metadatas=metadatas

        )


        logger.info(
            f"Added {len(texts)} chunks to ChromaDB."
        )


        return True



    except Exception as e:


        logger.error(
            f"Document insertion error: {e}"
        )


        return False



# =====================================
# Search Documents
# =====================================


def search_documents(query, k=4):

    db = get_vector_store()


    if db is None:

        return []



    try:

        return db.similarity_search(
            query,
            k=k
        )


    except Exception as e:

        logger.error(
            f"Search error: {e}"
        )

        return []