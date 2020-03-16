import logging
import os
import structlog
import sys

TG_TOKEN = os.environ['TG_TOKEN']
FINDER_HOST = os.environ['FINDER_HOST']
LOG_LEVEL = os.environ.get('LOG_LEVEL', logging.INFO)


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout, level=LOG_LEVEL)
structlog.configure(
    processors=[
        structlog.processors.KeyValueRenderer(),
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
)
