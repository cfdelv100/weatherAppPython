import config
import requests  # hit end points and gets weather data
import tkinter as tk
from tkinter import ttk, RIGHT, LEFT
from tkinter import messagebox


def search_weather():
    ttk.Label(window, text="Welcome to the Weather City App!").pack()
    # print("Welcome to the Weather City App!")
    # city = input("Enter a city name: ")
    label1 = ttk.Label(window, text="Enter City")
    label1.pack(side=LEFT)
    entry1 = ttk.Entry(window, font='Century 12', width=40)
    entry1.pack(side=RIGHT)

    def get_Entry_Value():
        e_text = entry1.get()
        requests_url = f"{config.BASE_URL}?appid={config.API_KEY}&q={e_text}"  # base url for query parameter which is a city
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

    button3 = ttk.Button(window, text="Enter", command=get_Entry_Value)
    button3.pack()


# TODO: Define implementation for the button to display responses. 
#  Implement and be sure only one window can be seen, implement messagebox.
def find_Weather():
    window1 = tk.Tk()
    window1.geometry('500x500')
    messagebox.askquestion("City", "Is this the city you want to submit")
    btn1 = ttk.Button(window1, text="City", command=lambda: find_Weather())
    btn1.pack()


def print_text(text):
    ttk.Label(window, text=text, font='Helvetica 13 bold').pack()


# window
window = tk.Tk()
window.title('Welcome to the Weather City App!')
window.geometry('600x400')

# button
button_string = tk.StringVar(value='Search for the Current Weather')
button = ttk.Button(master=window, text='Search', command=lambda: search_weather(),
                    textvariable=button_string)
button.pack()

# button2
button_string2 = tk.StringVar(value="Click Here to Enter a City!")
button2 = ttk.Button(master=window, text='Click here to Enter a City!', textvariable=button_string2,
                     command=lambda: find_Weather())
button2.pack()

# open window
window.mainloop()
