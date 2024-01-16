import config
import requests  # hit end points and gets weather data
import tkinter as tk
from tkinter import ttk, RIGHT, LEFT
from tkinter import messagebox


# window
window = tk.Tk()
window.title('Welcome to the Weather City App!')
window.geometry('800x800')

ttk.Label(window, text="Welcome to the Weather City App!").pack()
label1 = ttk.Label(window, text="Enter City")
label1.pack(side=LEFT)
entry1 = ttk.Entry(window, font='Century 12', width=40)
entry1.pack(side=RIGHT)


def get_Entry_Value():
    global var1, var2, var3, labels, city_name, weather, temperature, mes1, mes2, mes3

    e_text = entry1.get()
    requests_url = f"{config.BASE_URL}?appid={config.API_KEY}&q={e_text}"  # base url for query parameter which is a city
    response = requests.get(requests_url)  # get request for URL
    if response.status_code == 200:
        data = response.json()
        city_name = data['name']
        weather = data['weather'][0]['description']
        temperature = round(data["main"]["temp"] - 273.15, 2)

    if response.status_code == 404:
        print("Error occurred...")

    label_one = tk.Label(window, text=str(["Location:", city_name, "\n"]))
    label_two = tk.Label(window, text=str(["Weather:", weather, "\n"]))
    label_three = tk.Label(window, text=str(["Temperature", "The current temperature is: ", temperature, "celsius"]))
    label_one.place(x=200, y=400)
    label_two.place(x=200, y=450)
    label_three.place(x=200, y=500)


# TODO: Turn JSON like formatting into just strings, and improve UI.


# button
button_string = tk.StringVar(value='Search for the Current Weather')
button = ttk.Button(window, text='Search', command=get_Entry_Value)
button.pack()

# open window
window.mainloop()
