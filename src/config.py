from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

@dataclass
class BotConfig:
    intents: Path = DATA_DIR / "intents.json"
    facts: Path = DATA_DIR / "facts.json"
    currencies: Path = DATA_DIR / "currencies.json"