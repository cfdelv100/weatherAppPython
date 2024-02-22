from io import BytesIO

import config
import requests  # hit end points and gets weather data
import tkinter as tk
from tkinter import ttk, RIGHT, LEFT
from PIL import ImageTk, Image
import urllib.request

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
        icon = data['weather'][0]['icon']

        def create_text_window():
            new_window = tk.Toplevel(window)
            new_window.title("Weather")
            new_window.geometry('400x200')
            text_label = tk.Label(new_window, text=city_name_complete)
            text_label.pack()
            text_label2 = tk.Label(new_window, text=weather_complete)
            text_label2.pack()
            text_label3 = tk.Label(new_window, text=temperature_complete)
            text_label3.pack()
            icon2 = data['weather'][0]['id']
            icons_url = f"{config.ICON_BASE_URL}/{icon}@2x.png"

            response2 = urllib.request.urlopen(icons_url)
            response2.close()

            class WebImage:
                def __init__(self, url):
                    super().__init__()
                    u = requests.get(url)
                    self.image = ImageTk.PhotoImage(Image.open(BytesIO(u.content)))

                def get(self):
                    return self.image

            image = WebImage(icons_url).get()
            print(icon2)
            print(icon)
            if 200 <= icon2 <= 232:
                icon_display1 = tk.Label(new_window, image=image)
                icon_display1.image = image
                icon_display1.pack()
            if 300 <= icon2 <= 321:
                icon_display2 = tk.Label(new_window, image=image)
                icon_display2.image = image
                icon_display2.pack()
            if 500 <= icon2 <= 531:
                icon_display3 = tk.Label(new_window, image=image)
                icon_display3.image = image
                icon_display3.pack()
            if 600 <= icon2 <= 622:
                icon_display4 = tk.Label(new_window, image=image)
                icon_display4.image = image
                icon_display4.pack()
            if 701 <= icon2 <= 781:
                icon_display5 = tk.Label(master=new_window, image=image)
                icon_display5.image = image
                icon_display5.pack()
            if icon2 == 800:
                icon_display6 = tk.Label(new_window, image=image)
                icon_display6.image = image
                icon_display6.pack()
            if 801 <= icon2 <= 804:
                icon_display7 = tk.Label(master=new_window, image=image)
                icon_display7.image = image
                icon_display7.pack()

        #  label_one = tk.Label(window, text=str(["Location:", city_name, "\n"]))
        #  label_two = tk.Label(window, text=str(["Weather:", weather, "\n"]))
        #  label_three = tk.Label(window, text=str(["Temperature:", "The current temperature is: ", temperature, "celsius."]))
        #  label_one.place(x=60, y=100)
        #  label_two.place(x=60, y=150)
        #  label_three.place(x=60, y=200)
        button2 = tk.Button(window, text="Press Here to Pop Up Weather Window", command=lambda: create_text_window())
        button2.place(x=100, y=400)

        city_name_complete = "Location: " + city_name + "\n"
        weather_complete = "Weather: " + weather + "\n"
        temperature_complete = "Temperature: The current temperature is: " + str(temperature) + " celsius"
        create_text_window()

    if response.status_code == 404:
        print("Error occurred...")


# TODO: Icons need to be viewable for all backgrounds.


# button
button_string = tk.StringVar(value='Search for the Current Weather')
button = ttk.Button(window, text='Search', command=get_Entry_Value)
button.place(x=100, y=500)

# open window
window.mainloop()
