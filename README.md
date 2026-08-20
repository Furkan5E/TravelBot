# TravelBot

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Build](https://img.shields.io/badge/Build-uv-purple.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg?logo=docker)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Tests](https://img.shields.io/badge/pytest-passing-brightgreen.svg)

A lightweight, object-oriented conversational AI travel assistant and CLI tool that utilises natural language processing for dynamic sentiment analysis and real time data integration.

---

## Features

* **Natural Language Processing:** Integrates NLTK's VADER for contextual sentiment analysis ( `positive` , `negative` , `neutral` ) and Subject Verb Object (SVO) entity extraction.
* **Contextual Memory Engine:** Dynamic `MemoryManager` that persists user preferences, names, and trip parameters across conversation turns.
* **Live Currency Exchange:** Real-time API integration via `requests` for instant, multi currency fiat conversions.
* **SOLID Architecture:** Utilizes the Strategy Pattern for intent routing via a dedicated `BotConfig` dataclass, ensuring a scalable and Open/Closed compliant codebase.
* **Fault Tolerant CLI:** Graceful `KeyboardInterrupt` handling with ANSI colour coded terminal formatting.
* **Automated Testing:** Comprehensive unit test suite built with `pytest` ensuring robust NLP processing and state management.

---

## Setup Instructions

Clone the repository then sync the dependencies using uv.

```bash
git clone https://github.com/Furkan5E/travelbot.git
cd travelbot
uv sync
```

Run the bot.
```bash
uv run python src/main.py
```

To run the automated tests.
```bash
uv run pytest
```

---
## Docker Instructions

Build the image.
```bash
docker build -t travelbot .
```
Run the container.
```bash
docker run -it travelbot
```
---
## Example Conversation

```text
TRAVEL BOT: Hello! I'm your travel assistant.
You: hi, my name is Bob
TRAVEL BOT: Nice to meet you, Bob! I'll remember your name.
You: I feel stressed
TRAVEL BOT: Sorry you're feeling low. A relaxing trip to Vienna might help.
You: how much is 500 dollars in yen
TRAVEL BOT: 500 Dollars is currently 76450.0 Yen.
```
