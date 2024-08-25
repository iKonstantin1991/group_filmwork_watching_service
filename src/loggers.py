import logging
from logging.handlers import TimedRotatingFileHandler

from asgi_correlation_id import CorrelationIdFilter

from src.config import settings


def setup_logging() -> None:
    handlers = (
        logging.StreamHandler(),
        TimedRotatingFileHandler(filename=settings.log_file, when="midnight"),
    )
    cid_filter = CorrelationIdFilter()
    for log_handler in handlers:
        log_handler.addFilter(cid_filter)
        log_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] [req_id:%(correlation_id)s] %(message)s"
            )
        )
    logging.basicConfig(level=logging.INFO, handlers=handlers)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
