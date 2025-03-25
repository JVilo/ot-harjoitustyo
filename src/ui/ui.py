import tkinter as tk
from ui.login_view import LoginView
from ui.create_user_view import CreateUserView

class UI:
    """Main UI controller that handles switching between different views."""

    def __init__(self, root):
        # Initializes the UI with the root window and sets the initial view to None
        self._root = root
        self._current_view = None

    def handle_login(self):
        # Placeholder function for handling login (can be filled in later)
        print("Login handler called")

    def handle_create_user(self):
        # Placeholder function for handling user creation (can be filled in later)
        print("User creation handler called")
        # Add logic for what should happen after user creation, like navigating to a different view

    def start(self):
        # Starts the UI by showing the login view
        self._show_login_view()

    def _hide_current_view(self):
        # Hides the current view if there is one
        if self._current_view:
            self._current_view.destroy()  # Destroys the current view to remove it from the window

        self._current_view = None  # Resets the current view to None

    def _show_login_view(self):
        # Switches to the login view, hiding the current view first
        self._hide_current_view()

        # Create an instance of LoginView with both handlers
        self._current_view = LoginView(
            self._root,
            self.handle_login,  # Pass the handle_login function as the first handler
            self._show_create_user_view  # Pass the _show_create_user_view function as the second handler
        )

        self._current_view.pack()  # Packs the login view to display it

    def _show_create_user_view(self):
        # Switches to the create user view, hiding the current view first
        self._hide_current_view()

        # Create an instance of CreateUserView with both handlers
        self._current_view = CreateUserView(
            self._root,
            self.handle_create_user,  # Pass the handle_create_user function as the first handler
            self._show_login_view  # Pass the handle_show_login_view function as the second handler
        )

        self._current_view.pack()  # Packs the create user view to display it
    
    def run(self):
        # Runs the application and initializes the Tkinter root window
        root = tk.Tk()  # Create the Tkinter root window
        self.start()  # Start the UI and show the login view
        root.mainloop()  # Start Tkinter's event loop to keep the window open