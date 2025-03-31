from io import BytesIO
import sqlite3
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import urllib.request
import threading
import json
import config


class WeatherApp:
    def __init__(self):
        # Initialize main window
        self.window = tk.Tk()
        self.window.title('Weather & Airport Info App')
        self.window.geometry('900x600')
        self.window['background'] = 'gray'

        # API configuration
        self.WEATHER_BASE_URL = config.BASE_URL
        self.WEATHER_API_KEY = config.API_KEY  # Replace with config.API_KEY
        self.WEATHER_ICON_BASE_URL = config.ICON_BASE_URL

        # Airport API configuration
        self.AIRPORT_API_URL = "https://api.example.com/airports"  # Replace with actual airport API URL
        self.AIRPORT_API_KEY = "your_airport_api_key"  # Replace with actual API key

        # Create database and tables if they don't exist
        self.initialize_database()

        # Show login screen
        self.setup_login_ui()
        self.window.mainloop()

    def initialize_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()

            # Create users table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                email TEXT
            )
            ''')

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror('Database Error', f'Error initializing database: {e}')

    def setup_login_ui(self):
        """Set up the login screen UI elements"""
        # Clear main window
        for widget in self.window.winfo_children():
            widget.destroy()

        ttk.Label(self.window, text="Welcome to the Weather & Airport Info App!",
                  font=('Arial', 16, 'bold')).pack(pady=10)

        # Login frame
        login_frame = ttk.Frame(self.window, padding=20)
        login_frame.pack(pady=20)

        ttk.Label(login_frame, text='Username').grid(row=0, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(login_frame, text='Password').grid(row=1, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(login_frame, show='*', width=30)
        self.password_entry.grid(row=1, column=1, pady=5)

        # Buttons frame
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        login_button = ttk.Button(button_frame, text='Login', command=self.login)
        login_button.pack(side=tk.LEFT, padx=5)

        register_button = ttk.Button(button_frame, text='Register', command=self.show_registration)
        register_button.pack(side=tk.LEFT, padx=5)

    def show_registration(self):
        """Display the registration form"""
        # Clear main window
        for widget in self.window.winfo_children():
            widget.destroy()

        ttk.Label(self.window, text="Create New Account",
                  font=('Arial', 16, 'bold')).pack(pady=10)

        # Registration frame
        reg_frame = ttk.Frame(self.window, padding=20)
        reg_frame.pack(pady=10)

        # Username
        ttk.Label(reg_frame, text='Username*').grid(row=0, column=0, sticky='w', pady=5)
        self.reg_username = ttk.Entry(reg_frame, width=30)
        self.reg_username.grid(row=0, column=1, pady=5)

        # Password
        ttk.Label(reg_frame, text='Password*').grid(row=1, column=0, sticky='w', pady=5)
        self.reg_password = ttk.Entry(reg_frame, show='*', width=30)
        self.reg_password.grid(row=1, column=1, pady=5)

        # Confirm Password
        ttk.Label(reg_frame, text='Confirm Password*').grid(row=2, column=0, sticky='w', pady=5)
        self.reg_confirm_pwd = ttk.Entry(reg_frame, show='*', width=30)
        self.reg_confirm_pwd.grid(row=2, column=1, pady=5)

        # Full Name
        ttk.Label(reg_frame, text='Full Name*').grid(row=3, column=0, sticky='w', pady=5)
        self.reg_name = ttk.Entry(reg_frame, width=30)
        self.reg_name.grid(row=3, column=1, pady=5)

        # Age
        ttk.Label(reg_frame, text='Age').grid(row=4, column=0, sticky='w', pady=5)
        self.reg_age = ttk.Entry(reg_frame, width=30)
        self.reg_age.grid(row=4, column=1, pady=5)

        # Email
        ttk.Label(reg_frame, text='Email').grid(row=5, column=0, sticky='w', pady=5)
        self.reg_email = ttk.Entry(reg_frame, width=30)
        self.reg_email.grid(row=5, column=1, pady=5)

        # Required fields note
        ttk.Label(reg_frame, text='* Required fields',
                  font=('Arial', 8, 'italic')).grid(row=6, column=0, columnspan=2, sticky='w', pady=5)

        # Buttons
        button_frame = ttk.Frame(reg_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)

        register_button = ttk.Button(button_frame, text='Create Account', command=self.register_user)
        register_button.pack(side=tk.LEFT, padx=5)

        back_button = ttk.Button(button_frame, text='Back to Login', command=self.setup_login_ui)
        back_button.pack(side=tk.LEFT, padx=5)

    def register_user(self):
        """Register a new user"""
        # Get form data
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm_pwd = self.reg_confirm_pwd.get()
        name = self.reg_name.get().strip()
        age_str = self.reg_age.get().strip()
        email = self.reg_email.get().strip()

        # Validate required fields
        if not username or not password or not name:
            messagebox.showerror('Registration Error', 'Please fill all required fields')
            return

        # Validate password match
        if password != confirm_pwd:
            messagebox.showerror('Registration Error', 'Passwords do not match')
            return

        # Validate age if provided
        age = None
        if age_str:
            try:
                age = int(age_str)
                if age < 0 or age > 120:
                    messagebox.showerror('Registration Error', 'Please enter a valid age')
                    return
            except ValueError:
                messagebox.showerror('Registration Error', 'Age must be a number')
                return

        try:
            # Connect to database
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                messagebox.showerror('Registration Error', 'Username already exists')
                conn.close()
                return

            # Insert new user
            cursor.execute(
                'INSERT INTO users (username, password, name, age, email) VALUES (?, ?, ?, ?, ?)',
                (username, password, name, age, email)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo('Registration Successful',
                                'Your account has been created successfully. You can now log in.')

            # Return to log-in screen
            self.setup_login_ui()

        except sqlite3.Error as e:
            messagebox.showerror('Database Error', f'Error creating user: {e}')

    def login(self):
        """Handle login authentication"""
        try:
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()

            username = self.username_entry.get()
            password = self.password_entry.get()

            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?;',
                           (username, password))
            user = cursor.fetchone()

            if user:
                self.show_main_app(user)
            else:
                messagebox.showerror('Login Failed', 'Invalid username or password')

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror('Database Error', f'Error connecting to database: {e}')

    def show_main_app(self, user):
        """Display the main application with tabs for different features"""
        # Clear main window
        for widget in self.window.winfo_children():
            widget.destroy()

        # Create a tabbed interface
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Profile tab
        profile_tab = ttk.Frame(notebook)
        notebook.add(profile_tab, text="Profile")

        # Weather tab
        weather_tab = ttk.Frame(notebook)
        notebook.add(weather_tab, text="Weather")

        # Airport/Airline tab
        airline_tab = ttk.Frame(notebook)
        notebook.add(airline_tab, text="Airport & Airline Info")

        # Set up each tab
        self.setup_profile_tab(profile_tab, user)
        self.setup_weather_tab(weather_tab)
        self.setup_airline_tab(airline_tab)

    def setup_profile_tab(self, parent, user):
        """Set up the profile tab"""
        profile_frame = ttk.LabelFrame(parent, text="User Profile")
        profile_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(profile_frame, text=f'Name: {user[2]}', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)

        # Only show age if it exists
        if user[3]:
            ttk.Label(profile_frame, text=f'Age: {user[3]}', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)

        # Only show email if it exists
        if user[4]:
            ttk.Label(profile_frame, text=f'Email: {user[4]}', font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)

        # Logout button
        logout_button = ttk.Button(profile_frame, text="Logout", command=self.setup_login_ui)
        logout_button.pack(anchor='w', padx=10, pady=10)

    def setup_weather_tab(self, parent):
        """Set up the weather tab"""
        weather_frame = ttk.Frame(parent)
        weather_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Search frame
        search_frame = ttk.Frame(weather_frame)
        search_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(search_frame, text="Enter City:").pack(side=tk.LEFT, padx=5)
        self.city_entry = ttk.Entry(search_frame, font='Century 12', width=30)
        self.city_entry.pack(side=tk.LEFT, padx=5)
        self.city_entry.bind('<Return>', lambda event: self.get_weather())

        search_button = ttk.Button(search_frame, text='Search', command=self.get_weather)
        search_button.pack(side=tk.LEFT, padx=5)

        # Result frame for weather information
        self.weather_result_frame = ttk.Frame(weather_frame)
        self.weather_result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_airline_tab(self, parent):
        """Set up the airport/airline tab"""
        airline_frame = ttk.Frame(parent)
        airline_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Search options frame
        search_frame = ttk.LabelFrame(airline_frame, text="Search Options")
        search_frame.pack(fill="x", padx=10, pady=10)

        # Search by airport code
        airport_frame = ttk.Frame(search_frame)
        airport_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(airport_frame, text="Airport Code (e.g. LAX, JFK):").pack(side=tk.LEFT, padx=5)
        self.airport_code_entry = ttk.Entry(airport_frame, width=10)
        self.airport_code_entry.pack(side=tk.LEFT, padx=5)

        airport_search_button = ttk.Button(
            airport_frame,
            text='Get Airlines',
            command=lambda: self.get_airport_data("code")
        )
        airport_search_button.pack(side=tk.LEFT, padx=5)

        # Search by city name
        city_frame = ttk.Frame(search_frame)
        city_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(city_frame, text="City Name:").pack(side=tk.LEFT, padx=5)
        self.airport_city_entry = ttk.Entry(city_frame, width=30)
        self.airport_city_entry.pack(side=tk.LEFT, padx=5)

        city_search_button = ttk.Button(
            city_frame,
            text='Get Airlines',
            command=lambda: self.get_airport_data("city")
        )
        city_search_button.pack(side=tk.LEFT, padx=5)

        # Result frame for airline information
        self.airline_result_frame = ttk.Frame(airline_frame)
        self.airline_result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def get_weather(self):
        """Get weather information for the entered city"""
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return

        # Clear previous results
        for widget in self.weather_result_frame.winfo_children():
            widget.destroy()

        # Show loading indicator
        loading_label = ttk.Label(self.weather_result_frame, text="Loading weather data...")
        loading_label.pack()
        progress = ttk.Progressbar(self.weather_result_frame, orient='horizontal', mode='indeterminate')
        progress.pack(fill='x', padx=20, pady=10)
        progress.start()

        # Use threading to prevent UI freeze during API request
        def fetch_weather_data():
            try:
                requests_url = f"{self.WEATHER_BASE_URL}?appid={self.WEATHER_API_KEY}&q={city}"
                response = requests.get(requests_url)

                # Remove loading indicators
                self.window.after(0, lambda: [loading_label.destroy(), progress.destroy()])

                if response.status_code == 200:
                    data = response.json()
                    self.window.after(0, lambda: self.display_weather(data))
                else:
                    self.window.after(0, lambda: messagebox.showerror(
                        "Weather Error",
                        f"Could not find weather for '{city}'. Status code: {response.status_code}"
                    ))
            except Exception as e:
                self.window.after(0, lambda: [
                    loading_label.destroy(),
                    progress.destroy(),
                    messagebox.showerror("Error", f"An error occurred: {str(e)}")
                ])

        threading.Thread(target=fetch_weather_data, daemon=True).start()

    def display_weather(self, data):
        """Display the weather data in the result frame"""
        # Extract data
        city_name = data['name']
        weather_desc = data['weather'][0]['description']
        temperature = round(data["main"]["temp"] - 273.15)
        temperatureFarenheight = round((temperature * (9/5)) + 32)
        icon_code = data['weather'][0]['icon']

        # Create results display
        result_container = ttk.Frame(self.weather_result_frame)
        result_container.pack(pady=10)

        ttk.Label(result_container, text=f"Location: {city_name}",
                  font=('Arial', 14, 'bold')).pack(anchor='w')
        ttk.Label(result_container, text=f"Weather: {weather_desc}",
                  font=('Arial', 12)).pack(anchor='w')
        ttk.Label(result_container, text=f"Temperature: {temperature}°C",
                  font=('Arial', 12)).pack(anchor='w')
        ttk.Label(result_container, text=f"Temperature: {temperatureFarenheight}°F",
                  font=('Arial', 12)).pack(anchor='w')

        # Display weather icon
        self.display_weather_icon(result_container, icon_code)

    def display_weather_icon(self, parent, icon_code):
        """Display the weather icon"""
        try:
            icons_url = f"{self.WEATHER_ICON_BASE_URL}/{icon_code}@2x.png"
            response = requests.get(icons_url)

            if response.status_code == 200:
                image = ImageTk.PhotoImage(Image.open(BytesIO(response.content)))
                icon_label = ttk.Label(parent, image=image)
                icon_label.image = image  # Keep a reference to prevent garbage collection
                icon_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading weather icon: {e}")

    def get_airport_data(self, search_type):
        """Get airport and airline data based on search criteria"""
        # Clear previous results
        for widget in self.airline_result_frame.winfo_children():
            widget.destroy()

        # Get search parameters
        if search_type == "code":
            search_param = self.airport_code_entry.get().strip().upper()
            if not search_param:
                messagebox.showwarning("Input Error", "Please enter an airport code")
                return
            endpoint = f"{self.AIRPORT_API_URL}/airport/{search_param}"
        else:  # search_type == "city"
            search_param = self.airport_city_entry.get().strip()
            if not search_param:
                messagebox.showwarning("Input Error", "Please enter a city name")
                return
            endpoint = f"{self.AIRPORT_API_URL}/city/{search_param}"

        # Show loading indicator
        loading_label = ttk.Label(self.airline_result_frame, text="Loading airport data...")
        loading_label.pack()
        progress = ttk.Progressbar(self.airline_result_frame, orient='horizontal', mode='indeterminate')
        progress.pack(fill='x', padx=20, pady=10)
        progress.start()

        # Use threading to prevent UI freeze during API request
        def fetch_airport_data():
            try:
                # For this example, we'll simulate the API response
                # In a real application, you would use requests:
                # headers = {"Authorization": f"Bearer {self.AIRPORT_API_KEY}"}
                # response = requests.get(endpoint, headers=headers)

                # Simulate API call delay
                import time
                time.sleep(1.5)

                # Remove loading indicators
                self.window.after(0, lambda: [loading_label.destroy(), progress.destroy()])

                # Simulate API response based on search type
                if search_type == "code":
                    if search_param in ["LAX", "JFK", "ORD", "ATL", "DFW"]:
                        self.window.after(0,
                                          lambda: self.display_airport_data(self.get_mock_airport_data(search_param)))
                    else:
                        self.window.after(0, lambda: messagebox.showinfo(
                            "Airport Not Found",
                            f"No data found for airport code: {search_param}"
                        ))
                else:  # search_type == "city"
                    if search_param.lower() in ["los angeles", "new york", "chicago", "atlanta", "dallas"]:
                        city_code_map = {
                            "los angeles": "LAX",
                            "new york": "JFK",
                            "chicago": "ORD",
                            "atlanta": "ATL",
                            "dallas": "DFW"
                        }
                        code = city_code_map[search_param.lower()]
                        self.window.after(0, lambda: self.display_airport_data(self.get_mock_airport_data(code)))
                    else:
                        self.window.after(0, lambda: messagebox.showinfo(
                            "Airport Not Found",
                            f"No airports found for city: {search_param}"
                        ))

            except Exception as e:
                self.window.after(0, lambda: [
                    loading_label.destroy(),
                    progress.destroy(),
                    messagebox.showerror("Error", f"An error occurred: {str(e)}")
                ])

        threading.Thread(target=fetch_airport_data, daemon=True).start()

    def get_mock_airport_data(self, airport_code):
        """Generate mock airport data for demonstration"""
        airport_data = {
            "LAX": {
                "name": "Los Angeles International Airport",
                "city": "Los Angeles",
                "country": "United States",
                "airlines": [
                    {"name": "American Airlines", "iata": "AA", "terminal": "4,5"},
                    {"name": "Delta Air Lines", "iata": "DL", "terminal": "2,3"},
                    {"name": "United Airlines", "iata": "UA", "terminal": "7,8"},
                    {"name": "Alaska Airlines", "iata": "AS", "terminal": "6"},
                    {"name": "Southwest Airlines", "iata": "WN", "terminal": "1"}
                ]
            },
            "JFK": {
                "name": "John F. Kennedy International Airport",
                "city": "New York",
                "country": "United States",
                "airlines": [
                    {"name": "American Airlines", "iata": "AA", "terminal": "8"},
                    {"name": "Delta Air Lines", "iata": "DL", "terminal": "2,4"},
                    {"name": "JetBlue Airways", "iata": "B6", "terminal": "5"},
                    {"name": "Lufthansa", "iata": "LH", "terminal": "1"},
                    {"name": "British Airways", "iata": "BA", "terminal": "7"}
                ]
            },
            "ORD": {
                "name": "O'Hare International Airport",
                "city": "Chicago",
                "country": "United States",
                "airlines": [
                    {"name": "American Airlines", "iata": "AA", "terminal": "3"},
                    {"name": "United Airlines", "iata": "UA", "terminal": "1"},
                    {"name": "Frontier Airlines", "iata": "F9", "terminal": "5"},
                    {"name": "Spirit Airlines", "iata": "NK", "terminal": "3"},
                    {"name": "Air Canada", "iata": "AC", "terminal": "5"}
                ]
            },
            "ATL": {
                "name": "Hartsfield-Jackson Atlanta International Airport",
                "city": "Atlanta",
                "country": "United States",
                "airlines": [
                    {"name": "Delta Air Lines", "iata": "DL", "terminal": "S,N"},
                    {"name": "Southwest Airlines", "iata": "WN", "terminal": "N"},
                    {"name": "American Airlines", "iata": "AA", "terminal": "T"},
                    {"name": "United Airlines", "iata": "UA", "terminal": "T"},
                    {"name": "Spirit Airlines", "iata": "NK", "terminal": "N"}
                ]
            },
            "DFW": {
                "name": "Dallas/Fort Worth International Airport",
                "city": "Dallas",
                "country": "United States",
                "airlines": [
                    {"name": "American Airlines", "iata": "AA", "terminal": "A,B,C,D"},
                    {"name": "Spirit Airlines", "iata": "NK", "terminal": "E"},
                    {"name": "Delta Air Lines", "iata": "DL", "terminal": "E"},
                    {"name": "United Airlines", "iata": "UA", "terminal": "E"},
                    {"name": "Frontier Airlines", "iata": "F9", "terminal": "E"}
                ]
            }
        }

        return airport_data.get(airport_code, {})

    def display_airport_data(self, data):
        """Display the airport and airline data"""
        if not data:
            ttk.Label(self.airline_result_frame,
                      text="No airport data found",
                      font=('Arial', 12)).pack(pady=10)
            return

        # Create airport info section
        airport_info = ttk.LabelFrame(self.airline_result_frame, text="Airport Information")
        airport_info.pack(fill="x", padx=10, pady=10)

        ttk.Label(airport_info, text=data["name"],
                  font=('Arial', 14, 'bold')).pack(anchor='w', padx=10, pady=5)
        ttk.Label(airport_info,
                  text=f"Location: {data['city']}, {data['country']}",
                  font=('Arial', 12)).pack(anchor='w', padx=10, pady=5)

        # Create airline section
        if "airlines" in data and data["airlines"]:
            airline_frame = ttk.LabelFrame(self.airline_result_frame, text="Airlines Operating at this Airport")
            airline_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Create treeview for airlines
            columns = ("name", "iata", "terminal")
            airlines_tree = ttk.Treeview(airline_frame, columns=columns, show="headings")

            # Define headings
            airlines_tree.heading("name", text="Airline Name")
            airlines_tree.heading("iata", text="IATA Code")
            airlines_tree.heading("terminal", text="Terminal(s)")

            # Set column widths
            airlines_tree.column("name", width=250)
            airlines_tree.column("iata", width=80)
            airlines_tree.column("terminal", width=100)

            # Add airlines
            for airline in data["airlines"]:
                airlines_tree.insert("", "end", values=(
                    airline["name"],
                    airline["iata"],
                    airline["terminal"]
                ))

            # Add scrollbar
            scrollbar = ttk.Scrollbar(airline_frame, orient="vertical", command=airlines_tree.yview)
            airlines_tree.configure(yscrollcommand=scrollbar.set)

            # Pack the treeview and scrollbar
            airlines_tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        else:
            ttk.Label(self.airline_result_frame,
                      text="No airline information available",
                      font=('Arial', 12)).pack(pady=10)


if __name__ == '__main__':
    WeatherApp()
