from tkinter import ttk, StringVar, constants
import sqlite3
from tkinter import messagebox
from services.pef_service import pef_service, InvalidCredentialsError


class LoginView:

    def __init__(self, root, handle_login, handle_show_create_user_view):

        self._root = root
        self._handle_login = handle_login
        self._handle_show_create_user_view = handle_show_create_user_view
        self._frame = None
        self._username_entry = None
        self._password_entry = None
        self._error_variable = None
        self._error_label = None

        self._initialize()

    def grid(self, **kwargs):
        # Grid the frame (container) where all widgets are added
        self._frame.grid(**kwargs)

    def destroy(self):
        self._frame.destroy()

    def _login_handler(self):
        username = self._username_entry.get()
        password = self._password_entry.get()

        try:
            pef_service.login(username, password)
            self._handle_login()
            user = pef_service.login(username, password)
            pef_service._user = user
        except InvalidCredentialsError:
            self._show_error("Invalid username or password")

        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                messagebox.showerror(
                    "Tietokantavirhe",
                    "Tietokantaa ei ole alustettu. Suorita 'poetry run invoke build' ennen sovelluksen käynnistämistä."
                )
            else:
                raise

    def _show_error(self, message):
        self._error_variable.set(message)
        self._error_label.grid()

    def _hide_error(self):
        self._error_label.grid_remove()

    def _initialize_username_field(self):
        username_label = ttk.Label(master=self._frame, text="Username")

        self._username_entry = ttk.Entry(master=self._frame, width=30)

        username_label.grid(padx=5, pady=5, sticky=constants.W)
        self._username_entry.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize_password_field(self):
        password_label = ttk.Label(master=self._frame, text="Password")

        # Set show="*" to mask the password
        self._password_entry = ttk.Entry(
            master=self._frame, show="*", width=30)

        password_label.grid(padx=5, pady=5, sticky=constants.W)
        self._password_entry.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize(self):
        self._frame = ttk.Frame(master=self._root)

        self._error_variable = StringVar(self._frame)

        self._error_label = ttk.Label(
            master=self._frame,
            textvariable=self._error_variable,
            foreground="red"
        )

        self._error_label.grid(padx=5, pady=5)

        self._initialize_username_field()
        self._initialize_password_field()

        login_button = ttk.Button(
            master=self._frame,
            text="Login",
            command=self._login_handler,
            width=20
        )

        create_user_button = ttk.Button(
            master=self._frame,
            text="Create user",
            command=self._handle_show_create_user_view,
            width=20
        )

        self._frame.grid_columnconfigure(0, weight=1, minsize=400)

        login_button.grid(padx=5, pady=5, sticky=constants.W)
        create_user_button.grid(padx=5, pady=5, sticky=constants.W)

        self._hide_error()
