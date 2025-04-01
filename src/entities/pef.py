import uuid

class Pef:
    def __init__(self, value, user=None, pef_id=None):

        self.pef_id = pef_id or str(uuid.uuid4())  # Generate a new UUID if not provided
        self.value = value  # PEF value
        self.user = user  # User associated with this PEF measurement