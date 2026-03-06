from datetime import datetime


class Event:
    def __init__(self, message: str):
        self.message = message
        self.timestamp = datetime.now()
