class User:
    """Represents a user with username and password.

    Attributes:
        username: The username of the user.
        password: The password of the user.
    """

    def __init__(self, username, password):
        """Initializes a new User instance.

        Args:
            username: The user's username.
            password: The user's password.
        """
        self.username = username
        self.password = password

    def __str__(self):
        """Returns the string representation of the user.

        Returns:
            The username as string.
        """
        return self.username
