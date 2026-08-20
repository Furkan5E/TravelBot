from bot import TravelBot
from config import BotConfig

def main():
    config = BotConfig()
    bot = TravelBot(config)

    print("TRAVEL BOT: Hello! I'm your travel assistant.")

    try:
        while True:
            text = input("You: ")
            if text.lower() == "quit":
                print("TRAVEL BOT: Goodbye!")
                break
            print("TRAVEL BOT:", bot.respond(text))
    except KeyboardInterrupt:
        print("\nTRAVEL BOT: Goodbye!")

if __name__ == "__main__":
    main()