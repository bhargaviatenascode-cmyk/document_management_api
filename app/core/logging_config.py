import logging

from app.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.FileHandler(settings.log_file), logging.StreamHandler()],
    )
