"""Mock LLM used for offline lab runs."""
import random
import time


MOCK_RESPONSES = {
    "default": [
        "This is a mock AI response. In production this would come from a real LLM provider.",
        "The agent is running correctly and received your question.",
        "Your cloud-ready AI agent processed the request successfully.",
    ],
    "docker": [
        "Docker packages an application and its dependencies so it runs consistently everywhere."
    ],
    "deploy": [
        "Deployment means moving code to a server or cloud platform where users can access it."
    ],
    "health": [
        "The service is healthy. Health checks help platforms restart or reroute traffic safely."
    ],
}


def ask(question: str, delay: float = 0.05) -> str:
    time.sleep(delay + random.uniform(0, 0.02))
    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])
