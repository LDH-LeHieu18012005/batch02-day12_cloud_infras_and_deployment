"""Mock LLM used by the Docker production example."""
import random
import time


MOCK_RESPONSES = {
    "default": [
        "This is a mock AI response for the Docker production example.",
        "The containerized agent is running correctly.",
        "Your question was received by the production-style Docker agent.",
    ],
    "docker": [
        "Docker packages an app with its dependencies so it can run consistently."
    ],
    "deploy": [
        "Deployment moves the application from local development to a reachable service."
    ],
}


def ask(question: str, delay: float = 0.05) -> str:
    time.sleep(delay + random.uniform(0, 0.02))
    text = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in text:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])
