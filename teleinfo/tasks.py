import logging
import time
from celery import shared_task

logger = logging.getLogger("django")


@shared_task
def test_task():
    while True:
        logger.info("hello i'm in a task in celery")
        time.sleep(10)  # Attente de 10 secondes ent
