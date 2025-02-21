import logging
import os
from datetime import datetime
from pytz import timezone

def setup_logger():
    log_directory = "/app/logs"
    os.makedirs(log_directory, exist_ok=True)

    log_file_name = datetime.now(timezone('America/Guayaquil')).strftime('logs-%d-%m-%Y.log')
    log_file_path = os.path.join(log_directory, log_file_name)

    logger = logging.getLogger("ChatAssistantsLogger")
    
    # Asegúrate de que no se añadan manejadores duplicados
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
