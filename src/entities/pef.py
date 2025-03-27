import uuid

class Pef:
    def __init__(self, value, user=None, pef_id=None):

        self.pef_id = pef_id or str(uuid.uuid4())  # Generate a new UUID if not provided
        self.value = value  # PEFR value
        self.user = user  # User associated with this PEFR measurement