from pathlib import Path
from pypdf import PdfReader

# pyrefly: ignore [missing-import]
from src.ingestion.models import Document


def load_pdf(pdf_path: Path) -> Document:
    '''
    Load a PDF file and return a Document object.
    '''
    reader = PdfReader(str(pdf_path))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    full_text = '\n'.join(pages)

    return Document(
        text=full_text,
        source=pdf_path.stem,
        path=str(pdf_path)
    )


def load_documents(data_dir: str) -> list[Document]:
    """
    Recursively load all pdfs from the data directory.
    """

    documents = []

    for pdf_file in Path(data_dir).rglob('*.pdf'):
        try:
            document = load_pdf(pdf_file)
            documents.append(document)
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")

    return documents
