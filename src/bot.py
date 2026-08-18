import json
import re
import random
from memory import MemoryManager
from nlp import NLPProcessor

class TravelBot:
    def __init__(self, intents_path, facts_path):
        self.memory = MemoryManager()
        self.nlp = NLPProcessor()
        
        intents = self.load_json(intents_path)
        facts = self.load_json(facts_path)
        
        self.data = {
            "patterns": self.build_patterns(intents),
            "qa": intents["QA"],
            "MoodResponses": intents["MoodResponses"],
            "CitySentimentResponses": intents["CitySentimentResponses"],
            "MemoryRecall": intents["MemoryRecall"],
            "Suggestions": intents["Suggestions"],
            "fallback": intents["Fallback"],
            "facts": facts["Facts"]
        }

        self.handlers = {
        "feeling": self._handle_feeling,
        "city_sentiment": self._handle_city_sentiment,
        "fact_city": self._handle_fact_city,
        "fact_object": self._handle_fact_object,
        "recall_city": self._handle_recall_city
    }

    @staticmethod
    def load_json(file):
        with open(file, "r") as f:
            return json.load(f)

    @staticmethod
    def build_patterns(data):
        patterns = []
        for tag in data["Tags"]:
            for p in tag["patterns"]:
                patterns.append({
                    "tag": tag["tag"],
                    "pattern": re.compile(p, re.IGNORECASE),
                    "responses": tag["responses"]
                })
        return patterns

    def match_input(self, text):
        for entry in self.data["patterns"]:
            m = entry["pattern"].search(text)
            if m:
                return entry, m.groupdict()
        return None, {}

    def fact_query(self, city, keyword=None):
        if not city:
            return None
        city = city.lower().strip()
        ranked = []
        for f in self.data["facts"]:
            lf = f.lower()
            s = 0
            if city in lf:
                s += 5
            if keyword and keyword in lf:
                s += 10
            ranked.append((s, f))
        
        ranked.sort(reverse=True)
        return ranked[0][1] if ranked else None

    def generate_response(self, entry, captured, user_text):
        self.memory.update(captured)
        tag = entry["tag"]
        
        #get the function for tag or use a default template
        handler = self.handlers.get(tag, self._handle_default)
        return handler(entry, captured, user_text)

    def _handle_default(self, entry, captured, user_text):
        """The fallback handler for intents that just need string formatting."""
        template = random.choice(entry["responses"])
        context = {**self.memory.get_all(), **captured}
        
        try:
            resp = template.format(**context)
        except KeyError:
            resp = re.sub(r"{\w+}", "", template)
            
        return re.sub(r"\s{2,}", " ", resp).strip()

    def _handle_feeling(self, entry, captured, user_text):
        mood = captured.get("mood", "")
        sentiment = self.nlp.interpret_sentiment(mood)
        suggestion_list = self.data["Suggestions"][sentiment]
        city = random.choice(suggestion_list)
        return random.choice(self.data["MoodResponses"][sentiment]).format(city=city)

    def _handle_city_sentiment(self, entry, captured, user_text):
        city = captured["city"].title()
        mood_txt = captured["mood"]
        sentiment = self.nlp.interpret_sentiment(mood_txt)
        
        #set the sentiment key in memory here
        self.memory.update({f"sentiment_{city}": sentiment})
        
        templates = self.data["CitySentimentResponses"].get(sentiment)
        if not templates:
            return f"Thanks for telling me how you feel about {city}."
        
        return random.choice(templates).format(city=city)

    def _handle_fact_city(self, entry, captured, user_text):
        city = captured.get("city", "").title()
        user_lower = user_text.lower()
        keyword = None
        
        if "language" in user_lower or "speak" in user_lower:
            keyword = "speak"
        elif "currency" in user_lower or "use" in user_lower:
            keyword = "yen"
        elif "population" in user_lower:
            keyword = "population"
        
        fact = self.fact_query(city, keyword)
        if fact:
            prefix = random.choice(entry["responses"]).format(city=city)
            return f"{prefix} {fact}"
        
        return random.choice(self.data["fallback"])

    def _handle_fact_object(self, entry, captured, user_text):
        obj = captured.get("object", "").lower()
        fact = None
        
        if obj == "currency":
            fact = self.fact_query("Tokyo", keyword="yen")
            
        prefix = random.choice(entry["responses"]).format(object=obj)
        return prefix + (" " + fact if fact else "")

    def _handle_recall_city(self, entry, captured, user_text):
        # If the user asks about a specific city
        if "city" in captured:
            city = captured["city"].title()
            key = f"sentiment_{city}"
            sentiment = self.memory.get(key)
            
            if sentiment == "positive":
                return random.choice(self.data["MemoryRecall"]["positive"]).format(city=city)
            elif sentiment == "negative":
                alt = random.choice(self.data["Suggestions"]["alternatives"])
                return random.choice(self.data["MemoryRecall"]["negative"]).format(city=city, alt=alt)
            
            return f"I'm not sure you told me how you feel about {city}."
        
        # If the user asks a general question like "what city did I say I like?"
        target = captured.get("mood")
        pos_words = ["love", "like", "enjoy"]
        neg_words = ["hate", "dislike"]
        
        for k, sentiment in self.memory.get_all().items():
            if k.startswith("sentiment_"):
                city = k.replace("sentiment_", "")
                
                if sentiment == "positive" and target in pos_words:
                    return random.choice(self.data["MemoryRecall"]["positive"]).format(city=city)
                if sentiment == "negative" and target in neg_words:
                    alt = random.choice(self.data["Suggestions"]["alternatives"])
                    return random.choice(self.data["MemoryRecall"]["negative"]).format(city=city, alt=alt)
                    
        return "I don't think you told me that yet."

    def respond(self, text):
        ans = self.data["qa"].get(text.lower())
        if ans:
            return ans

        entry, captured = self.match_input(text)
        if entry:
            return self.generate_response(entry, captured, text)

        return random.choice(self.data["fallback"])