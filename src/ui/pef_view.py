from tkinter import ttk, StringVar, constants
from tkcalendar import Calendar
from datetime import datetime
from services.pef_service import pef_service


class PefListView:
    def __init__(self, root, handle_logout, pef_service, logged_in_user=None, user=None):
        self._root = root
        self._frame = None
        self._age_var = None
        self._height_var = None
        self._gender_var = None
        self._error_variable = None
        self._error_label = None
        self._morning_before_var = None
        self._morning_after_var = None
        self._evening_before_var = None
        self._evening_after_var = None
        self._calculate_comparison_button = None
        self._comparison_result_var = None
        self._comparison_result_label = None
        self._reference_pef_var = None
        self._calculate_button = None
        self._logged_in_user = logged_in_user  # Store the logged-in user
        # Logout handler to call when the button is clicked
        self._handle_logout = handle_logout

        self._pef_reference_button = None  # Button to trigger PEF reference calculation
        self.fields_initialized = False  # Flag to track if fields are initialized
        self._pef_service = pef_service
        self._user = user
        self._calendar = None
        self._time_of_day_dropdown = None
        self._medication_dropdown = None
        self._pef_value_1_entry = None
        self._pef_value_2_entry = None
        self._pef_value_3_entry = None
        self._toggle_button = None
        self._pef_frame = None

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
            # You can use any attribute of the logged-in user
            greeting_text = f"Hi, {self._logged_in_user.username}!"
        else:
            greeting_text = "Hi, Guest!"

        # Set the greeting text
        self._greeting_var.set(greeting_text)

        # Create a label to display the greeting
        greeting_label = ttk.Label(
            self._frame, textvariable=self._greeting_var)
        greeting_label.grid(padx=5, pady=5)

    def _initialize_logout_button(self):
        """Initialize the logout button and position it in the top-right corner."""
        logout_button = ttk.Button(
            self._frame, text="Logout", command=self._logout)
        # Place it in the top-right corner
        logout_button.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

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
                # Use the first element if it's a list
                reference_pef = reference_pef[-1]
            else:
                reference_pef = None  # Handle empty list

        if reference_pef is not None:
            self._reference_pef_var.set(
                f"PEF viitearvosi: {reference_pef.value:.2f} L/min")
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
            # Get the height from the text entry
            height = float(self._height_var.get())
            gender = self._gender_var.get()  # Get the gender value (male or female)

            # Call the method to calculate the reference PEF value
            reference_pef = pef_service.count_reference_pef(
                height, age, gender)

            # Update the displayed reference PEF value
            self._reference_pef_var.set(
                f"PEF viitearvosi: {reference_pef:.2f} L/min")
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
        self._age_label = ttk.Label(
            master=self._frame, text="Ikä (vuosina)")  # Label for age
        self._age_var = StringVar(self._frame)
        # Age dropdown from 5 to 99
        age_options = [str(i) for i in range(5, 100)]
        self._age_var.set(age_options[0])  # Default age

        self._age_dropdown = ttk.Combobox(
            master=self._frame, textvariable=self._age_var, values=age_options, state="readonly")
        self._age_label.grid(padx=5, pady=5, sticky=constants.W)
        self._age_dropdown.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_height_field(self):
        self._height_label = ttk.Label(
            master=self._frame, text="Pituus (cm)")  # Label for height
        self._height_var = StringVar(self._frame)

        self._height_entry = ttk.Entry(
            master=self._frame, textvariable=self._height_var)
        self._height_label.grid(padx=5, pady=5, sticky=constants.W)
        self._height_entry.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_gender_checkboxes(self):
        self._gender_label = ttk.Label(
            master=self._frame, text="Sukupuoli")  # Label for gender
        self._gender_var = StringVar(self._frame)
        self._gender_var.set("")  # Default to empty value

        self._male_checkbox = ttk.Radiobutton(
            master=self._frame, text="Mies", variable=self._gender_var, value="male")
        self._female_checkbox = ttk.Radiobutton(
            master=self._frame, text="Nainen", variable=self._gender_var, value="female")

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
            self._calculate_button.config(
                state=constants.NORMAL)  # Enable the button
        else:
            # Keep it disabled if fields are empty
            self._calculate_button.config(state=constants.DISABLED)

    def _initialize_comparison_button(self):
        """Initializes the 'Laske vertailu' button to start the comparison."""
        self._calculate_comparison_button = ttk.Button(
            master=self._frame,
            text="Laske vertailu",
            command=self._toggle_comparison_fields
        )
        self._calculate_comparison_button.grid(
            padx=5, pady=5, sticky=constants.EW)

    def _toggle_comparison_fields(self):
        """Shows or hides the fields for morning/evening PEF values and handles calculation."""
        if not self.fields_initialized:
            # Initialize fields for comparison
            self._initialize_comparison_fields()
            self._calculate_comparison_button.config(text="Sulje vertailu")
        else:
            # Hide the comparison fields
            self._hide_comparison_fields()
            self._calculate_comparison_button.config(text="Laske vertailu")

    def _initialize_comparison_fields(self):
        """Initialize the fields for entering morning and evening PEF values."""
        # Initialize PEF input variables
        self._morning_before_var = StringVar(self._frame)
        self._morning_after_var = StringVar(self._frame)
        self._evening_before_var = StringVar(self._frame)
        self._evening_after_var = StringVar(self._frame)

        # Create labels for the input fields
        self._morning_before_label = ttk.Label(
            master=self._frame, text="Aamun PEF ennen lääkettä (L/min)")
        self._morning_after_label = ttk.Label(
            master=self._frame, text="Aamun PEF jälkeen lääkettä (L/min)")
        self._evening_before_label = ttk.Label(
            master=self._frame, text="Illan PEF ennen lääkettä (L/min)")
        self._evening_after_label = ttk.Label(
            master=self._frame, text="Illan PEF jälkeen lääkettä (L/min)")

        # Create entry fields for the PEF values
        self._morning_before_entry = ttk.Entry(
            master=self._frame, textvariable=self._morning_before_var)
        self._morning_after_entry = ttk.Entry(
            master=self._frame, textvariable=self._morning_after_var)
        self._evening_before_entry = ttk.Entry(
            master=self._frame, textvariable=self._evening_before_var)
        self._evening_after_entry = ttk.Entry(
            master=self._frame, textvariable=self._evening_after_var)

        # Grid the labels and entry fields
        self._morning_before_label.grid(padx=5, pady=5, sticky=constants.W)
        self._morning_before_entry.grid(padx=5, pady=5, sticky=constants.EW)

        self._morning_after_label.grid(padx=5, pady=5, sticky=constants.W)
        self._morning_after_entry.grid(padx=5, pady=5, sticky=constants.EW)

        self._evening_before_label.grid(padx=5, pady=5, sticky=constants.W)
        self._evening_before_entry.grid(padx=5, pady=5, sticky=constants.EW)

        self._evening_after_label.grid(padx=5, pady=5, sticky=constants.W)
        self._evening_after_entry.grid(padx=5, pady=5, sticky=constants.EW)

        # Create the "Calculate" button
        self._calculate_button = ttk.Button(
            master=self._frame,
            text="Laske",
            command=self._calculate_comparison
        )
        self._calculate_button.grid(padx=5, pady=5, sticky=constants.EW)

        # Create the result label to display comparison results
        self._comparison_result_var = StringVar(self._frame)
        self._comparison_result_label = ttk.Label(
            master=self._frame,
            textvariable=self._comparison_result_var,
            foreground="green"
        )
        self._comparison_result_label.grid(padx=5, pady=5)

        self.fields_initialized = True

    def _hide_comparison_fields(self):
        """Hide all the comparison-related fields."""
        self._morning_before_label.grid_remove()
        self._morning_before_entry.grid_remove()
        self._morning_after_label.grid_remove()
        self._morning_after_entry.grid_remove()
        self._evening_before_label.grid_remove()
        self._evening_before_entry.grid_remove()
        self._evening_after_label.grid_remove()
        self._evening_after_entry.grid_remove()
        self._calculate_button.grid_remove()
        self._comparison_result_label.grid_remove()

        self.fields_initialized = False

    def _calculate_comparison(self):
        """Calculate and show the differences between morning/evening PEF and before/after medication."""
        try:
            # Get input values with validation
            morning_before = self._safe_float_conversion(
                self._morning_before_var.get())
            morning_after = self._safe_float_conversion(
                self._morning_after_var.get())
            evening_before = self._safe_float_conversion(
                self._evening_before_var.get())
            evening_after = self._safe_float_conversion(
                self._evening_after_var.get())

            # Debug: Print out the values being passed to the service
            print(
                f"Morning Before: {morning_before}, Morning After: {morning_after}")
            print(
                f"Evening Before: {evening_before}, Evening After: {evening_after}")

            # Calculate the differences using PefService
            # If bronchodilation values are not provided, they will be passed as None
            results = self._pef_service.calculate_pef_differences(
                morning_before, morning_after, evening_before, evening_after
            )

            # Debug: Print out the results from the service
            print(f"Results: {results}")

            # Update the UI with the results
            self._display_comparison_results(results)

        except ValueError:
            self._comparison_result_var.set(
                "Virhe: Täytä kaikki kentät oikein!")

    def _safe_float_conversion(self, value):
        """Safely converts input value to float, returns None if invalid or empty."""
        try:
            return float(value) if value.strip() else None
        except ValueError:
            return None

    def _display_comparison_results(self, results):
        """Helper function to format and display results."""
        # Format each result with a check for None to prevent errors if a value is missing
        morning_evening_diff = f"{results['morning_evening_diff']:.2f}%" if results.get(
            'morning_evening_diff') is not None else "Ei saatavilla"
        before_after_diff_morning = f"{results['before_after_diff_morning']:.2f}%" if results.get(
            'before_after_diff_morning') is not None else "Ei saatavilla"
        before_after_diff_evening = f"{results['before_after_diff_evening']:.2f}%" if results.get(
            'before_after_diff_evening') is not None else "Ei saatavilla"
        warning_message = results.get('warning_message', "Ei varoitusta")

        # Set the results in the UI
        self._comparison_result_var.set(
            f"Aamun-illan ero: {morning_evening_diff}\n"
            f"Aamun ero ennen-jälkeen: {before_after_diff_morning}\n"
            f"Illan ero ennen-jälkeen: {before_after_diff_evening}\n"
            f"Varoitus: {warning_message}"
        )

    def _create_pef_toggle_button(self):
        """Create a button to toggle the PEF monitoring section."""
        self._toggle_button = ttk.Button(self._root, text="Pef-seuranta", command=self._toggle_pef_section)
        self._toggle_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Create the PEF monitoring section (hidden initially)
        self._pef_frame = ttk.Frame(self._root)
        self._pef_frame.grid(row=1, column=0, padx=10, pady=10)

        # This will initially be hidden
        self._pef_frame.grid_forget()

    def _toggle_pef_section(self):
        """Toggle visibility of the PEF monitoring section."""
        print("Toggling PEF section visibility")
        if self._pef_frame.winfo_ismapped():  # If the frame is currently visible
            self._pef_frame.grid_forget()  # Hide the frame
            self._toggle_button.config(text="Pef-seuranta")  # Reset button text
        else:
            if not self._pef_frame.winfo_ismapped():  # If the frame is not visible
                # Create the PEF monitoring section only if it's not already created
                self._create_pef_monitoring_section()
                # Make the frame visible
                self._pef_frame.grid(row=1, column=0, padx=10, pady=10)  # Ensure the frame is placed in the grid
            self._toggle_button.config(text="Piiloita pef-seuranta")

    def _create_pef_monitoring_section(self):
        """Create the PEF monitoring section inputs."""
        # Date picker for the current date
        self._date_label = ttk.Label(self._pef_frame, text="Valitse päivämäärä:")
        self._date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self._calendar = Calendar(self._pef_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self._calendar.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self._calendar.selection_set(datetime.today().date())  # Set default date to today

        # Morning/Evening and Before/After medication dropdowns
        self._time_of_day_label = ttk.Label(self._pef_frame, text="Aika päivästä (AAMU/ILTA):")
        self._time_of_day_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self._time_of_day_dropdown = ttk.Combobox(self._pef_frame, values=["AAMU", "ILTA"])
        self._time_of_day_dropdown.grid(row=1, column=1, padx=5, pady=5)

        self._medication_label = ttk.Label(self._pef_frame, text="Ennen lääkettä tai lääkkeen jälkeen:")
        self._medication_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self._medication_dropdown = ttk.Combobox(self._pef_frame, values=["ENNNEN LÄÄKETÄ", "LÄÄKKEEN JÄLKEEN"])
        self._medication_dropdown.grid(row=2, column=1, padx=5, pady=5)

        # PEF values (3 fields for measurements)
        self._pef_label = ttk.Label(self._pef_frame, text="Syötä PEF-arvot (L/min):")
        self._pef_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self._pef_value_1_label = ttk.Label(self._pef_frame, text="PEF 1:")
        self._pef_value_1_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self._pef_value_1_entry = ttk.Entry(self._pef_frame)
        self._pef_value_1_entry.grid(row=4, column=1, padx=5, pady=5)

        self._pef_value_2_label = ttk.Label(self._pef_frame, text="PEF 2:")
        self._pef_value_2_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        self._pef_value_2_entry = ttk.Entry(self._pef_frame)
        self._pef_value_2_entry.grid(row=5, column=1, padx=5, pady=5)

        self._pef_value_3_label = ttk.Label(self._pef_frame, text="PEF 3:")
        self._pef_value_3_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self._pef_value_3_entry = ttk.Entry(self._pef_frame)
        self._pef_value_3_entry.grid(row=6, column=1, padx=5, pady=5)

        # Save buttons
        self._save_button = ttk.Button(self._pef_frame, text="Tallenna ja sulje", command=self._save_and_close)
        self._save_button.grid(row=7, column=0, padx=5, pady=10)

        self._save_continue_button = ttk.Button(self._pef_frame, text="Tallenna ja jatka",
                                               command=self._save_and_continue)
        self._save_continue_button.grid(row=7, column=1, padx=5, pady=10)

    def _save_and_close(self):
        """Save the data and close the section."""
        self._save_pef_data()
        self._pef_frame.grid_forget()  # Hide the PEF monitoring section
        self._toggle_button.config(text="Pef-seuranta")  # Reset the button text

    def _save_and_continue(self):
        """Save the data and clear the fields for the next input."""
        self._save_pef_data()
        self._clear_pef_inputs()

    def _save_pef_data(self):
        """Collect and store the PEF monitoring data."""
        date = self._calendar.get_date()  # Get the selected date
        username = self._logged_in_user.username
        value1 = self._pef_value_1_entry.get()  # First PEF value
        value2 = self._pef_value_2_entry.get()  # Second PEF value
        value3 = self._pef_value_3_entry.get()  # Third PEF value
        state = self._medication_dropdown.get()  # Before or after medication
        time = self._time_of_day_dropdown.get()
        print(f"Date: {date}, Value1: {value1}, Value2: {value2}, Value3: {value3}, State: {state}, Time: {time}")

        self._pef_service.add_value_to_monitoring(date,
                                                  username,
                                                  value1,
                                                  value2,
                                                  value3,
                                                  state,
                                                  time
                                                  )
        print(f"PEF Data Saved")

    def _clear_pef_inputs(self):
        """Clear all input fields for new data entry."""
        self._calendar.selection_set(datetime.today().date())  # Reset calendar to today
        self._time_of_day_dropdown.set('')  # Reset the time of day dropdown
        self._medication_dropdown.set('')  # Reset the medication dropdown
        self._pef_value_1_entry.delete(0, ttk.END)  # Clear PEF value 1 field
        self._pef_value_2_entry.delete(0, ttk.END)  # Clear PEF value 2 field
        self._pef_value_3_entry.delete(0, ttk.END)  # Clear PEF value 3 field

    def _initialize(self):
        self._frame = ttk.Frame(master=self._root)

        self._error_variable = StringVar(
            self._frame)  # Variable for error messages
        self._error_label = ttk.Label(
            master=self._frame,
            textvariable=self._error_variable,
            foreground="red"  # Error text color
        )
        self._error_label.grid(padx=5, pady=5)
        self._initialize_greeting_label()

        self._initialize_reference_label()  # Initialize the reference label
        self._update_reference_pef_ui()  # Now we can safely call this method

        # Initialize buttons and handlers
        # Initialize the "Laske PEF-viitearvo" button
        self._initialize_pef_reference_button()
        self._initialize_logout_button()  # Initialize the logout button
        # Initialize the 'Laske vertailu' button to start comparison calculation
        self._initialize_comparison_button()  # Add this line
        self._create_pef_toggle_button()
