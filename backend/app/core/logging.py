import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    # Base directory = backend/
    BASE_DIR = Path(__file__).resolve().parents[2]

    # logs directory inside backend
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    logger = logging.getLogger("infra_analyzer")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Console logging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File logging (rotating)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()
