from tkinter import ttk, StringVar, constants
from services.pef_service import pef_service

class PefListView:
    def __init__(self, root):
        self._root = root
        self._frame = None
        self._age_var = None
        self._height_var = None
        self._gender_var = None
        self._error_variable = None
        self._error_label = None
        self._reference_pef_var = None
        self._calculate_button = None

        self._initialize()

    def pack(self):
        self._frame.pack(fill=constants.X)

    def destroy(self):
        self._frame.destroy()

    def _calculate_pef_handler(self):
        try:
            age = int(self._age_var.get())  # Get the age from the dropdown
            height = float(self._height_var.get())  # Get the height from the text entry
            gender = self._gender_var.get()  # Get the gender value (male or female)
            
            # Call the method to calculate the reference PEF value
            reference_pef = pef_service.count_reference_pef(height, age, gender)
            
            # Update the displayed reference PEF value
            self._reference_pef_var.set(f"PEF viitearvosi: {reference_pef:.2f} L/min")
            self._error_label.grid_remove()  # Hide error if calculation was successful

        except ValueError:
            # If the user input is not valid, show an error message
            self._show_error("Ole hyvä ja täytä pituus ja ikä!")

    def _show_error(self, message):
        self._error_variable.set(message)
        self._error_label.grid()

    def _hide_error(self):
        self._error_label.grid_remove()

    def _initialize_age_dropdown(self):
        age_label = ttk.Label(master=self._frame, text="Ikä (vuosina)")
        self._age_var = StringVar(self._frame)
        age_options = [str(i) for i in range(5, 100)]  # Age dropdown from 5 to 99
        self._age_var.set(age_options[0])  # Default age

        age_dropdown = ttk.Combobox(master=self._frame, textvariable=self._age_var, values=age_options, state="readonly")
        age_label.grid(padx=5, pady=5, sticky=constants.W)
        age_dropdown.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_height_field(self):
        height_label = ttk.Label(master=self._frame, text="Pituus (cm)")
        self._height_var = StringVar(self._frame)

        height_entry = ttk.Entry(master=self._frame, textvariable=self._height_var)
        height_label.grid(padx=5, pady=5, sticky=constants.W)
        height_entry.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_gender_checkboxes(self):
        gender_label = ttk.Label(master=self._frame, text="Sukupuoli")
        self._gender_var = StringVar(self._frame)
        self._gender_var.set("")  # Default to empty value

        male_checkbox = ttk.Radiobutton(master=self._frame, text="Mies", variable=self._gender_var, value="male")
        female_checkbox = ttk.Radiobutton(master=self._frame, text="Nainen", variable=self._gender_var, value="female")
        
        gender_label.grid(padx=5, pady=5, sticky=constants.W)
        male_checkbox.grid(padx=5, pady=5, sticky=constants.W)
        female_checkbox.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize_calculate_button(self):
        """Initializes the 'Laske' button."""
        self._calculate_button = ttk.Button(
            master=self._frame,
            text="Laske",
            state=constants.DISABLED,  # Initially disabled
            command=self._calculate_pef_handler
        )
        self._calculate_button.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize(self):
        self._frame = ttk.Frame(master=self._root)

        self._error_variable = StringVar(self._frame)  # Variable for error messages
        self._error_label = ttk.Label(
            master=self._frame,
            textvariable=self._error_variable,
            foreground="red"  # Error text color
        )
        self._error_label.grid(padx=5, pady=5)

        self._reference_pef_var = StringVar(self._frame)  # Variable for reference PEFR value
        reference_pef_label = ttk.Label(
            master=self._frame,
            textvariable=self._reference_pef_var
        )
        reference_pef_label.grid(padx=5, pady=5)

        self._initialize_age_dropdown()
        self._initialize_height_field()
        self._initialize_gender_checkboxes()
        self._initialize_calculate_button()

        # Enable laske button only when all fields are filled
        self._age_var.trace("w", self._enable_finish_button)
        self._height_var.trace("w", self._enable_finish_button)
        self._gender_var.trace("w", self._enable_finish_button)

    def _enable_finish_button(self, *args):
        if self._age_var.get() and self._height_var.get() and self._gender_var.get():
            self._calculate_button.config(state=constants.NORMAL)  # Enable the button
        else:
            self._calculate_button.config(state=constants.DISABLED)  # Keep it disabled if fields are empty