import logging
import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# =====================================
# Logging
# =====================================

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("ELMO-RAG")

# =====================================
# Configuration
# =====================================

DB_PATH = "chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# =====================================
# Load Embedding Model
# =====================================

try:
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    logger.info("Embedding model loaded successfully.")
except Exception as e:
    logger.error(f"Embedding loading failed: {e}")
    embedding_model = None

# =====================================
# Load Vector Database
# =====================================

vector_db = None


def load_vector_database():
    global vector_db

    if not os.path.exists(DB_PATH):
        logger.warning(
            "Chroma database not found. RAG will return empty context until documents are ingested."
        )
        return

    try:
        vector_db = Chroma(
            persist_directory=DB_PATH, embedding_function=embedding_model
        )
        logger.info("ChromaDB loaded successfully.")
    except Exception as e:
        logger.error(f"ChromaDB loading error: {e}")
        vector_db = None


load_vector_database()

# =====================================
# Retrieve Relevant Documents
# =====================================


def retrieve_context(query, k=4):
    if vector_db is None:
        logger.warning("Vector database unavailable.")
        return ""

    try:
        # Fetch documents with distance scores
        results = vector_db.similarity_search_with_score(query, k=k)

        if not results:
            return ""

        relevant_docs = []

        for doc, score in results:
            # Note: Chroma L2 distance (lower is closer).
            # Adjusted threshold guard or accepted based on standard L2 spreads.
            # If scores seem too strict, consider removing the hard threshold and relying purely on top-k.
            if score < 1.5:
                relevant_docs.append(doc.page_content)

        if not relevant_docs:
            # Fallback to top result if strict threshold filters everything out
            relevant_docs.append(results[0][0].page_content)

        context = "\n\n".join(relevant_docs)

        logger.info(f"Retrieved {len(relevant_docs)} documents for query.")

        return context[:4000]

    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        return ""