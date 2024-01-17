import config
import requests  # hit end points and gets weather data
import tkinter as tk
from tkinter import ttk, RIGHT, LEFT
from tkinter import messagebox

# window
window = tk.Tk()
window.title('Welcome to the Weather City App!')
window.geometry('400x640')

ttk.Label(window, text="Welcome to the Weather City App!").pack()
label1 = ttk.Label(window, text="Enter City")
label1.pack(side=LEFT)
entry1 = ttk.Entry(window, font='Century 12', width=40)
entry1.pack(side=RIGHT)


def get_Entry_Value():
    global var1, var2, var3, labels, city_name, weather, temperature, mes1, mes2, mes3, create_text_window

    e_text = entry1.get()
    requests_url = f"{config.BASE_URL}?appid={config.API_KEY}&q={e_text}"  # base url for query parameter which is a city
    response = requests.get(requests_url)  # get request for URL
    if response.status_code == 200:
        data = response.json()
        city_name = data['name']
        weather = data['weather'][0]['description']
        temperature = round(data["main"]["temp"] - 273.15, 2)

        city_name_complete = "Location: " + city_name + "\n"
        weather_complete = "Weather: " + weather + "\n"
        temperature_complete = "Temperature: The current temperature is: " + str(temperature) + " celsius"

    if response.status_code == 404:
        print("Error occurred...")

    def create_text_window():
        new_window = tk.Toplevel(window)
        new_window.title("Weather")
        text_label = tk.Label(new_window, text=city_name_complete)
        text_label.pack()
        text_label2 = tk.Label(new_window, text=weather_complete)
        text_label2.pack()
        text_label3 = tk.Label(new_window, text=temperature_complete)
        text_label3.pack()

    label_one = tk.Label(window, text=str(["Location:", city_name, "\n"]))
    label_two = tk.Label(window, text=str(["Weather:", weather, "\n"]))
    label_three = tk.Label(window, text=str(["Temperature", "The current temperature is: ", temperature, "celsius"]))
    label_one.place(x=60, y=100)
    label_two.place(x=60, y=150)
    label_three.place(x=60, y=200)

    button2 = tk.Button(window, text="Press Here to Pop Up Weather Window", command=lambda: create_text_window())
    button2.place(x=100, y=400)


# TODO: Add icons via API into both windows, Implement more results from weatherAPI.


# button
button_string = tk.StringVar(value='Search for the Current Weather')
button = ttk.Button(window, text='Search', command=get_Entry_Value)
button.place(x=100, y=500)

# open window
window.mainloop()
