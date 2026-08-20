from bot import TravelBot
from config import BotConfig

def main():
    config = BotConfig()
    bot = TravelBot(config)

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

    print(f"{BLUE}TRAVEL BOT: {RESET}Hello! I'm your travel assistant.")

    try:
        while True:
            text = input(f"{GREEN}You:{RESET} ")
            if text.lower() == "quit":
                print(f"{BLUE}TRAVEL BOT:{RESET} Goodbye!")
                break
            
            response = bot.respond(text)
            print(f"{BLUE}TRAVEL BOT:{RESET} {response}")
            
    except KeyboardInterrupt:
        print(f"\n{BLUE}TRAVEL BOT:{RESET} Goodbye!")

if __name__ == "__main__":
    main()