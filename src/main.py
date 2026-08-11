import json
import re
import random
import nltk
import os

from nltk import pos_tag, word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("punkt", quiet=True)
nltk.download("averaged_perceptron_tagger_eng", quiet=True)

memory = {}
sia = SentimentIntensityAnalyzer()

def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

def build_patterns(data):
    patterns = []
    for tag in data["Tags"]: #loop through each tag
        for p in tag["patterns"]: #loop through each pattern
            patterns.append({
                "tag": tag["tag"],
                "pattern": re.compile(p, re.IGNORECASE),
                "responses": tag["responses"]
            })  #store complied regex in patterns list
    return patterns

def match_input(text, patterns):
    for entry in patterns:
        # attempt to match the text
        m = entry["pattern"].search(text)
        if m:
            return entry, m.groupdict()
    return None, {} #no match


def interpret_sentiment(text):
    score = sia.polarity_scores(text)["compound"] #get vader score
    if score > 0.3:
        return "positive"
    if score < -0.3:
        return "negative"
    return "neutral"


def extract_svo(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)

    subject = None
    verb = None
    obj = None
    
    #prefer proper nouns first
    for word, pos in tagged:
        if pos in ("NNP", "NNPS"):
            return word, None, None

    #use last noun as subject otherwise
    for word, pos in tagged:
        if pos.startswith("NN"):
            subject = word

    #first verb
    for word, pos in tagged:
        if pos.startswith("VB"):
            verb = word
            break

    # Last noun/adj after verb = object
    for word, pos in tagged:
        if verb and (pos.startswith("NN") or pos.startswith("JJ")):
            obj = word

    return subject, verb, obj


def fact_query(city, facts, keyword=None):
    if not city:
        return None

    city = city.lower().strip()
    ranked = []

    for f in facts:
        lf = f.lower()
        s = 0

        # City relevance
        if city in lf:
            s += 5

        # Keyword relevance (for currency/language/population questions)
        if keyword and keyword in lf:
            s += 10

        ranked.append((s, f))

    ranked.sort(reverse=True)
    return ranked[0][1] if ranked else None

def generate_response(entry, captured, data, user_text):

    # store memory
    for key, value in captured.items():
        memory[key] = value.strip()

    tag = entry["tag"]

    # handle sentiment replies
    if tag == "feeling":
        mood = captured.get("mood", "")
        sentiment = interpret_sentiment(mood)
        suggestion_list = data["Suggestions"][sentiment]
        city = random.choice(suggestion_list)
        return random.choice(data["MoodResponses"][sentiment]).format(city=city)

    # city sentiment based replies
    if tag == "city_sentiment":
        city = captured["city"].title()
        mood_txt = captured["mood"]
        sentiment = interpret_sentiment(mood_txt)
        
        memory[f"sentiment_{city}"] = sentiment
        templates = data["CitySentimentResponses"].get(sentiment)

        if not templates:
            return f"Thanks for telling me how you feel about {city}."

        return random.choice(templates).format(city=city)

    # fact responses
    if tag == "fact_city":
        city = captured.get("city", "").title()
    
        # Determine keyword from user_text
        user_lower = user_text.lower()
        keyword = None
        if "language" in user_lower or "speak" in user_lower:
            keyword = "speak"
        elif "currency" in user_lower or "use" in user_lower:
            keyword = "yen"  # or "lira"/"euro" based on city
        elif "population" in user_lower:
            keyword = "population"
    
        fact = fact_query(city, data["facts"], keyword)
    
        if fact:
            prefix = random.choice(entry["responses"])
            prefix = prefix.format(city=city)
            return f"{prefix} {fact}"

    if tag == "fact_object":
        obj = captured.get("object", "").lower()
    
        # Lookup for general objects like currency
        fact = None
        if obj == "currency":
            fact = fact_query("Tokyo", data["facts"], keyword="yen")  # fallback
    
        prefix = random.choice(entry["responses"]).format(object=obj)
        return prefix + (" " + fact if fact else "")


    # memory recall
    if tag == "recall_city":
        # If city explicitly asked
        if "city" in captured:
            city = captured["city"].title()
            key = f"sentiment_{city}"
    
            if key in memory:
                sentiment = memory[key]
                if sentiment == "positive":
                    return random.choice(data["MemoryRecall"]["positive"]).format(city=city)
                elif sentiment == "negative":
                    alt = random.choice(data["Suggestions"]["alternatives"])
                    return random.choice(data["MemoryRecall"]["negative"]).format(city=city, alt=alt)
    
            return f"I'm not sure you told me how you feel about {city}."
    
        # If asking "what city did I say I like/hate"
        target = captured.get("mood")
    
        pos_words = ["love", "like", "enjoy"]
        neg_words = ["hate", "dislike"]
    
        for k in memory:
            if k.startswith("sentiment_"):
                city = k.replace("sentiment_", "")
                sentiment = memory[k]
                if sentiment == "positive" and target in pos_words:
                    return random.choice(data["MemoryRecall"]["positive"]).format(city=city)
                if sentiment == "negative" and target in neg_words:
                    alt = random.choice(data["Suggestions"]["alternatives"])
                    return random.choice(data["MemoryRecall"]["negative"]).format(city=city, alt=alt)
    
        return "I don't think you told me that yet."
    
    # use variables in template
    template = random.choice(entry["responses"])
    context = {**memory, **captured}

    try:
        resp = template.format(**context)
    except KeyError:
        # remove any unused placeholders
        resp = re.sub(r"{\w+}", "", template)

    resp = re.sub(r"\s{2,}", " ", resp).strip()
    return resp

def respond(text, data):

    # direct QA
    ans = data["qa"].get(text.lower())
    if ans:
        return ans

    # regex intent matching FIRST
    entry, captured = match_input(text, data["patterns"])
    if entry:
        return generate_response(entry, captured, data, text)

    # NO direct fact_query here anymore
    # now fact_query only runs if an intent tag tells it to

    # fallback reply
    return random.choice(data["fallback"])


def chatbot():

    current_dir = os.path.dirname(os.path.abspath(__file__))

    intents_path = os.path.join(current_dir, "..", "data", "intents.json")
    facts_path = os.path.join(current_dir, "..", "data", "facts.json")

    intents = load_json(intents_path)
    facts = load_json(facts_path)

    data = {
        "patterns": build_patterns(intents),
        "qa": intents["QA"],
        "MoodResponses": intents["MoodResponses"],
        "CitySentimentResponses": intents["CitySentimentResponses"],
        "MemoryRecall": intents["MemoryRecall"],
        "Suggestions": intents["Suggestions"],
        "fallback": intents["Fallback"],
        "facts": facts["Facts"]
    }

    print("TRAVEL BOT: Hello! I'm your travel assistant.")

    while True:
        text = input("You: ")

        if text.lower() == "quit":
            print("TRAVEL BOT: Goodbye!")
            break

        print("TRAVEL BOT:", respond(text, data))

if __name__ == "__main__":
    chatbot()