FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . /app

RUN uv sync
RUN uv run python -m nltk.downloader vader_lexicon punkt punkt_tab averaged_perceptron_tagger

CMD ["uv", "run", "python", "src/main.py"]