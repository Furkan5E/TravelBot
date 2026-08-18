import os
from bot import TravelBot

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    intents_path = os.path.join(current_dir, "..", "data", "intents.json")
    facts_path = os.path.join(current_dir, "..", "data", "facts.json")
    currencies_path = os.path.join(current_dir, "..", "data", "currencies.json")

    bot = TravelBot(intents_path, facts_path, currencies_path)

    print("TRAVEL BOT: Hello! I'm your travel assistant.")

    while True:
        text = input("You: ")

        if text.lower() == "quit":
            print("TRAVEL BOT: Goodbye!")
            break

        print("TRAVEL BOT:", bot.respond(text))

if __name__ == "__main__":
    main()