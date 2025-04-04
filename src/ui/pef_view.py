from tkinter import ttk, StringVar, constants
from services.pef_service import pef_service

class PefListView:
    def __init__(self, root, handle_logout, pef_service, logged_in_user=None, user = None):
        self._root = root
        self._frame = None
        self._age_var = None
        self._height_var = None
        self._gender_var = None
        self._error_variable = None
        self._error_label = None
        self._reference_pef_var = None
        self._calculate_button = None
        self._logged_in_user = logged_in_user  # Store the logged-in user
        self._handle_logout = handle_logout  # Logout handler to call when the button is clicked

        self._pef_reference_button = None  # Button to trigger PEF reference calculation
        self.fields_initialized = False  # Flag to track if fields are initialized
        self._pef_service = pef_service
        self._user = user

        self._initialize()

    def pack(self):
        self._frame.pack(fill=constants.X)

    def destroy(self):
        self._frame.destroy()

    def _initialize_greeting_label(self):
        """Initialize the greeting label to show the user's name."""
        self._greeting_var = StringVar(self._frame)

        # Check if logged_in_user exists, and if it does, use the user's name for the greeting
        if self._logged_in_user:
            greeting_text = f"Hi, {self._logged_in_user.name}!"  # You can use any attribute of the logged-in user
        else:
            greeting_text = "Hi, Guest!"
        
        # Set the greeting text
        self._greeting_var.set(greeting_text)

        # Create a label to display the greeting
        greeting_label = ttk.Label(self._frame, textvariable=self._greeting_var)
        greeting_label.grid(padx=5, pady=5)


    def _initialize_logout_button(self):
        """Initialize the logout button and position it in the top-right corner."""
        logout_button = ttk.Button(self._frame, text="Logout", command=self._logout)
        logout_button.grid(row=0, column=1, padx=10, pady=10, sticky="ne")  # Place it in the top-right corner


    def _initialize_reference_label(self):
        """Initialize the reference label to display the reference PEF value."""
        self._reference_pef_var = StringVar(self._frame)  # Initialize it here
        reference_pef_label = ttk.Label(
            master=self._frame,
            textvariable=self._reference_pef_var
        )
        reference_pef_label.grid(padx=5, pady=5)

    def _update_reference_pef_ui(self):
        """Fetches and displays the stored reference PEF value."""
        reference_pef = self._pef_service.get_reference_pef_for_user() 
        
        if isinstance(reference_pef, list):  # Check if reference_pef is a list
            if reference_pef:
                reference_pef = reference_pef[0]  # Use the first element if it's a list
            else:
                reference_pef = None  # Handle empty list

        if reference_pef is not None:
            self._reference_pef_var.set(f"PEF viitearvosi: {reference_pef:.2f} L/min")
        else:
            self._reference_pef_var.set("No reference PEF value found.")

    def display_user_pef(self):
        """Fetch the logged-in user's PEF and display the reference PEF value."""
        user_pef = pef_service.get_user_pef(self._logged_in_user.id)
        if user_pef:
            # Display the reference PEF value for the logged-in user
            self.update_reference_pef(user_pef)
        else:
            self.update_reference_pef("PEF data not available")

    def _logout(self):
        """Handle logout logic and return to the login view."""
        self._handle_logout()  # This will call the handle_logout method from the UI

    def _calculate_pef_handler(self):
        try:
            # Get user inputs
            age = int(self._age_var.get())  # Get the age from the dropdown
            height = float(self._height_var.get())  # Get the height from the text entry
            gender = self._gender_var.get()  # Get the gender value (male or female)
            
            # Call the method to calculate the reference PEF value
            reference_pef = pef_service.count_reference_pef(height, age, gender)

            # Update the displayed reference PEF value
            self._reference_pef_var.set(f"PEF viitearvosi: {reference_pef:.2f} L/min")
            self._error_label.grid_remove()  # Hide error if calculation was successful

            # Hide the input fields and their labels after calculation
            self._age_label.grid_remove()
            self._age_dropdown.grid_remove()
            self._height_label.grid_remove()
            self._height_entry.grid_remove()
            self._gender_label.grid_remove()
            self._male_checkbox.grid_remove()
            self._female_checkbox.grid_remove()
            self._calculate_button.grid_remove()

            # Show the recalculate button and re-enable it
            self._initialize_pef_reference_button()

        except ValueError:
            # If the user input is not valid, show an error message
            self._show_error("Ole hyvä ja täytä pituus ja ikä!")

    def _recalculate_pef_handler(self):
        """Handler for recalculating the reference PEF."""
        # Make sure the fields are initialized (in case they were removed during the first calculation)
        self._initialize_fields()

        # Show the input fields again for recalculation
        self._age_label.grid(padx=5, pady=5, sticky=constants.W)
        self._age_dropdown.grid(padx=5, pady=5, sticky=constants.EW)
        self._height_label.grid(padx=5, pady=5, sticky=constants.W)
        self._height_entry.grid(padx=5, pady=5, sticky=constants.EW)
        self._gender_label.grid(padx=5, pady=5, sticky=constants.W)
        self._male_checkbox.grid(padx=5, pady=5, sticky=constants.W)
        self._female_checkbox.grid(padx=5, pady=5, sticky=constants.W)

        # Reset reference PEF value
        self._reference_pef_var.set("")

        # Hide the recalculate button
        self._pef_reference_button.grid_remove()  # Hide the button again

        # Re-enable the "Laske" button and check if it's enabled
        self._calculate_button.config(state=constants.NORMAL)

        # Reset the fields for the next calculation
        self.fields_initialized = False  # Reset the flag for new calculation

    def _show_error(self, message):
        self._error_variable.set(message)
        self._error_label.grid()

    def _hide_error(self):
        self._error_label.grid_remove()

    def _initialize_age_dropdown(self):
        # Ensure age dropdown is initialized
        self._age_label = ttk.Label(master=self._frame, text="Ikä (vuosina)")  # Label for age
        self._age_var = StringVar(self._frame)
        age_options = [str(i) for i in range(5, 100)]  # Age dropdown from 5 to 99
        self._age_var.set(age_options[0])  # Default age

        self._age_dropdown = ttk.Combobox(master=self._frame, textvariable=self._age_var, values=age_options, state="readonly")
        self._age_label.grid(padx=5, pady=5, sticky=constants.W)
        self._age_dropdown.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_height_field(self):
        self._height_label = ttk.Label(master=self._frame, text="Pituus (cm)")  # Label for height
        self._height_var = StringVar(self._frame)

        self._height_entry = ttk.Entry(master=self._frame, textvariable=self._height_var)
        self._height_label.grid(padx=5, pady=5, sticky=constants.W)
        self._height_entry.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_gender_checkboxes(self):
        self._gender_label = ttk.Label(master=self._frame, text="Sukupuoli")  # Label for gender
        self._gender_var = StringVar(self._frame)
        self._gender_var.set("")  # Default to empty value

        self._male_checkbox = ttk.Radiobutton(master=self._frame, text="Mies", variable=self._gender_var, value="male")
        self._female_checkbox = ttk.Radiobutton(master=self._frame, text="Nainen", variable=self._gender_var, value="female")
        
        self._gender_label.grid(padx=5, pady=5, sticky=constants.W)
        self._male_checkbox.grid(padx=5, pady=5, sticky=constants.W)
        self._female_checkbox.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize_pef_reference_button(self):
        """Initializes the button to calculate PEF reference."""
        self._pef_reference_button = ttk.Button(
            master=self._frame,
            text="Laske PEF-viitearvo",  # Button to start calculation
            command=self._recalculate_pef_handler  # Correct command for recalculation
        )
        self._pef_reference_button.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_fields(self):
        """This method initializes the input fields (age, height, gender)."""
        # Check if fields have already been initialized
        if self.fields_initialized:
            return  # If fields are already initialized, do nothing

        self._initialize_age_dropdown()  # This will create the _age_dropdown widget
        self._initialize_height_field()
        self._initialize_gender_checkboxes()

        # Show the input fields for calculation
        self._age_label.grid(padx=5, pady=5, sticky=constants.W)
        self._age_dropdown.grid(padx=5, pady=5, sticky=constants.EW)
        self._height_label.grid(padx=5, pady=5, sticky=constants.W)
        self._height_entry.grid(padx=5, pady=5, sticky=constants.EW)
        self._gender_label.grid(padx=5, pady=5, sticky=constants.W)
        self._male_checkbox.grid(padx=5, pady=5, sticky=constants.W)
        self._female_checkbox.grid(padx=5, pady=5, sticky=constants.W)

        # Initialize the calculate button (after fields are initialized)
        self._initialize_calculate_button()

        # Enable the "Laske" button only after all fields are filled
        self._age_var.trace("w", self._enable_finish_button)
        self._height_var.trace("w", self._enable_finish_button)
        self._gender_var.trace("w", self._enable_finish_button)

        # Disable the "Laske PEF-viitearvo" button after it has been clicked
        self._pef_reference_button.config(state=constants.DISABLED)

        # Mark the fields as initialized
        self.fields_initialized = True

    def _initialize_calculate_button(self):
        """Initializes the 'Laske' button."""
        self._calculate_button = ttk.Button(
            master=self._frame,
            text="Laske",
            state=constants.DISABLED,  # Initially disabled
            command=self._calculate_pef_handler  # Button action to calculate PEF
        )
        self._calculate_button.grid(padx=5, pady=5, sticky=constants.EW)

    def _enable_finish_button(self, *args):
        """Enables the 'Laske' button when all fields are filled."""
        if self._age_var.get() and self._height_var.get() and self._gender_var.get():
            self._calculate_button.config(state=constants.NORMAL)  # Enable the button
        else:
            self._calculate_button.config(state=constants.DISABLED)  # Keep it disabled if fields are empty

    def _initialize(self):
        self._frame = ttk.Frame(master=self._root)

        self._error_variable = StringVar(self._frame)  # Variable for error messages
        self._error_label = ttk.Label(
            master=self._frame,
            textvariable=self._error_variable,
            foreground="red"  # Error text color
        )
        self._error_label.grid(padx=5, pady=5)

        self._initialize_reference_label()  # Initialize the reference label
        self._update_reference_pef_ui()  # Now we can safely call this method

        # Initialize buttons and handlers
        self._initialize_pef_reference_button()  # Initialize the "Laske PEF-viitearvo" button
        self._initialize_logout_button()  # Initialize the logout button