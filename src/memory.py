class MemoryManager:
    def __init__(self):
        self.data = {}

    def update(self, kwargs):
        for key, value in kwargs.items():
            if isinstance(value, str):
                self.data[key] = value.strip()
            else:
                self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def get_all(self):
        return self.data