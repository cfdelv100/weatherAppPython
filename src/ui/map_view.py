from io import BytesIO
import threading
from urllib.parse import urlencode

import requests
from tkinter import ttk

try:
    from PIL import Image, ImageTk
except ImportError:  # pragma: no cover - optional dependency in some environments
    Image = None
    ImageTk = None

from src import config


class MapView(ttk.Frame):
    def __init__(self, parent, title: str = "Location Map"):
        super().__init__(parent)
        self.title = title
        self.status_label = ttk.Label(self, text="Map rendering requires a Geoapify API key.")
        self.status_label.pack(fill="both", expand=True, padx=12, pady=12)
        self.image_label = None
        self.map_image = None

    def show_location(self, latitude: float, longitude: float, label: str, extent_padding: float = 18.0):
        del extent_padding

        for widget in self.winfo_children():
            widget.destroy()

        if not config.GEOAPIFY_API_KEY:
            self.status_label = ttk.Label(
                self,
                text=(
                    f"{self.title}\n{label}\n{latitude:.4f}, {longitude:.4f}\n"
                    "Set GEOAPIFY_API_KEY to display the map."
                ),
            )
            self.status_label.pack(fill="both", expand=True, padx=12, pady=12)
            return

        if Image is None or ImageTk is None:
            self.status_label = ttk.Label(self, text="Map rendering requires Pillow.")
            self.status_label.pack(fill="both", expand=True, padx=12, pady=12)
            return

        self.status_label = ttk.Label(self, text=f"Loading Geoapify map for {label}...")
        self.status_label.pack(fill="both", expand=True, padx=12, pady=12)

        def load_map():
            params = {
                "style": "osm-carto",
                "width": 640,
                "height": 360,
                "scaleFactor": 2,
                "center": f"lonlat:{longitude:.6f},{latitude:.6f}",
                "zoom": 11,
                "marker": f"lonlat:{longitude:.6f},{latitude:.6f}",
                "apiKey": config.GEOAPIFY_API_KEY,
            }
            map_url = f"{config.GEOAPIFY_STATIC_MAP_BASE_URL}?{urlencode(params)}"

            try:
                response = requests.get(map_url, timeout=15)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                photo = ImageTk.PhotoImage(image)
            except Exception as error:
                self.after(
                    0,
                    lambda: self._show_error(
                        label,
                        latitude,
                        longitude,
                        error,
                    ),
                )
                return

            self.after(0, lambda: self._display_map(photo))

        threading.Thread(target=load_map, daemon=True).start()

    def _display_map(self, photo):
        for widget in self.winfo_children():
            widget.destroy()
        self.map_image = photo
        self.image_label = ttk.Label(self, image=photo)
        self.image_label.pack(fill="both", expand=True)

    def _show_error(self, label, latitude, longitude, error):
        for widget in self.winfo_children():
            widget.destroy()
        self.status_label = ttk.Label(
            self,
            text=f"Unable to load Geoapify map.\n{label}\n{latitude:.4f}, {longitude:.4f}\n{error}",
        )
        self.status_label.pack(fill="both", expand=True, padx=12, pady=12)
