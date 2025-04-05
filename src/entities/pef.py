import uuid


class Pef:
    """Class representing a PEF reference."""

    def __init__(self, value, user=None, pef_id=None):
        """Constructor for the Pef class.

        Args:
            value (float): The PEF reference value.
            user (User): The user who owns this reference.
            pef_id (str): The ID for the reference, defaults to a generated UUID.
        """
        self.value = value
        self.user = user
        self.pef_id = pef_id or str(uuid.uuid4())
