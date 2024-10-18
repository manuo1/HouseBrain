import logging
import time

logger = logging.getLogger("django")


def test_task():
    while True:
        logger.info("hello i'm in a task in celery")
        print("truc")
        time.sleep(10)  # Attente de 10 secondes ent
