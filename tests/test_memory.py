import pytest
from src.memory import MemoryManager

@pytest.fixture
def memory():
    return MemoryManager()

def test_update_and_get(memory):
    #testing to see if stores data and strips trailing spaces
    memory.update({"name": "Bob", "city": "London   "})
    
    assert memory.get("name") == "Bob"
    assert memory.get("city") == "London"

def test_get_default(memory):
    #testing that asking for a non existent key returns none
    assert memory.get("unknown_key") is None

def test_get_all(memory):
    memory.update({"days": 7})
    assert memory.get_all() == {"days": 7}