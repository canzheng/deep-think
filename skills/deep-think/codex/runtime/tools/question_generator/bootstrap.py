from __future__ import annotations


def bootstrap_topic_state(topic: str) -> dict[str, str]:
    cleaned_topic = topic.strip()
    if not cleaned_topic:
        raise ValueError("Topic must not be empty")

    return {"topic": cleaned_topic}
