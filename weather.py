import config
import requests  # hit end points and gets weather data
import tkinter as tk
from tkinter import ttk


def search_weather():
    print("Welcome to the Weather City App!")
    city = input("Enter a city name: ")
    requests_url = f"{config.BASE_URL}?appid={config.API_KEY}&q={city}"  # base url for query parameter which is a city
    response = requests.get(requests_url)  # get request for URL

    if response.status_code == 200:
        data = response.json()
        city_name = data['name']
        weather = data['weather'][0]['description']
        temperature = round(data["main"]["temp"] - 273.15, 2)
        print("Location:", city_name, "\n"
              "Weather:", weather, "\n"
              "The current temperature is: ", temperature, "celsius")
    if response.status_code == 404:
        print("Error occurred...")


# window
window = tk.Tk()
window.title('Welcome to the Weather City App!')
window.geometry('600x400')

# button
button_string = tk.StringVar(value='Search for the Current Weather')
button = ttk.Button(master=window, text='Search', command=lambda: search_weather(),
                    textvariable=button_string)
button.pack()
# TODO: Add implementation for the buttons to allow input from user and respond with the search_weather() function.
# button2
button_string2 = tk.StringVar(value="Click Here to Enter a City!")
button2 = ttk.Button(master=window, text='Click here to Enter a City!', textvariable=button_string2)
button2.pack()

# open window
window.mainloop()
