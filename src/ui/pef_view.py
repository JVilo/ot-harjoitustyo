from tkinter import ttk, StringVar, constants, END, messagebox, Text
import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import textwrap
from services.pef_service import pef_service


class PefListView:
    def __init__(self, root, handle_logout, pef_service, logged_in_user=None, user=None):
        self._root = root
        self._frame = None
        self._age_var = None
        self._height_var = None
        self._gender_var = None
        self._error_variable = StringVar()  # Initialize error variable
        self._error_label = None
        self._morning_before_var = StringVar()
        self._morning_after_var = StringVar()
        self._evening_before_var = StringVar()
        self._evening_after_var = StringVar()
        self._comparison_result_var = StringVar()
        self._calculate_comparison_button = None
        self._comparison_result_label = None
        self._reference_pef_var = None
        self._calculate_button = None
        self._logged_in_user = logged_in_user  # Store the logged-in user
        # Logout handler to call when the button is clicked
        self._handle_logout = handle_logout
        self._reference_pef_var = StringVar()
        self._morning_before_var = StringVar()
        self._vcmd = self._root.register(self.validate_pef_input)

        self._entry = ttk.Entry(
            self._frame,
            validate="key",
            validatecommand=(self._vcmd, '%P')
        )
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
        self._frame.grid(row=0, column=0, sticky="nsew")
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

    def destroy(self):
        self._frame.destroy()

    def validate_pef_input(self, new_value):
        print(f"Validating: '{new_value}'")  # Debug output
        if new_value == "":
            return True
        if new_value.isdigit() and len(new_value) <= 3:
            return True
        return False

    def _initialize_greeting_label(self):
        """Initialize the greeting label to show the user's name."""
        self._greeting_var = StringVar(self._frame)
        greeting_text = f"Hi, {self._logged_in_user.username}!" if self._logged_in_user else "Hi, Guest!"
        self._greeting_var.set(greeting_text)

        greeting_label = ttk.Label(
            self._header_frame, textvariable=self._greeting_var)
        greeting_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    def _initialize_logout_button(self):
        """Place logout button at the top-right corner."""
        logout_button = ttk.Button(
            self._header_frame, text="Logout", command=self._logout)
        logout_button.grid(row=0, column=1, padx=10, pady=10,
                           sticky="e")  # Right-aligned in the top row
        # Keep column 1 for logout, don't stretch it
        self._header_frame.grid_columnconfigure(1, weight=0)
        # Allow column 0 to stretch (greeting label)
        self._header_frame.grid_columnconfigure(0, weight=1)

    def _initialize_reference_label(self):
        """Initialize the reference label to display the reference PEF value."""
        self._reference_pef_var = StringVar(self._frame)  # Initialize it here
        reference_pef_label = ttk.Label(
            self._left_panel, textvariable=self._reference_pef_var)
        reference_pef_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

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
            height_input = self._height_var.get()
            # Validate height
            try:
                height = float(height_input)
            except ValueError:
                messagebox.showerror(title= "Virhe", message="Pituuden tulee olla numero.")
                return

            if height < 85 or height > 272:
                messagebox.showerror(title= "Virhe", message="Pituuden tulee olla välillä 100–272 cm.")
                return
            gender = self._gender_var.get()  # Get the gender value (male or female)

            # Call the method to calculate the reference PEF value
            reference_pef = pef_service.count_reference_pef(
                height, age, gender)
            print(reference_pef, "the value")

            # Update the displayed reference PEF value
            self._reference_pef_var.set(
                f"PEF viitearvosi: {reference_pef:.2f} L/min")
            if self._error_label:
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
            self.fields_initialized = False

        except ValueError:
            self._show_error("An error occurred while calculating.")

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
        self.fields_initialized = True  # Reset the flag for new calculation

    def _show_error(self, message):
        self._error_variable.set(message)
        self._error_label.grid()

    def _hide_error(self):
        self._error_label.grid_remove()

    def _initialize_age_dropdown(self):
        # Ensure age dropdown is initialized
        self._age_label = ttk.Label(
            master=self._reference_section, text="Ikä (vuosina)")  # Label for age
        self._age_var = StringVar()
        # Age dropdown from 5 to 99
        age_options = [str(i) for i in range(5, 100)]
        self._age_var.set(age_options[0])  # Default age

        self._age_dropdown = ttk.Combobox(
            master=self._reference_section, textvariable=self._age_var, values=age_options, state="readonly")
        self._age_label.grid(padx=5, pady=5, sticky=constants.W)
        self._age_dropdown.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_height_field(self):
        self._height_label = ttk.Label(
            master=self._reference_section, text="Pituus (cm)")  # Label for height
        self._height_var = StringVar()

        self._height_entry = ttk.Entry(
            master=self._reference_section, textvariable=self._height_var)
        self._height_label.grid(padx=5, pady=5, sticky=constants.W)
        self._height_entry.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_gender_checkboxes(self):
        self._gender_label = ttk.Label(
            master=self._reference_section, text="Sukupuoli")  # Label for gender
        self._gender_var = StringVar()
        self._gender_var.set("")  # Default to empty value

        self._male_checkbox = ttk.Radiobutton(
            master=self._reference_section, text="Mies", variable=self._gender_var, value="male")
        self._female_checkbox = ttk.Radiobutton(
            master=self._reference_section, text="Nainen", variable=self._gender_var, value="female")

        self._gender_label.grid(padx=5, pady=5, sticky=constants.W)
        self._male_checkbox.grid(padx=5, pady=5, sticky=constants.W)
        self._female_checkbox.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize_pef_reference_button(self):
        """Initializes the button to show/hide PEF reference calculation."""
        self._pef_reference_button = ttk.Button(
            master=self._left_panel,
            text="Laske PEF-viitearvo",
            command=self._toggle_reference_section  # This now toggles the view
        )
        self._pef_reference_button.grid(
            row=3, column=0, padx=10, pady=10, sticky="w")

    def _toggle_reference_section(self):
        """Toggles visibility of the PEF reference calculation section."""
        if self._reference_section.winfo_ismapped():
            self._reference_section.grid_remove()
            self._pef_reference_button.config(text="Laske PEF-viitearvo")
        else:
            self._reference_section.grid()
            self._initialize_fields()  # Ensure fields are shown in the section
            self._pef_reference_button.config(text="Sulje PEF-viitearvo")

        self._pef_reference_button.config(state=constants.NORMAL)

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
            master=self._reference_section,
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
        """Place comparison button below the greeting and logout section."""
        self._calculate_comparison_button = ttk.Button(
            self._left_panel,
            text="Laske vertailu",
            command=self._toggle_comparison_fields  # This should call the toggle function
        )
        self._calculate_comparison_button.grid(
            row=1, column=0, padx=10, pady=10, sticky="w")

    def _toggle_comparison_fields(self):
        """Shows or hides the fields for morning/evening PEF values and handles calculation."""
        print("Toggling comparison fields...")
        if not self.fields_initialized:
            print("Initializing comparison fields...")  # Debugging line
            # Initialize fields for comparison
            self._initialize_comparison_fields()
            self._comparison_frame.grid()
            self._calculate_comparison_button.config(text="Sulje vertailu")
        else:
            print("Hiding comparison fields...")  # Debugging line
            # Hide the comparison fields
            self._hide_comparison_fields()
            self._calculate_comparison_button.config(text="Laske vertailu")

    def _initialize_comparison_fields(self):
        try:
            """Initialize the fields for entering morning and evening PEF values."""
            print("Initializing comparison fields...")  # Debugging line
            vcmd_pef = self._root.register(self.validate_pef_input)

            # Only initialize if they haven't been initialized already
            if self._morning_before_var is None:
                self._morning_before_var = StringVar(self._comparison_frame)
            if self._morning_after_var is None:
                self._morning_after_var = StringVar(self._comparison_frame)
            if self._evening_before_var is None:
                self._evening_before_var = StringVar(self._comparison_frame)
            if self._evening_after_var is None:
                self._evening_after_var = StringVar(self._comparison_frame)

            print(f"morning_before_var initialized: {self._morning_before_var}")
            print(f"morning_after_var initialized: {self._morning_after_var}")

            # Create labels for the input fields
            self._morning_before_label = ttk.Label(
                master=self._comparison_frame, text="Aamun PEF ennen lääkettä (L/min)")
            self._morning_after_label = ttk.Label(
                master=self._comparison_frame, text="Aamun PEF jälkeen lääkettä (L/min)")
            self._evening_before_label = ttk.Label(
                master=self._comparison_frame, text="Illan PEF ennen lääkettä (L/min)")
            self._evening_after_label = ttk.Label(
                master=self._comparison_frame, text="Illan PEF jälkeen lääkettä (L/min)")

            # Create entry fields for the PEF values
            self._morning_before_entry = ttk.Entry(
                master=self._comparison_frame, textvariable=self._morning_before_var, validate="key",
                validatecommand=(vcmd_pef, '%P'))
            self._morning_after_entry = ttk.Entry(
                master=self._comparison_frame, textvariable=self._morning_after_var, validate="key",
                validatecommand=(vcmd_pef, '%P'))
            self._evening_before_entry = ttk.Entry(
                master=self._comparison_frame, textvariable=self._evening_before_var, validate="key",
                validatecommand=(vcmd_pef, '%P'))
            self._evening_after_entry = ttk.Entry(
                master=self._comparison_frame, textvariable=self._evening_after_var, validate="key",
                validatecommand=(vcmd_pef, '%P'))

            # Grid the labels and entry fields inside the comparison frame
            self._morning_before_label.grid(row=0, column=0, padx=5, pady=5, sticky=constants.W)
            self._morning_before_entry.grid(row=0, column=1, padx=5, pady=5, sticky=constants.W)

            self._morning_after_label.grid(row=1, column=0, padx=5, pady=5, sticky=constants.W)
            self._morning_after_entry.grid(row=1, column=1, padx=5, pady=5, sticky=constants.W)

            self._evening_before_label.grid(row=2, column=0, padx=5, pady=5, sticky=constants.W)
            self._evening_before_entry.grid(row=2, column=1, padx=5, pady=5, sticky=constants.W)

            self._evening_after_label.grid(row=3, column=0, padx=5, pady=5, sticky=constants.W)
            self._evening_after_entry.grid(row=3, column=1, padx=5, pady=5, sticky=constants.W)

            # Create the "Calculate" button
            self._calculate_button = ttk.Button(
                master=self._comparison_frame, text="Laske", command=self._calculate_comparison)
            self._calculate_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky=constants.W)

            # Create the result label to display comparison results
            self._comparison_result_var = StringVar(self._comparison_frame)
            self._comparison_result_label = ttk.Label(
                master=self._comparison_frame,
                textvariable=self._comparison_result_var,
                foreground="green"
            )
            self._comparison_result_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=constants.W)

            self.fields_initialized = True
            print("Comparison fields initialized successfully.")
        except Exception as e:
            print(f"Error during initialization: {e}")

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
        print("Comparison fields hidden.")  # Debugging line

    def _calculate_comparison(self):
        """Calculate and show the differences between morning/evening PEF and before/after medication."""
        print("Calculate Comparison Button Pressed")
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

            def validate_pef_value(value_str):
                """Validate PEF value if present."""
                if value_str is None:
                    return None  # Allow empty or invalid values (already handled by _safe_float_conversion)
                if 10 <= value_str <= 999:
                    return value_str
                else:
                    messagebox.showerror("Virhe", "PEF-arvon tulee olla välillä 10–999.")
                    return None

            morning_before = validate_pef_value(morning_before)
            morning_after = validate_pef_value(morning_after)
            evening_before = validate_pef_value(evening_before)
            evening_after = validate_pef_value(evening_after)

            # Debug: Print out the values being passed to the service
            print(
                f"Morning Before: {morning_before}, Morning After: {morning_after}")
            print(
                f"Evening Before: {evening_before}, Evening After: {evening_after}")

            # Calculate the differences using PefService
            results = self._pef_service.calculate_pef_differences(
                morning_before, morning_after, evening_before, evening_after
            )

            # Debug: Print out the results from the service
            print(f"Results: {results}")

            # Update the UI with the results
            self._display_comparison_results(results)

        except ValueError:
            self._comparison_result_var.set("Virhe: Täytä kaikki kentät!")

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
        """Create only the toggle button, not the frame or its contents."""
        self._toggle_button = ttk.Button(
            self._left_panel, text="Pef-seuranta", command=self._toggle_pef_section)
        self._toggle_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self._pef_frame = None

    def _toggle_pef_section(self):
        """Toggle visibility of the PEF monitoring section."""
        if self._pef_frame.winfo_ismapped():
            # Hide the PEF section
            self._pef_frame.grid_forget()
            self._toggle_button.config(text="Pef-seuranta")
        else:
            # Show the PEF section (create if needed)
            if not hasattr(self, '_pef_monitoring_section_created') or not self._pef_monitoring_section_created:
                self._create_pef_monitoring_section()
                self._pef_monitoring_section_created = True

            self._pef_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
            self._populate_pef_data_table()
            self._toggle_button.config(text="Piilota pef-seuranta")

            # Auto-resize the window to fit contents
            self._root.update_idletasks()  # Make sure everything is rendered
            required_height = self._pef_frame.winfo_reqheight() + 300  # Add padding
            current_width = self._root.winfo_width()
            self._root.geometry(f"{current_width}x{required_height}")

    def _create_pef_monitoring_section(self):
        """Create the PEF monitoring section inputs."""

        # Register validation for PEF fields
        vcmd_pef = self._root.register(self.validate_pef_input)

        # Date picker for the current date
        self._date_label = ttk.Label(
            self._pef_frame, text="Valitse päivämäärä:")
        self._date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self._calendar = Calendar(
            self._pef_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            font=("Helvetica", 9),
            showweeknumbers=False,
            firstweekday="monday"
        )
        self._calendar.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self._calendar.selection_set(datetime.today().date())

        # Morning/Evening and Before/After medication dropdowns
        self._time_of_day_label = ttk.Label(
            self._pef_frame, text="Aika päivästä (AAMU/ILTA):")
        self._time_of_day_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self._time_of_day_dropdown = ttk.Combobox(
            self._pef_frame, values=["AAMU", "ILTA"],state="readonly")
        self._time_of_day_dropdown.grid(row=1, column=1, padx=5, pady=5)

        self._medication_label = ttk.Label(
            self._pef_frame, text="Ennen lääkettä tai lääkkeen jälkeen:")
        self._medication_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self._medication_dropdown = ttk.Combobox(
            self._pef_frame, values=["ENNEN LÄÄKETTÄ", "LÄÄKKEEN JÄLKEEN"],state="readonly")
        self._medication_dropdown.grid(row=2, column=1, padx=5, pady=5)

        # PEF values (3 fields for measurements)
        self._pef_label = ttk.Label(
            self._pef_frame, text="Syötä PEF-arvot (L/min):")
        self._pef_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self._pef_value_1_label = ttk.Label(self._pef_frame, text="PEF 1:")
        self._pef_value_1_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self._pef_value_1_entry = ttk.Entry(self._pef_frame, validate="key",
                                            validatecommand=(vcmd_pef, '%P'))
        self._pef_value_1_entry.grid(row=4, column=1, padx=5, pady=5)

        self._pef_value_2_label = ttk.Label(self._pef_frame, text="PEF 2:")
        self._pef_value_2_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        self._pef_value_2_entry = ttk.Entry(self._pef_frame, validate="key",
                                            validatecommand=(vcmd_pef, '%P'))
        self._pef_value_2_entry.grid(row=5, column=1, padx=5, pady=5)

        self._pef_value_3_label = ttk.Label(self._pef_frame, text="PEF 3:")
        self._pef_value_3_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self._pef_value_3_entry = ttk.Entry(self._pef_frame, validate="key",
                                            validatecommand=(vcmd_pef, '%P'))
        self._pef_value_3_entry.grid(row=6, column=1, padx=5, pady=5)

        # Save buttons
        self._save_button = ttk.Button(
            self._pef_frame, text="Tallenna ja sulje", command=self._save_and_close)
        self._save_button.grid(row=7, column=0, padx=5, pady=10)

        self._save_continue_button = ttk.Button(self._pef_frame, text="Tallenna ja jatka",
                                                command=self._save_and_continue)
        self._save_continue_button.grid(row=7, column=1, padx=5, pady=10)

        self._create_pef_data_table()

    def _save_and_close(self):
        """Save the data and close the section."""
        self._save_pef_data()
        self._pef_frame.grid_forget()  # Hide the PEF monitoring section
        self._toggle_button.config(
            text="Pef-seuranta")  # Reset the button text
        self._populate_pef_data_table()

    def _save_and_continue(self):
        """Save the data and clear the fields for the next input — only if successful."""
        if self._save_pef_data():
            self._populate_pef_data_table()
            self._clear_pef_inputs(keep_date=True)

    def _save_pef_data(self):
        """Collect and store the PEF monitoring data."""
        date = self._calendar.get_date()
        username = self._logged_in_user.username
        value1 = self._pef_value_1_entry.get()
        value2 = self._pef_value_2_entry.get()
        value3 = self._pef_value_3_entry.get()
        state = self._medication_dropdown.get()
        time = self._time_of_day_dropdown.get()

        if not all([value1, value2, value3, state, time]):
            messagebox.showerror("Virhe", "Kaikki kentät on täytettävä.")
            return False

        try:
            val1 = int(value1)
            val2 = int(value2)
            val3 = int(value3)
            if not (10 <= val1 <= 999 and 10 <= val2 <= 999 and 10 <= val3 <= 999):
                raise ValueError
        except ValueError:
            messagebox.showerror("Virhe", "PEF-arvojen tulee olla numeroita välillä 10–999.")
            return False

        self._pef_service.add_value_to_monitoring(date, username, value1, value2, value3, state, time)
        print("PEF Data Saved")
        return True

    def _clear_pef_inputs(self, keep_date=False):
        """Clear all input fields for new data entry. Optionally preserve the selected date."""
        if not keep_date:
            self._calendar.selection_set(datetime.today().date())

        self._time_of_day_dropdown.set('')
        self._medication_dropdown.set('')
        self._pef_value_1_entry.delete(0, END)
        self._pef_value_2_entry.delete(0, END)
        self._pef_value_3_entry.delete(0, END)

    def _create_pef_data_table(self):
        """Creates and populates the table to display saved PEF monitoring entries."""
        # Add a label
        label = ttk.Label(self._pef_frame, text="Tallennetut PEF-arvot:")
        label.grid(row=8, column=0, columnspan=2, pady=(10, 0), sticky="w")

        # Define columns
        columns = ("date", "value1", "value2", "value3", "state", "time")

        # Create Treeview with columns
        self._pef_table = ttk.Treeview(self._pef_frame, columns=columns, show="headings", height=5)

        # Add a scrollbar to the table
        self._scrollbar = ttk.Scrollbar(self._pef_frame, orient="vertical", command=self._pef_table.yview)
        self._pef_table.configure(yscrollcommand=self._scrollbar.set)

        # Set table and scrollbar grid layout
        self._pef_table.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=5)
        self._scrollbar.grid(row=9, column=2, sticky="ns")

        # Define headings
        self._pef_table.heading("date", text="Päivämäärä")
        self._pef_table.heading("value1", text="PEF 1")
        self._pef_table.heading("value2", text="PEF 2")
        self._pef_table.heading("value3", text="PEF 3")
        self._pef_table.heading("state", text="Lääke")
        self._pef_table.heading("time", text="Aika päivästä")

        self._pef_table.column("date", anchor="center", width=90)
        self._pef_table.column("value1", anchor="center", width=80)
        self._pef_table.column("value2", anchor="center", width=80)
        self._pef_table.column("value3", anchor="center", width=80)
        self._pef_table.column("state", anchor="center", width=130)
        self._pef_table.column("time", anchor="center", width=110)

        # Add "Lopeta" button after the summary
        self._lopeta_button = ttk.Button(self._pef_frame, text="Lopeta", command=self.lopeta_button_click)
        self._lopeta_button.grid(row=11, column=0, columnspan=2, pady=10)

        self._populate_pef_data_table()  # Load initial data

    def _populate_pef_data_table(self):
        """Fetches and inserts user monitoring data into the table."""
        # First, clear the table
        for row in self._pef_table.get_children():
            self._pef_table.delete(row)

        # Fetch all completed monitoring sessions (with start and end dates)
        completed_sessions = self._pef_service.get_sessions_by_username(self._logged_in_user.username)

        completed_dates = set()

        # Build a set of all dates that are part of completed monitoring periods
        for session in completed_sessions:
            try:
                session_start_date = datetime.strptime(session["start_date"], "%Y-%m-%d").date()
                session_end_date = datetime.strptime(session["end_date"], "%Y-%m-%d").date()
            except Exception as e:
                print(f"Error parsing session dates: {e}")
                continue  # Skip if invalid date format

            current_date = session_start_date
            while current_date <= session_end_date:
                completed_dates.add(current_date)
                current_date += timedelta(days=1)

        # Now fetch all monitoring entries (all saved PEF measurements)
        data = self._pef_service.get_monitoring_by_username()

        print("DEBUG: Retrieved monitoring data:", data)

        if not data:
            return

        # Filter out entries that are already part of completed sessions
        filtered_data = []
        for entry in data:
            try:
                entry_date = datetime.strptime(entry[2], "%Y-%m-%d").date()
            except Exception as e:
                print(f"Error parsing monitoring entry date: {e}")
                continue  # Skip invalid date entries

            if entry_date not in completed_dates:
                filtered_data.append(entry)

        # Now populate the table with filtered (unfinished) monitoring entries
        for entry in filtered_data:
            self._pef_table.insert("", "end", values=(
                entry[2],  # date (as string, original)
                entry[3],  # value1
                entry[4],  # value2
                entry[5],  # value3
                entry[6],  # state (before/after medication)
                entry[7]   # time of day (morning/evening)
            ))

    def lopeta_button_click(self):
        """Handles finalizing the monitoring period and showing the results."""

        table_data = self._pef_table.get_children()

        if not table_data:
            messagebox.showerror("Virhe", "Ei tallennettuja tietoja. Et voi päättää seurantaa ilman tietoja.")
            return

        # Get start and end dates
        start_date = self._pef_table.item(table_data[0])['values'][0]
        end_date = self._pef_table.item(table_data[-1])['values'][0]

        username = self._logged_in_user.username

        # Save monitoring session
        self._pef_service.create_monitoring_session(username, start_date, end_date)

        # Calculate summary
        monitoring_summary = self._pef_service.calculate_monitoring_difference_for_session(
            username, start_date, end_date
        )
        self._show_monitoring_results(monitoring_summary)

    def _open_past_monitorings_view(self):
        """Open a new popup window to select and view past monitoring summaries."""

        # Create a new popup window
        self._past_sessions_window = tk.Toplevel(self._root)
        self._past_sessions_window.title("Aiemmat seurannat")
        self._past_sessions_window.geometry("400x300")  # Set a reasonable size

        # Fetch previous sessions
        sessions = self._pef_service.get_sessions_by_username(self._logged_in_user.username)

        if not sessions:
            # Show a simple message if no previous monitorings
            no_sessions_label = ttk.Label(self._past_sessions_window, text="Sinulla ei ole aiempia seurantoja.")
            no_sessions_label.pack(padx=10, pady=20)

            # Show a simple close button
            close_button = ttk.Button(self._past_sessions_window, text="Sulje",
                                      command=self._past_sessions_window.destroy)
            close_button.pack(pady=10)
            return

        # Create listbox to show sessions
        self._session_listbox = ttk.Treeview(self._past_sessions_window, columns=("start_date", "end_date"),
                                             show="headings")
        self._session_listbox.heading("start_date", text="Alkupäivä")
        self._session_listbox.heading("end_date", text="Loppupäivä")
        self._session_listbox.pack(padx=10, pady=10, fill="both", expand=True)

        for session in sessions:
            self._session_listbox.insert("", "end", values=(session["start_date"], session["end_date"]))

        # Button to view selected session
        view_button = ttk.Button(self._past_sessions_window, text="Näytä seurantaraportti",
                                 command=self._view_selected_session)
        view_button.pack(pady=5)

        # Close button
        close_button = ttk.Button(self._past_sessions_window, text="Sulje", command=self._past_sessions_window.destroy)
        close_button.pack(pady=5)

    def _view_selected_session(self):
        """View the summary of the selected monitoring session."""
        selected_item = self._session_listbox.selection()

        if not selected_item:
            messagebox.showerror("Virhe", "Valitse seuranta ensin.")
            return

        selected_values = self._session_listbox.item(selected_item)['values']
        start_date, end_date = selected_values

        username = self._logged_in_user.username

        # Fetch and calculate the report
        monitoring_summary = self._pef_service.calculate_monitoring_difference_for_session(
            username, start_date, end_date
        )

        if not isinstance(monitoring_summary, dict):
            messagebox.showerror("Virhe", f"Seurantaraportin lataus epäonnistui: {monitoring_summary}")
            return

        # Format the report text
        report_text = textwrap.dedent(f"""
            📊 PEF-seurantaraportti:
    
            • Päivittäinen vaihtelu ≥ 20 % ja 60 L/min: {monitoring_summary['over_20']} kertaa
            • Bronkodilataatiovaste ≥ 15 % ja 60 L/min: {monitoring_summary['over_15']} kertaa
    
            • Seurantajakson korkein PEF-arvo: {monitoring_summary['highest']} L/min
            • Alhaisin PEF-arvo: {monitoring_summary['lowest']} L/min
            • Keskimääräinen PEF-arvo: {monitoring_summary['average']:.1f} L/min
    
            🔔 Yhteenveto:
            {monitoring_summary['warning_message']}
        """)

        # Show the formatted report
        messagebox.showinfo(
            "Seurantaraportti",
            f"Seurantajakso: {start_date} - {end_date}\n\n{report_text.strip()}"
        )
    def _show_monitoring_results(self, summary_data):
        popup = tk.Toplevel(self._root)
        popup.title("Seurannan tulokset")

        # Bind the close event to a function that handles cleanup
        popup.protocol("WM_DELETE_WINDOW", lambda: self._on_results_popup_close(popup))

        result_text = textwrap.dedent(f"""
            📊 PEF-seurannan tulokset:

            • Päivittäinen vaihtelu ≥ 20 % ja 60 L/min: {summary_data['over_20']} kertaa
            • Bronkodilataatiovaste ≥ 15 % ja 60 L/min: {summary_data['over_15']} kertaa

            • Seurantajakson korkein PEF-arvo: {summary_data['highest']} L/min
            • Alhaisin PEF-arvo: {summary_data['lowest']} L/min
            • Keskimääräinen PEF-arvo: {summary_data['average']:.1f} L/min

            🔔 Yhteenveto:
            {summary_data['warning_message']}
        """)

        tk.Label(popup, text=result_text.strip(), justify="left").pack(padx=20, pady=20)

        close_btn = ttk.Button(popup, text="Sulje", command=lambda: self._on_results_popup_close(popup))
        close_btn.pack(pady=(0, 20))

    def _on_results_popup_close(self, popup):
        popup.destroy()
        self._clear_current_session_data()

    def _clear_current_session_data(self):
        """Clears all session-specific data and resets the form."""
        self._clear_pef_inputs()

        # Clear table rows
        for row in self._pef_table.get_children():
            self._pef_table.delete(row)

        # Reset buttons
        self._save_button.config(state="normal")
        self._save_continue_button.config(state="normal")
        self._lopeta_button.config(state="normal")

    def _show_instructions_popup(self):
        """Shows a popup window with the detailed instructions for the app."""
        instructions_text = textwrap.dedent("""
            📖 **PEF-sovelluksen - Ohjeet**

            1️⃣ **PEF-viitearvo**:
                - **PEF-viitearvojen laskeminen**:  
                    Voit laskea PEF-viitearvot painamalla **"Näytä/Peitä PEF-viite"** -painiketta.
                    - Laskuri käyttää antamiasi tietoja, kuten **pituus**, **ikä** ja **sukupuoli**, laskeakseen viitearvot, joiden avulla voit verrata omia PEF-arvojasi odotettuihin arvoihin.
                - Laskennan jälkeen viitearvot näytetään sovelluksen **vasemmalla puolella** vertailua varten.

            2️⃣ **PEF-vertailun teko**:
                - **Pikavertailu - PEF-vertailu**:  
                    PEF-vertailu on suunniteltu nopeisiin tarkistuksiin eri mittaussarjojen välillä.
                    - Jokaiselta päivältä syötetään parhaat ja huonoimmat PEF-arvot useista mittauksista (esim. ennen ja jälkeen lääkityksen). Näin saadaan käsitys vuorokausivaihtelusta.
                    - Voit myös tarkastella **bronkodilataatiovastetta**, jos se on käytettävissä. Tässä tapauksessa käytetään vain lääkityksettömiä PEF-arvoja vuorokausivaihtelun laskemiseen (ilman bronkodilataatiovastetta).
                    - **"Näytä/Peitä vertailu"** -painike kytkee vertailuosion näkyville.

            3️⃣ **PEF-seuranta**:
                - **PEF-tietojen syöttäminen**:  
                    Yksi PEF-mittaus sisältää kolme peräkkäistä puhallusta. Kunkin puhallussarjan korkein PEF-arvo tallennetaan sovellukseen.
                    - Mittaustuloksia seurataan eri vuorokaudenaikoina (Aamu/Ilta), ja merkitään, onko se ennen vai jälkeen lääkityksen.
                    - Paina **"Tallenna ja jatka"** tallentaaksesi tiedot ja syöttääksesi uuden mittaussarjan. Jos olet valmis, paina **"Tallenna ja sulje"** lopettaaksesi istunnon.
                - Kun olet syöttänyt PEF-arvot tietylle ajanjaksolle, paina **"Lopeta"** lopettaaksesi seurantajakson.
                - **"Lopeta"**-painikkeen jälkeen sovellus näyttää seurantajakson yhteenvedon, joka sisältää tärkeimmät tilastot, kuten korkein PEF, keskimääräinen PEF ja vuorokausivaihtelu.
                - Voit tarkastella tuloksia ja nähdä, kuinka PEF-arvosi ovat muuttuneet ajan myötä.

            4️⃣ **Aiemmat seurantajaksojen tulokset**:
                - Käytä **"Katso aiemmat seurannat"** -painiketta tarkastellaksesi aiempia seurantatietoja.
                - Valitse haluamasi jakso nähdäksesi yhteenvedon, joka sisältää yksityiskohtaisen analyysin PEF-arvojen vaihteluista ja lääkityksen vaikutuksesta.
        """)

        # Create the popup window
        popup = tk.Toplevel(self._root)
        popup.title("PEF-sovelluksen ohjeet")

        # Display the instructions text inside the popup
        instructions_label = tk.Label(popup, text=instructions_text, justify="left", padx=10, pady=10)
        instructions_label.pack(padx=10, pady=10)

        # Button to close the instructions window
        close_button = ttk.Button(popup, text="Sulje", command=popup.destroy)
        close_button.pack(pady=10)

    def _initialize(self):
        # Main frame
        self._frame = ttk.Frame(master=self._root)
        self._frame.grid(row=0, column=0, sticky="nsew")
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

        # HEADER FRAME
        self._header_frame = ttk.Frame(self._frame)
        self._header_frame.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self._header_frame.grid_columnconfigure(0, weight=1)
        self._header_frame.grid_columnconfigure(1, weight=0)

        self._initialize_greeting_label()  # This should place greeting label to the left
        self._initialize_logout_button()  # This places logout to the right

        # CONTENT FRAME
        self._content_frame = ttk.Frame(self._frame)
        self._content_frame.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=10)
        self._content_frame.grid_columnconfigure(0, weight=0)  # Left panel
        self._content_frame.grid_columnconfigure(1, weight=1)  # Center panel
        self._content_frame.grid_rowconfigure(0, weight=1)

        # LEFT PANEL
        self._left_panel = ttk.Frame(self._content_frame)
        self._left_panel.grid(row=0, column=0, sticky="n")

        # CENTER PANEL
        self._center_panel = ttk.Frame(self._content_frame)
        self._center_panel.grid(row=0, column=1, sticky="nsew", padx=20)

        # Add buttons in left panel
        self._initialize_reference_label()  # Reference info label
        if self._logged_in_user:
            self._update_reference_pef_ui()
        self._initialize_pef_reference_button()  # Näytä/Peitä PEF-viite
        self._initialize_comparison_button()  # Näytä/Peitä vertailu
        self._create_pef_toggle_button()  # Näytä/Peitä seuranta
        self._view_past_sessions_button = ttk.Button(
            self._left_panel,
            text="Katso aiemmat seurannat",
            command=self._open_past_monitorings_view
        )
        self._view_past_sessions_button.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self._show_instructions_button = ttk.Button(
            self._left_panel,
            text="Näytä ohjeet",  # Button text: "Show Instructions"
            command=self._show_instructions_popup  # Function to show instructions
        )
        self._show_instructions_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # Placeholder frames for toggleable sections
        self._reference_section = ttk.Frame(self._center_panel)
        self._reference_section.grid(row=0, column=0, sticky="ew")
        self._reference_section.grid_remove()  # Initially hidden

        self._comparison_frame = ttk.Frame(self._center_panel)
        self._comparison_frame.grid(row=1, column=0, sticky="ew")
        self._comparison_frame.grid_remove()

        self._pef_frame = ttk.Frame(self._center_panel)
        self._pef_frame.grid(row=2, column=0, sticky="ew")
        self._pef_frame.grid_remove()
