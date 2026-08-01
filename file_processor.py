import os
import logging

from pypdf import PdfReader
from PIL import Image

from langchain_text_splitters import RecursiveCharacterTextSplitter

from vector_store import add_documents


# =====================================
# Logging
# =====================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("ELMO-FILE")


# =====================================
# Supported Files
# =====================================

PDF_EXTENSIONS = [
    ".pdf"
]

IMAGE_EXTENSIONS = [
    ".png",
    ".jpg",
    ".jpeg"
]


# =====================================
# Main Processor
# =====================================


def process_file(file_path):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            "File not found"
        )


    extension = os.path.splitext(
        file_path
    )[1].lower()


    if extension in PDF_EXTENSIONS:

        return process_pdf(
            file_path
        )


    elif extension in IMAGE_EXTENSIONS:

        return process_image(
            file_path
        )


    else:

        raise ValueError(
            "Only PDF and images supported"
        )



# =====================================
# PDF Processing
# =====================================


def process_pdf(file_path):

    logger.info(
        "Processing PDF..."
    )


    reader = PdfReader(
        file_path
    )


    documents = []


    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):


        text = page.extract_text()


        if text:


            documents.append({

                "text": text,

                "metadata": {

                    "source": os.path.basename(
                        file_path
                    ),

                    "page": page_number

                }

            })



    if not documents:

        return "No text found in PDF"



    # -------------------------
    # Chunking
    # -------------------------

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=800,

        chunk_overlap=150

    )


    chunks = []


    for doc in documents:


        split_text = splitter.split_text(
            doc["text"]
        )


        for chunk in split_text:


            chunks.append({

                "page_content": chunk,

                "metadata": doc["metadata"]

            })



    # -------------------------
    # Store in Chroma
    # -------------------------

    add_documents(
        chunks
    )


    logger.info(
        f"Created {len(chunks)} chunks"
    )


    return (
        f"PDF processed successfully. "
        f"Created {len(chunks)} searchable chunks."
    )



# =====================================
# Image Processing
# =====================================


def process_image(file_path):

    image = Image.open(
        file_path
    )


    return f"""

Image Information:

Format : {image.format}

Mode : {image.mode}

Width : {image.width}

Height : {image.height}

"""