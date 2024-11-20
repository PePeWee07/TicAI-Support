import PyPDF2
from config.logging_config import logger

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text is None:
                    raise ValueError(f"La página {reader.pages.index(page)} no contiene texto legible.")
                text += page_text
            return text
    except (FileNotFoundError, PyPDF2.errors.PdfReadError) as e:
        logger.error(f"No se pudo leer el archivo PDF: {e}")
        raise RuntimeError(f"No se pudo leer el archivo PDF: {e}")
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado al procesar el PDF: {e}")
        raise RuntimeError(f"Ocurrió un error inesperado al procesar el PDF: {e}")
