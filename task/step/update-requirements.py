import logging

logger = logging.getLogger(__name__)

def run_step(context: dict):
    with open("requirements.txt", "a", encoding="utf-8") as file:
        file.write("pypyr" + "\n")
        file.write("pepreqs" + "\n")
        file.close()
