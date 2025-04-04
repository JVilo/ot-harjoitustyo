from tkinter import ttk, StringVar, constants
from services.pef_service import pef_service, UsernameExistsError, PasswordsDoNotMatch


class CreateUserView:
    """View responsible for user registration"""

    def __init__(self, root, handle_create_user, handle_show_login_view):
        # Initializes the view with the given root, create user handler, and login view handler
        self._root = root
        self._handle_create_user = handle_create_user
        self._handle_show_login_view = handle_show_login_view
        self._frame = None
        self._username_entry = None
        self._password_entry = None
        self._password2_entry = None
        self._error_variable = None
        self._error_label = None

        self._initialize()

    def pack(self):
        # Packs the frame to make it visible in the window
        self._frame.pack(fill=constants.X)

    def destroy(self):
        # Destroys the frame, removing it from the window
        self._frame.destroy()

    def _create_user_handler(self):
        # Handles user creation logic when the "Create" button is clicked
        username = self._username_entry.get()  # Get the entered username
        password = self._password_entry.get()  # Get the entered password
        password2 = self._password2_entry.get()  # Get the entered password confirmation

        # Checks if username or password is empty, shows an error if so
        if len(username) == 0 or len(password) == 0:
            self._show_error("Username and password are required")
            return

        if password != password2:
            # If the passwords do not match, show an error message
            self._show_error("Passwords do not match")
            return

        try:
            # Attempts to create a new user via the pef_service
            pef_service.create_user(username, password, password2)  # Pass only the username and password
            self._handle_create_user()  # Calls the handler after successful user creation

        except UsernameExistsError:
            # If the username already exists, show an error message
            self._show_error(f"Username {username} already exists")

        except PasswordsDoNotMatch:
            # If the passwords do not match (this is more of a safeguard in case the validation failed before)
            self._show_error("Passwords do not match")

    def _show_error(self, message):
        # Displays an error message in the error label
        self._error_variable.set(message)
        self._error_label.grid()

    def _hide_error(self):
        # Hides the error message by removing the error label from the grid
        self._error_label.grid_remove()

    def _initialize_username_field(self):
        # Initializes the username input field with a label and entry widget
        username_label = ttk.Label(master=self._frame, text="Username")
        self._username_entry = ttk.Entry(master=self._frame, width=30)

        # Places the username label and entry in the grid
        username_label.grid(padx=5, pady=5, sticky=constants.W)
        self._username_entry.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize_password_field(self):
        # Initializes the password input field with a label and entry widget
        password_label = ttk.Label(master=self._frame, text="Password")
        self._password_entry = ttk.Entry(master=self._frame, show="*", width=30)  # Mask the password input

        # Places the password label and entry in the grid
        password_label.grid(padx=5, pady=5, sticky=constants.W)
        self._password_entry.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize_password2_field(self):
        # Initializes the "Password again" input field with a label and entry widget
        password_label = ttk.Label(master=self._frame, text="Password again")
        self._password2_entry = ttk.Entry(master=self._frame, show="*", width=30)  # Mask the password input

        # Places the "Password again" label and entry in the grid
        password_label.grid(padx=5, pady=5, sticky=constants.W)
        self._password2_entry.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize(self):
        # Initializes the frame and its components
        self._frame = ttk.Frame(master=self._root)

        self._error_variable = StringVar(self._frame)  # Variable to hold error messages

        self._error_label = ttk.Label(
            master=self._frame,
            textvariable=self._error_variable,
            foreground="red"  # Set the error text color to red
        )

        self._error_label.grid(padx=5, pady=5)  # Places the error label in the grid

        # Initializes the username, password, and password confirmation fields
        self._initialize_username_field()
        self._initialize_password_field()
        self._initialize_password2_field()

        # Create the "Create" button that triggers user creation
        create_user_button = ttk.Button(
            master=self._frame,
            text="Create",
            command=self._create_user_handler,  # Calls the function that handles user creation
            width=20
        )

        # Create the "Login" button to switch to the login view
        login_button = ttk.Button(
            master=self._frame,
            text="Login",
            command=self._handle_show_login_view,  # Calls the function to show the login view
            width=20
        )

        self._frame.grid_columnconfigure(0, weight=1, minsize=400)  # Configures the grid to resize properly

        # Places the buttons in the grid
        self._frame.grid_columnconfigure(0, weight=1, minsize=400)  # This will make the buttons expand
        create_user_button.grid(padx=5, pady=5, sticky=constants.W)
        login_button.grid(padx=5, pady=5, sticky=constants.W)
        # Hides the error message label initially
        self._hide_error()