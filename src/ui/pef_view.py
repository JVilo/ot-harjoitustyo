from tkinter import ttk, StringVar, constants, END, messagebox, Text
import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import textwrap
from services.pef_service import pef_service


class PefListView:
    """View class responsible for managing PEF measurements."""

    def __init__(self, root, handle_logout, pef_service, logged_in_user=None, user=None):
        self._root = root
        self._frame = None
        self._error_variable = StringVar()
        self._logged_in_user = logged_in_user
        self._handle_logout = handle_logout
        self._pef_service = pef_service
        self._user = user

        self._initialize_variables()
        self._initialize()

    def _initialize_variables(self):
        """Initialize StringVars and control variables."""
        self._age_var = StringVar()
        self._height_var = StringVar()
        self._gender_var = StringVar()
        self._reference_pef_var = StringVar()
        self._morning_before_var = StringVar()
        self._morning_after_var = StringVar()
        self._evening_before_var = StringVar()
        self._evening_after_var = StringVar()
        self._comparison_result_var = StringVar()

        self._fields_initialized = False
        self._vcmd = self._root.register(self.validate_pef_input)

        self._calendar = None
        self._time_of_day_dropdown = None
        self._medication_dropdown = None
        self._pef_value_1_entry = None
        self._pef_value_2_entry = None
        self._pef_value_3_entry = None
        self._toggle_button = None
        self._pef_frame = None

    def pack(self):
        """Show the frame."""
        self._frame.grid(row=0, column=0, sticky="nsew")
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

    def destroy(self):
        """Destroy the frame."""
        self._frame.destroy()

    def validate_pef_input(self, new_value):
        """Validate PEF input field values."""
        if new_value == "":
            return True
        if new_value.isdigit() and len(new_value) <= 3:
            return True
        return False

    def _initialize(self):
        """Initialize the main UI layout."""
        self._frame = ttk.Frame(master=self._root)
        self._frame.grid(row=0, column=0, sticky="nsew")
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

        self._header_frame = ttk.Frame(self._frame)
        self._header_frame.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self._header_frame.grid_columnconfigure(0, weight=1)

        self._initialize_greeting_label()
        self._initialize_logout_button()

        self._content_frame = ttk.Frame(self._frame)
        self._content_frame.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=10)
        self._content_frame.grid_columnconfigure(0, weight=0)
        self._content_frame.grid_columnconfigure(1, weight=1)
        self._content_frame.grid_rowconfigure(0, weight=1)

        self._left_panel = ttk.Frame(self._content_frame)
        self._left_panel.grid(row=0, column=0, sticky="n")

        self._center_panel = ttk.Frame(self._content_frame)
        self._center_panel.grid(row=0, column=1, sticky="nsew", padx=20)

        self._initialize_left_panel_buttons()

        self._reference_section = ttk.Frame(self._center_panel)
        self._comparison_frame = ttk.Frame(self._center_panel)
        self._pef_frame = ttk.Frame(self._center_panel)

        self._reference_section.grid(row=0, column=0, sticky="ew")
        self._comparison_frame.grid(row=1, column=0, sticky="ew")
        self._pef_frame.grid(row=2, column=0, sticky="ew")

        self._reference_section.grid_remove()
        self._comparison_frame.grid_remove()
        self._pef_frame.grid_remove()

    def _initialize_greeting_label(self):
        """Create greeting label for user."""
        self._greeting_var = StringVar()
        greeting_text = f"Hi, {self._logged_in_user.username}!" if self._logged_in_user else "Hi, Guest!"
        self._greeting_var.set(greeting_text)

        greeting_label = ttk.Label(
            self._header_frame, textvariable=self._greeting_var)
        greeting_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    def _initialize_logout_button(self):
        """Create logout button."""
        logout_button = ttk.Button(
            self._header_frame, text="Logout", command=self._logout)
        logout_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self._header_frame.grid_columnconfigure(1, weight=0)

    def _initialize_left_panel_buttons(self):
        """Initialize buttons and labels for left panel."""
        self._initialize_reference_label()
        if self._logged_in_user:
            self._update_reference_pef_ui()

        self._pef_reference_button = ttk.Button(
            self._left_panel, text="Laske PEF-viitearvo", command=self._toggle_reference_section
        )
        self._pef_reference_button.grid(
            row=3, column=0, padx=10, pady=10, sticky="w")

        self._calculate_comparison_button = ttk.Button(
            self._left_panel, text="Laske vertailu", command=self._toggle_comparison_fields
        )
        self._calculate_comparison_button.grid(
            row=1, column=0, padx=10, pady=10, sticky="w")

        self._toggle_button = ttk.Button(
            self._left_panel, text="Pef-seuranta", command=self._toggle_pef_section
        )
        self._toggle_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self._view_past_sessions_button = ttk.Button(
            self._left_panel, text="Katso aiemmat seurannat", command=self._open_past_monitorings_view
        )
        self._view_past_sessions_button.grid(
            row=4, column=0, padx=10, pady=10, sticky="w")

        self._show_instructions_button = ttk.Button(
            self._left_panel, text="Näytä ohjeet", command=self._show_instructions_popup
        )
        self._show_instructions_button.grid(
            row=5, column=0, padx=10, pady=10, sticky="w")

    def _initialize_reference_label(self):
        """Initialize label to show PEF reference value."""
        reference_label = ttk.Label(
            self._left_panel, textvariable=self._reference_pef_var)
        reference_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    def _update_reference_pef_ui(self):
        """Update displayed reference PEF value."""
        reference_pef = self._pef_service.get_reference_pef_for_user()

        if isinstance(reference_pef, list):
            if reference_pef:
                reference_pef = reference_pef[-1]
            else:
                reference_pef = None

        if reference_pef is not None:
            self._reference_pef_var.set(
                f"PEF viitearvosi: {reference_pef.value:.2f} L/min")
        else:
            self._reference_pef_var.set("No reference PEF value found.")

    def _logout(self):
        """Handle user logout."""
        self._handle_logout()

    def _toggle_reference_section(self):
        """Toggle visibility of the PEF reference input section."""
        if self._reference_section.winfo_ismapped():
            self._reference_section.grid_remove()
            self._pef_reference_button.config(text="Laske PEF-viitearvo")
        else:
            self._hide_all_sections()
            self._reference_section.grid()
            self._initialize_fields()
            self._pef_reference_button.config(text="Sulje PEF-viitearvo")

        self._pef_reference_button.config(state=constants.NORMAL)

    def _initialize_fields(self):
        """Initialize dropdowns and entries for PEF reference calculation."""
        if self._fields_initialized:
            return

        self._initialize_age_dropdown()
        self._initialize_height_field()
        self._initialize_gender_checkboxes()
        self._initialize_calculate_button()

        self._fields_initialized = True

    def _initialize_age_dropdown(self):
        """Initialize dropdown for selecting age."""
        self._age_label = ttk.Label(
            master=self._reference_section, text="Ikä (vuosina)")
        age_options = [str(i) for i in range(5, 100)]
        self._age_var.set(age_options[0])

        self._age_dropdown = ttk.Combobox(
            master=self._reference_section,
            textvariable=self._age_var,
            values=age_options,
            state="readonly"
        )
        self._age_label.grid(padx=5, pady=5, sticky=constants.W)
        self._age_dropdown.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_height_field(self):
        """Initialize entry for entering height."""
        self._height_label = ttk.Label(
            master=self._reference_section, text="Pituus (cm)")
        self._height_entry = ttk.Entry(
            master=self._reference_section, textvariable=self._height_var)
        self._height_label.grid(padx=5, pady=5, sticky=constants.W)
        self._height_entry.grid(padx=5, pady=5, sticky=constants.EW)

    def _initialize_gender_checkboxes(self):
        """Initialize gender selection."""
        self._gender_label = ttk.Label(
            master=self._reference_section, text="Sukupuoli")
        self._male_checkbox = ttk.Radiobutton(
            master=self._reference_section, text="Mies", variable=self._gender_var, value="male")
        self._female_checkbox = ttk.Radiobutton(
            master=self._reference_section, text="Nainen", variable=self._gender_var, value="female")

        self._gender_label.grid(padx=5, pady=5, sticky=constants.W)
        self._male_checkbox.grid(padx=5, pady=5, sticky=constants.W)
        self._female_checkbox.grid(padx=5, pady=5, sticky=constants.W)

    def _initialize_calculate_button(self):
        """Initialize the calculate button for PEF reference."""
        self._calculate_button = ttk.Button(
            master=self._reference_section,
            text="Laske",
            state=constants.DISABLED,
            command=self._calculate_pef_handler
        )
        self._calculate_button.grid(padx=5, pady=5, sticky=constants.EW)

        self._age_var.trace("w", self._enable_calculate_button)
        self._height_var.trace("w", self._enable_calculate_button)
        self._gender_var.trace("w", self._enable_calculate_button)

    def _enable_calculate_button(self, *args):
        """Enable calculate button when all fields are filled."""
        if self._age_var.get() and self._height_var.get() and self._gender_var.get():
            self._calculate_button.config(state=constants.NORMAL)
        else:
            self._calculate_button.config(state=constants.DISABLED)

    def _calculate_pef_handler(self):
        """Handler to calculate and display reference PEF."""
        try:
            age = int(self._age_var.get())
            height = float(self._height_var.get())
            gender = self._gender_var.get()

            if not (85 <= height <= 272):
                messagebox.showerror(
                    title="Virhe", message="Pituuden tulee olla välillä 85–272 cm.")
                return

            reference_pef = pef_service.count_reference_pef(
                height, age, gender)
            self._reference_pef_var.set(
                f"PEF viitearvosi: {reference_pef:.2f} L/min")

            self._reference_section.grid_remove()
            self._pef_reference_button.config(text="Laske PEF-viitearvo")

        except ValueError:
            messagebox.showerror(
                title="Virhe", message="Syötä kelvolliset numerot.")

    def _toggle_comparison_fields(self):
        """Toggle visibility of PEF comparison fields."""
        if self._comparison_frame.winfo_ismapped():
            self._comparison_frame.grid_remove()
            self._calculate_comparison_button.config(text="Laske vertailu")
        else:
            self._hide_all_sections()
            self._comparison_frame.grid()
            self._initialize_comparison_fields()
            self._calculate_comparison_button.config(text="Sulje vertailu")

    def _initialize_comparison_fields(self):
        """Initialize fields for comparing morning/evening PEF values."""
        if hasattr(self, '_comparison_fields_initialized') and self._comparison_fields_initialized:
            return

        labels_texts = [
            "Aamun PEF ennen lääkettä (L/min)",
            "Aamun PEF jälkeen lääkettä (L/min)",
            "Illan PEF ennen lääkettä (L/min)",
            "Illan PEF jälkeen lääkettä (L/min)"
        ]
        vars_list = [
            self._morning_before_var,
            self._morning_after_var,
            self._evening_before_var,
            self._evening_after_var
        ]

        for idx, (text, var) in enumerate(zip(labels_texts, vars_list)):
            label = ttk.Label(self._comparison_frame, text=text)
            entry = ttk.Entry(self._comparison_frame, textvariable=var, validate="key",
                              validatecommand=(self._vcmd, '%P'))
            label.grid(row=idx, column=0, padx=5, pady=5, sticky=constants.W)
            entry.grid(row=idx, column=1, padx=5, pady=5)

        self._compare_button = ttk.Button(
            self._comparison_frame, text="Laske", command=self._calculate_comparison)
        self._compare_button.grid(row=4, column=0, columnspan=2, pady=10)

        self._comparison_result_label = ttk.Label(
            self._comparison_frame, textvariable=self._comparison_result_var, foreground="green"
        )
        self._comparison_result_label.grid(
            row=5, column=0, columnspan=2, pady=5)

        self._comparison_fields_initialized = True

    def _calculate_comparison(self):
        """Calculate PEF differences and update results."""
        """Calculate PEF differences and update results."""
        try:
            mb = self._safe_float_conversion(self._morning_before_var.get())
            ma = self._safe_float_conversion(self._morning_after_var.get())
            eb = self._safe_float_conversion(self._evening_before_var.get())
            ea = self._safe_float_conversion(self._evening_after_var.get())

            # Check how many values are filled
            filled = [v for v in [mb, ma, eb, ea] if v is not None]
            if len(filled) < 2:
                messagebox.showerror(
                    "Virhe", "Syötä vähintään kaksi arvoa vertailuun.")
                return

            # Validate range only for filled fields
            for label, value in [("Aamu ennen", mb), ("Aamu jälkeen", ma),
                                 ("Ilta ennen", eb), ("Ilta jälkeen", ea)]:
                if value is not None and not (10 <= value <= 999):
                    messagebox.showerror(
                        "Virhe", f"{label} PEF-arvon tulee olla 10–999.")
                    return

            # Call your service with what we have
            results = self._pef_service.calculate_pef_differences(
                mb, ma, eb, ea)
            self._display_comparison_results(results)

        except Exception as e:
            messagebox.showerror("Virhe", f"Tapahtui virhe: {e}")

    def _safe_float_conversion(self, value):
        """Safely convert string to float."""
        try:
            return float(value) if value.strip() else None
        except ValueError:
            return None

    def _display_comparison_results(self, results):
        """Format and display comparison results."""
        def fmt(value):
            return f"{value:.2f}%" if value is not None else "–"

        text = (
            f"Aamun-illan ero: {fmt(results.get('morning_evening_diff'))}\n"
            f"Aamun ero ennen-jälkeen: {fmt(results.get('before_after_diff_morning'))}\n"
            f"Illan ero ennen-jälkeen: {fmt(results.get('before_after_diff_evening'))}\n"
            f"Varoitus: {results.get('warning_message', 'Ei varoitusta')}"
        )
        self._comparison_result_var.set(text)

    def _toggle_pef_section(self):
        """Toggle visibility of the PEF monitoring section."""
        if self._pef_frame.winfo_ismapped():
            self._pef_frame.grid_forget()
            self._toggle_button.config(text="Pef-seuranta")
        else:
            self._hide_all_sections()
            if not hasattr(self, '_pef_monitoring_section_created'):
                self._create_pef_monitoring_section()
                self._pef_monitoring_section_created = True

            self._pef_frame.grid(row=1, column=0, padx=10,
                                 pady=10, sticky="ew")
            self._populate_pef_data_table()
            self._toggle_button.config(text="Piilota pef-seuranta")

    def _create_pef_monitoring_section(self):
        """Create the PEF monitoring input section."""
        vcmd_pef = self._root.register(self.validate_pef_input)

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

        self._time_of_day_label = ttk.Label(
            self._pef_frame, text="Aika päivästä (AAMU/ILTA):")
        self._time_of_day_label.grid(
            row=1, column=0, padx=5, pady=5, sticky="w")

        self._time_of_day_dropdown = ttk.Combobox(
            self._pef_frame, values=["AAMU", "ILTA"], state="readonly"
        )
        self._time_of_day_dropdown.grid(row=1, column=1, padx=5, pady=5)

        self._medication_label = ttk.Label(
            self._pef_frame, text="Ennen lääkettä tai lääkkeen jälkeen:")
        self._medication_label.grid(
            row=2, column=0, padx=5, pady=5, sticky="w")

        self._medication_dropdown = ttk.Combobox(
            self._pef_frame, values=["ENNEN LÄÄKETTÄ", "LÄÄKKEEN JÄLKEEN"], state="readonly"
        )
        self._medication_dropdown.grid(row=2, column=1, padx=5, pady=5)

        self._initialize_pef_value_entries(vcmd_pef)
        self._initialize_monitoring_buttons()
        self._create_pef_data_table()

    def _initialize_pef_value_entries(self, vcmd_pef):
        """Create input fields for PEF values."""
        labels = ["PEF 1:", "PEF 2:", "PEF 3:"]
        entries = []

        for idx, text in enumerate(labels, start=4):
            label = ttk.Label(self._pef_frame, text=text)
            label.grid(row=idx, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(self._pef_frame, validate="key",
                              validatecommand=(vcmd_pef, '%P'))
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entries.append(entry)

        self._pef_value_1_entry, self._pef_value_2_entry, self._pef_value_3_entry = entries

    def _initialize_monitoring_buttons(self):
        """Create save and continue buttons."""
        self._save_button = ttk.Button(
            self._pef_frame, text="Tallenna ja sulje", command=self._save_and_close)
        self._save_button.grid(row=7, column=0, padx=5, pady=10)

        self._save_continue_button = ttk.Button(
            self._pef_frame, text="Tallenna ja jatka", command=self._save_and_continue)
        self._save_continue_button.grid(row=7, column=1, padx=5, pady=10)

    def _save_and_close(self):
        """Save monitoring data and close the PEF section."""
        if self._save_pef_data():
            self._pef_frame.grid_forget()
            self._toggle_button.config(text="Pef-seuranta")
            self._populate_pef_data_table()

    def _save_and_continue(self):
        """Save monitoring data and clear fields for next input."""
        if self._save_pef_data():
            self._populate_pef_data_table()
            self._clear_pef_inputs(keep_date=True)

    def _save_pef_data(self):
        """Save the entered PEF values to the service."""
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
            val1, val2, val3 = int(value1), int(value2), int(value3)
            if not (10 <= val1 <= 999 and 10 <= val2 <= 999 and 10 <= val3 <= 999):
                raise ValueError

            date_str = str(date)  # Convert to string format 'YYYY-MM-DD'
            existing = self._pef_service.get_monitoring_by_username()
            for entry in existing:
                if (entry['username'] == username and
                        entry['date'] == date_str and
                        entry['state'] == state and
                        entry['time'] == time):
                    messagebox.showerror(
                        "Virhe", "Tälle päivälle on jo tehty seuranta näillä parametreillä.")
                    return False

            if abs(val2 - val1) > 20 or abs(val3 - val2) > 20:
                messagebox.showerror(
                    "Virhe", "Kahden peräkkäisen PEF-arvon ero ei saa ylittää 20 yksikköä.")
                return False

        except ValueError:
            messagebox.showerror(
                "Virhe", "PEF-arvojen tulee olla numeroita välillä 10–999.")
            return False

        self._pef_service.add_value_to_monitoring(
            date, username, value1, value2, value3, state, time)
        return True

    def _clear_pef_inputs(self, keep_date=False):
        """Clear all input fields after save."""
        if not keep_date:
            self._calendar.selection_set(datetime.today().date())

        self._time_of_day_dropdown.set('')
        self._medication_dropdown.set('')
        self._pef_value_1_entry.delete(0, END)
        self._pef_value_2_entry.delete(0, END)
        self._pef_value_3_entry.delete(0, END)

    def _populate_pef_data_table(self):
        """Populate the PEF table with user's monitoring data."""
        for row in self._pef_table.get_children():
            self._pef_table.delete(row)

        completed_sessions = self._pef_service.get_sessions_by_username(
            self._logged_in_user.username)
        completed_dates = set()

        for session in completed_sessions:
            try:
                start = datetime.strptime(
                    session["start_date"], "%Y-%m-%d").date()
                end = datetime.strptime(session["end_date"], "%Y-%m-%d").date()
                current = start
                while current <= end:
                    completed_dates.add(current)
                    current += timedelta(days=1)
            except Exception:
                continue

        data = self._pef_service.get_monitoring_by_username()
        if not data:
            return

        for entry in data:
            try:
                entry_date = datetime.strptime(entry[2], "%Y-%m-%d").date()
            except Exception:
                continue

            if entry_date not in completed_dates:
                self._pef_table.insert("", "end", values=(
                    entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]
                ))

    def _create_pef_data_table(self):
        """Create the Treeview table for displaying monitoring data."""
        label = ttk.Label(self._pef_frame, text="Tallennetut PEF-arvot:")
        label.grid(row=8, column=0, columnspan=2, pady=(10, 0), sticky="w")

        columns = ("date", "value1", "value2", "value3", "state", "time")
        self._pef_table = ttk.Treeview(
            self._pef_frame, columns=columns, show="headings", height=5)

        scrollbar = ttk.Scrollbar(
            self._pef_frame, orient="vertical", command=self._pef_table.yview)
        self._pef_table.configure(yscrollcommand=scrollbar.set)

        self._pef_table.grid(row=9, column=0, columnspan=2,
                             sticky="nsew", pady=5)
        scrollbar.grid(row=9, column=2, sticky="ns")

        headings = {
            "date": "Päivämäärä", "value1": "PEF 1", "value2": "PEF 2",
            "value3": "PEF 3", "state": "Lääke", "time": "Aika päivästä"
        }

        for col, name in headings.items():
            self._pef_table.heading(col, text=name)

        self._pef_table.column("date", anchor="center", width=90)
        self._pef_table.column("value1", anchor="center", width=80)
        self._pef_table.column("value2", anchor="center", width=80)
        self._pef_table.column("value3", anchor="center", width=80)
        self._pef_table.column("state", anchor="center", width=130)
        self._pef_table.column("time", anchor="center", width=110)

        self._lopeta_button = ttk.Button(
            self._pef_frame, text="Lopeta", command=self.lopeta_button_click)
        self._lopeta_button.grid(row=11, column=0, columnspan=2, pady=10)

    def lopeta_button_click(self):
        """Finalize the monitoring period and show results."""
        table_data = self._pef_table.get_children()

        if not table_data:
            messagebox.showerror("Virhe", "Ei tallennettuja tietoja.")
            return

        start_date = self._pef_table.item(table_data[0])['values'][0]
        end_date = self._pef_table.item(table_data[-1])['values'][0]
        username = self._logged_in_user.username

        self._pef_service.create_monitoring_session(
            username, start_date, end_date)
        summary = self._pef_service.calculate_monitoring_difference_for_session(
            username, start_date, end_date)
        self._show_monitoring_results(summary)

    def _open_past_monitorings_view(self):
        """Open a window listing past monitoring sessions."""
        self._past_sessions_window = tk.Toplevel(self._root)
        self._past_sessions_window.title("Aiemmat seurannat")
        self._past_sessions_window.geometry("400x300")

        sessions = self._pef_service.get_sessions_by_username(
            self._logged_in_user.username)

        if not sessions:
            label = ttk.Label(self._past_sessions_window,
                              text="Sinulla ei ole aiempia seurantoja.")
            label.pack(padx=10, pady=20)
            ttk.Button(self._past_sessions_window, text="Sulje",
                       command=self._past_sessions_window.destroy).pack(pady=10)
            return

        self._session_listbox = ttk.Treeview(
            self._past_sessions_window, columns=("start_date", "end_date"), show="headings"
        )
        self._session_listbox.heading("start_date", text="Alkupäivä")
        self._session_listbox.heading("end_date", text="Loppupäivä")
        self._session_listbox.pack(padx=10, pady=10, fill="both", expand=True)

        for session in sessions:
            self._session_listbox.insert("", "end", values=(
                session["start_date"], session["end_date"]))

        view_button = ttk.Button(
            self._past_sessions_window, text="Näytä seurantaraportti", command=self._view_selected_session)
        view_button.pack(pady=5)

        close_button = ttk.Button(
            self._past_sessions_window, text="Sulje", command=self._past_sessions_window.destroy)
        close_button.pack(pady=5)

    def _view_selected_session(self):
        """Show monitoring summary for selected session."""
        selected_item = self._session_listbox.selection()

        if not selected_item:
            messagebox.showerror("Virhe", "Valitse seuranta ensin.")
            return

        selected_values = self._session_listbox.item(selected_item)['values']
        start_date, end_date = selected_values
        username = self._logged_in_user.username

        summary = self._pef_service.calculate_monitoring_difference_for_session(
            username, start_date, end_date)

        if not isinstance(summary, dict):
            messagebox.showerror(
                "Virhe", "Seurantaraportin lataus epäonnistui.")
            return

        report_text = textwrap.dedent(f"""
            📊 PEF-seurantaraportti:

            • Päivittäinen vaihtelu ≥ 20 % ja 60 L/min: {summary['over_20']} kertaa
            • Bronkodilataatiovaste ≥ 15 % ja 60 L/min: {summary['over_15']} kertaa

            • Korkein PEF-arvo: {summary['highest']} L/min
            • Alhaisin PEF-arvo: {summary['lowest']} L/min
            • Keskimääräinen PEF: {summary['average']:.1f} L/min

            🔔 Yhteenveto:
            {summary['warning_message']}
        """)

        messagebox.showinfo("Seurantaraportti", report_text.strip())

    def _show_monitoring_results(self, summary_data):
        """Show results of finalized monitoring session."""
        popup = tk.Toplevel(self._root)
        popup.title("Seurannan tulokset")

        popup.protocol("WM_DELETE_WINDOW",
                       lambda: self._on_results_popup_close(popup))

        result_text = textwrap.dedent(f"""
            📊 PEF-seurannan tulokset:

            • Päivittäinen vaihtelu ≥ 20 % ja 60 L/min: {summary_data['over_20']} kertaa
            • Bronkodilataatiovaste ≥ 15 % ja 60 L/min: {summary_data['over_15']} kertaa

            • Korkein PEF: {summary_data['highest']} L/min
            • Alhaisin PEF: {summary_data['lowest']} L/min
            • Keskimääräinen PEF: {summary_data['average']:.1f} L/min

            🔔 Yhteenveto:
            {summary_data['warning_message']}
        """)

        tk.Label(popup, text=result_text.strip(),
                 justify="left").pack(padx=20, pady=20)
        ttk.Button(popup, text="Sulje", command=lambda: self._on_results_popup_close(
            popup)).pack(pady=(0, 20))

    def _on_results_popup_close(self, popup):
        """Handle closing of results popup."""
        popup.destroy()
        self._clear_current_session_data()

    def _clear_current_session_data(self):
        """Reset form after finishing a monitoring session."""
        self._clear_pef_inputs()
        for row in self._pef_table.get_children():
            self._pef_table.delete(row)

    def _show_instructions_popup(self):
        """Show app instructions in a popup."""
        instructions_text = textwrap.dedent("""
            📖 PEF-sovelluksen - Ohjeet

            1️⃣ PEF-viitearvon laskeminen:
                Syötä ikä, pituus ja sukupuoli. Saat henkilökohtaisen PEF-viitearvosi.

            2️⃣ PEF-vertailu:
                Syötä PEF-mittaukset aamulla ja illalla, lääkkeen kanssa tai ilman.

            3️⃣ PEF-seuranta:
                Syötä mittaukset seurannan aikana. Sovellus laskee vaihtelut ja tallentaa tulokset.

            4️⃣ Aiemmat seurannat:
                Tarkastele aiemmin tallennettuja seurantaraportteja.
        """)

        popup = tk.Toplevel(self._root)
        popup.title("Ohjeet")

        tk.Label(popup, text=instructions_text.strip(),
                 justify="left", padx=10, pady=10).pack(padx=10, pady=10)
        ttk.Button(popup, text="Sulje", command=popup.destroy).pack(pady=10)

    def _hide_all_sections(self):
        self._reference_section.grid_remove()
        self._comparison_frame.grid_remove()
        self._pef_frame.grid_remove()

        # Reset button labels
        self._pef_reference_button.config(text="Laske PEF-viitearvo")
        self._calculate_comparison_button.config(text="Laske vertailu")
        self._toggle_button.config(text="Pef-seuranta")
