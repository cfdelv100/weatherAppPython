from datetime import datetime, timezone
import threading
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from PIL import Image, ImageTk
except ImportError:  # pragma: no cover - optional dependency in some environments
    Image = None
    ImageTk = None

from src.db.repository import UserRepository
from src.db.schema import initialize_database
from src.services.airport_service import AirportService
from src.services.geo_service import GeoService
from src.services.weather_service import WeatherService
from src.ui.map_view import MapView


class WeatherApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Weather & Airport Info App")
        self.window.geometry("900x600")
        self.dark_theme = {
            "bg": "#121212",
            "fg": "#FFFFFF",
            "button_bg": "#333333",
            "button_fg": "#FFFFFF",
            "entry_bg": "#2A2A2A",
            "entry_fg": "#FFFFFF",
            "frame_bg": "#1E1E1E",
            "highlight_bg": "#3700B3",
            "accent_color": "#BB86FC",
        }
        self.user_repo = UserRepository()
        self.weather_service = WeatherService()
        self.geo_service = GeoService()
        self.airport_service = AirportService()
        initialize_database()
        self.apply_dark_theme()
        self.setup_login_ui()
        self.window.mainloop()

    def apply_dark_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.dark_theme["bg"])
        style.configure("TLabel", background=self.dark_theme["bg"], foreground=self.dark_theme["fg"])
        style.configure(
            "Status.TLabel",
            background=self.dark_theme["bg"],
            foreground=self.dark_theme["accent_color"],
            font=("Arial", 11, "bold"),
        )
        style.configure("TButton", background=self.dark_theme["button_bg"], foreground=self.dark_theme["button_fg"])
        style.configure("TEntry", fieldbackground=self.dark_theme["entry_bg"], foreground=self.dark_theme["entry_fg"])
        style.configure("TNotebook", background=self.dark_theme["bg"])
        style.configure("TNotebook.Tab", background=self.dark_theme["button_bg"], foreground=self.dark_theme["fg"], padding=[10, 2])
        style.map("TNotebook.Tab", background=[("selected", self.dark_theme["highlight_bg"])])
        style.configure("Treeview", background=self.dark_theme["entry_bg"], foreground=self.dark_theme["fg"], fieldbackground=self.dark_theme["entry_bg"])
        style.map("Treeview", background=[("selected", self.dark_theme["accent_color"])], foreground=[("selected", "#000000")])
        style.configure("TLabelframe", background=self.dark_theme["frame_bg"])
        style.configure("TLabelframe.Label", background=self.dark_theme["frame_bg"], foreground=self.dark_theme["fg"])
        style.configure("TProgressbar", background=self.dark_theme["accent_color"])
        self.window.configure(background=self.dark_theme["bg"])

    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def _bind_mousewheel(self, canvas):
        def _on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        def _bind(event):
            self.window.bind_all("<MouseWheel>", _on_mousewheel)
            self.window.bind_all("<Button-4>", _on_mousewheel)
            self.window.bind_all("<Button-5>", _on_mousewheel)

        def _unbind(event):
            self.window.unbind_all("<MouseWheel>")
            self.window.unbind_all("<Button-4>")
            self.window.unbind_all("<Button-5>")

        canvas.bind("<Enter>", _bind)
        canvas.bind("<Leave>", _unbind)

    def setup_login_ui(self):
        self.clear_window()
        ttk.Label(self.window, text="Welcome to the Weather & Airport Info App!", font=("Arial", 16, "bold")).pack(pady=10)
        login_frame = ttk.Frame(self.window, padding=20)
        login_frame.pack(pady=20)

        ttk.Label(login_frame, text="Username").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(login_frame, text="Password").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, pady=5)

        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Register", command=self.show_registration).pack(side=tk.LEFT, padx=5)

    def show_registration(self):
        self.clear_window()
        ttk.Label(self.window, text="Create New Account", font=("Arial", 16, "bold")).pack(pady=10)
        reg_frame = ttk.Frame(self.window, padding=20)
        reg_frame.pack(pady=10)

        labels = ["Username*", "Password*", "Confirm Password*", "Full Name*", "Age", "Email"]
        entries = []
        for row, text in enumerate(labels):
            ttk.Label(reg_frame, text=text).grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(reg_frame, show="*" if "Password" in text else "", width=30)
            entry.grid(row=row, column=1, pady=5)
            entries.append(entry)

        self.reg_username, self.reg_password, self.reg_confirm_pwd, self.reg_name, self.reg_age, self.reg_email = entries
        ttk.Label(reg_frame, text="* Required fields", font=("Arial", 8, "italic")).grid(row=6, column=0, columnspan=2, sticky="w", pady=5)

        button_frame = ttk.Frame(reg_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Create Account", command=self.register_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back to Login", command=self.setup_login_ui).pack(side=tk.LEFT, padx=5)

    def register_user(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm_pwd = self.reg_confirm_pwd.get()
        name = self.reg_name.get().strip()
        age_str = self.reg_age.get().strip()
        email = self.reg_email.get().strip()

        if not username or not password or not name:
            messagebox.showerror("Registration Error", "Please fill all required fields")
            return
        if password != confirm_pwd:
            messagebox.showerror("Registration Error", "Passwords do not match")
            return

        age = None
        if age_str:
            try:
                age = int(age_str)
                if age < 0 or age > 120:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Registration Error", "Please enter a valid age")
                return

        if not self.user_repo.create_user(username, password, name, age, email):
            messagebox.showerror("Registration Error", "Username already exists")
            return

        messagebox.showinfo("Registration Successful", "Your account has been created successfully. You can now log in.")
        self.setup_login_ui()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        user = self.user_repo.authenticate(username, password)
        if user:
            self.show_main_app(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def show_main_app(self, user):
        self.clear_window()
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        profile_tab = ttk.Frame(notebook)
        weather_tab = ttk.Frame(notebook)
        airport_tab = ttk.Frame(notebook)
        notebook.add(profile_tab, text="Profile")
        notebook.add(weather_tab, text="Weather")
        notebook.add(airport_tab, text="Airport & Airline Info")

        self.setup_profile_tab(profile_tab, user)
        self.setup_weather_tab(weather_tab)
        self.setup_airport_tab(airport_tab)

    def setup_profile_tab(self, parent, user):
        profile_frame = ttk.LabelFrame(parent, text="User Profile")
        profile_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(profile_frame, text=f"Name: {user[2]}", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        if user[3]:
            ttk.Label(profile_frame, text=f"Age: {user[3]}", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        if user[4]:
            ttk.Label(profile_frame, text=f"Email: {user[4]}", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Button(profile_frame, text="Logout", command=self.setup_login_ui).pack(anchor="w", padx=10, pady=10)

    def setup_weather_tab(self, parent):
        weather_frame = ttk.Frame(parent)
        weather_frame.pack(fill="both", expand=True, padx=20, pady=20)

        search_frame = ttk.Frame(weather_frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(search_frame, text="Enter City:").pack(side=tk.LEFT, padx=5)
        self.city_entry = ttk.Entry(search_frame, width=30)
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.bind("<Return>", lambda event: self.get_weather())
        ttk.Button(search_frame, text="Search", command=self.get_weather).pack(side=tk.LEFT, padx=5)

        weather_results_container = ttk.Frame(weather_frame)
        weather_results_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.weather_result_canvas = tk.Canvas(
            weather_results_container,
            highlightthickness=0,
            background=self.dark_theme["bg"],
        )
        weather_scrollbar = ttk.Scrollbar(weather_results_container, orient="vertical", command=self.weather_result_canvas.yview)
        self.weather_result_canvas.configure(yscrollcommand=weather_scrollbar.set)

        weather_scrollbar.pack(side="right", fill="y")
        self.weather_result_canvas.pack(side="left", fill="both", expand=True)

        self.weather_result_frame = ttk.Frame(self.weather_result_canvas)
        self.weather_result_window = self.weather_result_canvas.create_window((0, 0), window=self.weather_result_frame, anchor="nw")

        self.weather_result_frame.bind(
            "<Configure>",
            lambda event: self.weather_result_canvas.configure(scrollregion=self.weather_result_canvas.bbox("all")),
        )
        self.weather_result_canvas.bind(
            "<Configure>",
            lambda event: self.weather_result_canvas.itemconfigure(self.weather_result_window, width=event.width),
        )
        self._bind_mousewheel(self.weather_result_canvas)

    def setup_airport_tab(self, parent):
        airport_frame = ttk.Frame(parent)
        airport_frame.pack(fill="both", expand=True, padx=20, pady=20)

        search_frame = ttk.LabelFrame(airport_frame, text="Search Options")
        search_frame.pack(fill="x", padx=10, pady=10)

        code_frame = ttk.Frame(search_frame)
        code_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(code_frame, text="Airport Code (e.g. LAX, JFK):").pack(side=tk.LEFT, padx=5)
        self.airport_code_entry = ttk.Entry(code_frame, width=10)
        self.airport_code_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(code_frame, text="Get Airlines", command=lambda: self.get_airport_data("code")).pack(side=tk.LEFT, padx=5)

        city_frame = ttk.Frame(search_frame)
        city_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(city_frame, text="City Name:").pack(side=tk.LEFT, padx=5)
        self.airport_city_entry = ttk.Entry(city_frame, width=30)
        self.airport_city_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(city_frame, text="Get Airlines", command=lambda: self.get_airport_data("city")).pack(side=tk.LEFT, padx=5)

        airport_results_container = ttk.Frame(airport_frame)
        airport_results_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.airport_result_canvas = tk.Canvas(
            airport_results_container,
            highlightthickness=0,
            background=self.dark_theme["bg"],
        )
        airport_scrollbar = ttk.Scrollbar(airport_results_container, orient="vertical", command=self.airport_result_canvas.yview)
        self.airport_result_canvas.configure(yscrollcommand=airport_scrollbar.set)

        airport_scrollbar.pack(side="right", fill="y")
        self.airport_result_canvas.pack(side="left", fill="both", expand=True)

        self.airline_result_frame = ttk.Frame(self.airport_result_canvas)
        self.airport_result_window = self.airport_result_canvas.create_window((0, 0), window=self.airline_result_frame, anchor="nw")

        self.airline_result_frame.bind(
            "<Configure>",
            lambda event: self.airport_result_canvas.configure(scrollregion=self.airport_result_canvas.bbox("all")),
        )
        self.airport_result_canvas.bind(
            "<Configure>",
            lambda event: self.airport_result_canvas.itemconfigure(self.airport_result_window, width=event.width),
        )
        self._bind_mousewheel(self.airport_result_canvas)

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return

        self.weather_result_canvas.yview_moveto(0)
        for widget in self.weather_result_frame.winfo_children():
            widget.destroy()

        self.weather_status_label = ttk.Label(
            self.weather_result_frame,
            text=f"Searching weather for {city}...",
            style="Status.TLabel",
        )
        self.weather_status_label.pack(anchor="w", padx=10, pady=(0, 8))

        loading_label = ttk.Label(self.weather_result_frame, text="Loading weather data...")
        loading_label.pack()
        progress = ttk.Progressbar(self.weather_result_frame, orient="horizontal", mode="indeterminate")
        progress.pack(fill="x", padx=20, pady=10)
        progress.start()

        def fetch_weather_data():
            try:
                weather = self.weather_service.get_weather(city)
                geo = self.geo_service.geocode_city(city)
                self.window.after(
                    0,
                    lambda: [loading_label.destroy(), progress.destroy(), self.display_weather(weather, geo)],
                )
            except Exception as error:
                self.window.after(
                    0,
                    lambda: [loading_label.destroy(), progress.destroy(), messagebox.showerror("Weather Error", str(error))],
                )

        threading.Thread(target=fetch_weather_data, daemon=True).start()

    def display_weather(self, data, geo_data=None):
        for widget in self.weather_result_frame.winfo_children():
            widget.destroy()

        accent_bar = tk.Frame(self.weather_result_frame, height=4, bg=self.dark_theme["accent_color"])
        accent_bar.pack(fill="x", padx=10, pady=(0, 10))

        city_name = data.get("name", "Unknown")
        weather_status_text = f"City found: {city_name}"
        if geo_data:
            weather_status_text = f"City found: {city_name} at {geo_data['lat']:.4f}, {geo_data['lon']:.4f}"

        self.weather_status_label = ttk.Label(
            self.weather_result_frame,
            text=weather_status_text,
            style="Status.TLabel",
        )
        self.weather_status_label.pack(anchor="w", padx=10, pady=(0, 8))

        map_section = ttk.Frame(self.weather_result_frame)
        map_section.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if geo_data:
            map_view = MapView(map_section, title="Weather Location Map")
            map_view.pack(fill="both", expand=True)
            map_view.show_location(geo_data["lat"], geo_data["lon"], city_name)
        else:
            ttk.Label(
                map_section,
                text="No map available for this city.",
                style="Status.TLabel",
            ).pack(anchor="w", padx=10, pady=6)

        result_container = ttk.Frame(self.weather_result_frame)
        result_container.pack(fill="x", padx=10, pady=(0, 10))

        weather_desc = data["weather"][0]["description"]
        temperature_c = round(data["main"]["temp"] - 273.15)
        temperature_f = round((temperature_c * 9 / 5) + 32)
        humidity = data["main"].get("humidity", "N/A")
        sea_level = data["main"].get("sea_level", "N/A")
        icon_code = data["weather"][0]["icon"]
        local_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        ttk.Label(result_container, text=f"Location: {city_name}", font=("Arial", 14, "bold")).pack(anchor="w")
        ttk.Label(result_container, text=f"The current time is: {local_time}", font=("Arial", 12)).pack(anchor="w")
        ttk.Label(result_container, text=f"Weather: {weather_desc}", font=("Arial", 12)).pack(anchor="w")
        ttk.Label(result_container, text=f"Temperature: {temperature_c}°C", font=("Arial", 12)).pack(anchor="w")
        ttk.Label(result_container, text=f"Temperature: {temperature_f}°F", font=("Arial", 12)).pack(anchor="w")
        ttk.Label(result_container, text=f"Sea Level: {sea_level}", font=("Arial", 12)).pack(anchor="w")
        ttk.Label(result_container, text=f"Humidity: {humidity}", font=("Arial", 12)).pack(anchor="w")

        icon_bytes = self.weather_service.get_icon_bytes(icon_code)
        icon_label = None
        if icon_bytes and Image is not None and ImageTk is not None:
            image = ImageTk.PhotoImage(Image.open(icon_bytes))
            icon_label = ttk.Label(result_container, image=image)
            icon_label.image = image
            icon_label.pack(pady=10)

    def get_airport_data(self, search_type):
        self.airport_result_canvas.yview_moveto(0)
        for widget in self.airline_result_frame.winfo_children():
            widget.destroy()

        if search_type == "code":
            search_param = self.airport_code_entry.get().strip().upper()
            if not search_param:
                messagebox.showwarning("Input Error", "Please enter an airport code")
                return
            data = self.airport_service.get_airport_by_code(search_param)
        else:
            search_param = self.airport_city_entry.get().strip()
            if not search_param:
                messagebox.showwarning("Input Error", "Please enter a city name")
                return
            data = self.airport_service.get_airport_by_city(search_param)

        if not data:
            self.airport_status_label = ttk.Label(
                self.airline_result_frame,
                text=f"No airport found for {search_param}",
                style="Status.TLabel",
            )
            self.airport_status_label.pack(anchor="w", padx=10, pady=(0, 8))
            messagebox.showinfo("Airport Not Found", f"No airport data found for: {search_param}")
            return

        self.display_airport_data(data)

    def display_airport_data(self, data):
        for widget in self.airline_result_frame.winfo_children():
            widget.destroy()

        accent_bar = tk.Frame(self.airline_result_frame, height=4, bg=self.dark_theme["accent_color"])
        accent_bar.pack(fill="x", padx=10, pady=(0, 10))

        airport_status = ttk.Label(
            self.airline_result_frame,
            text=f"Airport found: {data['name']} ({data['code']})",
            style="Status.TLabel",
        )
        airport_status.pack(anchor="w", padx=10, pady=(0, 8))
        airport_status.pack_forget()

        airport_info = ttk.LabelFrame(self.airline_result_frame, text="Airport Information")
        airport_info.pack_forget()
        ttk.Label(airport_info, text=data["name"], font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        ttk.Label(airport_info, text=f"Location: {data['city']}, {data['country']}", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)

        map_view = MapView(self.airline_result_frame, title="Airport Location Map")
        map_view.pack_forget()
        map_view.show_location(data["latitude"], data["longitude"], data["name"])

        airline_frame = None
        if data.get("airlines"):
            airline_frame = ttk.LabelFrame(self.airline_result_frame, text="Airlines Operating at this Airport")
            airline_frame.pack_forget()
            columns = ("name", "iata", "terminal")
            airlines_tree = ttk.Treeview(airline_frame, columns=columns, show="headings")
            airlines_tree.heading("name", text="Airline Name")
            airlines_tree.heading("iata", text="IATA Code")
            airlines_tree.heading("terminal", text="Terminal(s)")
            airlines_tree.column("name", width=250)
            airlines_tree.column("iata", width=80)
            airlines_tree.column("terminal", width=100)
            for airline in data["airlines"]:
                airlines_tree.insert("", "end", values=(airline["name"], airline["iata"], airline["terminal"]))
            scrollbar = ttk.Scrollbar(airline_frame, orient="vertical", command=airlines_tree.yview)
            airlines_tree.configure(yscrollcommand=scrollbar.set)
            airlines_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        else:
            airline_frame = ttk.Frame(self.airline_result_frame)
            ttk.Label(airline_frame, text="No airline information available", font=("Arial", 12)).pack(pady=10)
            airline_frame.pack_forget()

        self.window.after(80, lambda: airport_status.pack(anchor="w", padx=10, pady=(0, 8)))
        self.window.after(160, lambda: airport_info.pack(fill="x", padx=10, pady=10))
        self.window.after(240, lambda: map_view.pack(fill="both", expand=True, padx=10, pady=10))
        if airline_frame is not None:
            self.window.after(320, lambda: airline_frame.pack(fill="both", expand=True, padx=10, pady=10))


def main():
    WeatherApp()
