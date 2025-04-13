import tkinter as tk
from ui.login_view import LoginView
from ui.create_user_view import CreateUserView
from ui.pef_view import PefListView  # Import the PefListView for PEF calculation
from services.pef_service import pef_service


class UI:
    """Main UI controller that handles switching between different views."""

    def __init__(self, root):
        # Initializes the UI with the root window and sets the initial view to None
        self._root = root
        self._current_view = None

        self._root.geometry("1600x900")  # Set initial window size
        self._root.resizable(False, False)  # Disable resizing

        # Ensure grid layout is properly set up for root window
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

    def handle_login(self):
        # Placeholder function for handling login (this is where the user successfully logs in)
        print("Login handler called")

        # Once the user logs in successfully, show the PEF calculation view
        self._show_pef_view()

    def handle_logout(self):
        # Placeholder function to handle logging out
        print("Logout handler called")

        # After logging out, show the login view again
        self._show_login_view()

    def handle_create_user(self):
        # Placeholder function for handling user creation (this is where user creation logic goes)
        print("User creation handler called")
        # After user creation, you can switch to the login view or a success message
        self._show_login_view()

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
            self._show_create_user_view,
        )

        # Use grid() instead of pack
        self._current_view.grid(row=0, column=0, sticky="nsew")

    def _show_create_user_view(self):
        # Switches to the create user view, hiding the current view first
        self._hide_current_view()

        # Create an instance of CreateUserView with both handlers
        self._current_view = CreateUserView(
            self._root,
            self.handle_create_user,  # Pass the handle_create_user function as the first handler
            self._show_login_view  # Pass the handle_show_login_view function as the second handler
        )

        # Use grid() instead of pack
        self._current_view.grid(row=0, column=0, sticky="nsew")

    def _show_pef_view(self):
        # Switches to the PEF calculation view after login
        self._hide_current_view()

        user = pef_service.get_current_user()

        # Create an instance of PefListView for PEF calculation
        self._current_view = PefListView(
            self._root, self.handle_logout, pef_service, user
        )
        # Refresh the reference PEF value after login
        self._current_view._update_reference_pef_ui()

        # Use grid() to add PefListView to the root window
        self._current_view._frame.grid(row=0, column=0, sticky="nsew")

    def run(self):
        # Runs the application and initializes the Tkinter root window
        root = tk.Tk()  # Create the Tkinter root window
        root.geometry("1200x700")  # Set the window size to 1200x700
        self.start()  # Start the UI and show the login view
        root.mainloop()  # Start Tkinter's event loop to keep the window open