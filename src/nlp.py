import nltk
from nltk import pos_tag, word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("punkt", quiet=True)
nltk.download("averaged_perceptron_tagger_eng", quiet=True)

class NLPProcessor:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()

    def interpret_sentiment(self, text):
        score = self.sia.polarity_scores(text)["compound"]
        if score > 0.3:
            return "positive"
        if score < -0.3:
            return "negative"
        return "neutral"

    def extract_svo(self, text):
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)

        subject = verb = obj = None
        
        for word, pos in tagged:
            if pos in ("NNP", "NNPS"):
                return word, None, None

        for word, pos in tagged:
            if pos.startswith("NN"):
                subject = word

        for word, pos in tagged:
            if pos.startswith("VB"):
                verb = word
                break

        for word, pos in tagged:
            if verb and (pos.startswith("NN") or pos.startswith("JJ")):
                obj = word

        return subject, verb, obj