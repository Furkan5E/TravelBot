import pytest
from src.nlp import NLPProcessor

@pytest.fixture
def nlp():
    """This fixture creates a single NLPProcessor instance for all tests to use."""
    return NLPProcessor()

def test_interpret_sentiment_positive(nlp):
    result = nlp.interpret_sentiment("I absolutely love Tokyo, it is amazing!")
    assert result == "positive"

def test_interpret_sentiment_negative(nlp):
    result = nlp.interpret_sentiment("I hate being stressed and delayed.")
    assert result == "negative"

def test_interpret_sentiment_neutral(nlp):
    result = nlp.interpret_sentiment("The flight leaves at 8 AM.")
    assert result == "neutral"

def test_extract_svo(nlp):
    #testing the Subject-Verb-Object extraction
    subject, verb, obj = nlp.extract_svo("John visited London")
    
    assert subject == "John"
    assert verb == "visited"
    assert obj == "London"