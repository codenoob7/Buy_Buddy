# sidebar.py
import customtkinter as ctk
from PIL import Image
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller unpacking path
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Sidebar:
    def __init__(self, master):
        self.master = master
        self.sidebar_expanded = False
        self.collapsed_width = 60
        self.expanded_width = 220
        self.animation_speed = 15

        self.sidebar_commands = {}

        self.sidebar_frame = ctk.CTkFrame(master, fg_color="#2D2D2D", width=self.collapsed_width)
        self.sidebar_frame.place(x=0, y=0, relheight=1.0)

        self.button_containers = []

        self.toggle_button = ctk.CTkButton(
            self.sidebar_frame, text="☰", command=self.toggle_sidebar,
            width=50, height=30, fg_color="transparent", hover_color="#444",
            text_color="white", font=("Arial", 18)
        )
        self.toggle_button.pack(pady=(15, 50), anchor="w", padx=10)

        self.frame_items = [
            (resource_path('Images/home.png'), 'HOME'),
            (resource_path("Images/search_method.png"), "SEARCH METHOD"),
            (resource_path("Images/notifier.png"), "NOTIFIER"),
            (resource_path("Images/chat.png"), "CHAT"),
            (resource_path("Images/wishlist.png"), "WISHLIST"),
            (resource_path("Images/setting.png"), "SETTING"),
            (resource_path("Images/about.png"), "ABOUT"),
            (resource_path("Images/logout.png"), "LOGOUT"),
        ]

        for img_path, text in self.frame_items:
            self.create_sidebar_button(img_path, text)

        self.hide_labels_initially()

    def load_icon(self, pth):
        img = Image.open(pth)
        return ctk.CTkImage(img, size=(26, 26))

    def create_sidebar_button(self, img_path, text):
        container = ctk.CTkFrame(self.sidebar_frame, fg_color="#2D2D2D")
        container.pack(fill="x", pady=25, padx=5)

        icon = self.load_icon(img_path)
        icon_label = ctk.CTkLabel(container, image=icon, text="", fg_color="transparent")
        icon_label.pack(side="left", padx=(10, 5), pady=5)

        text_label = ctk.CTkLabel(
            container, text=text, text_color="white",
            fg_color="transparent", font=("Arial", 16, 'bold')
        )
        text_label.pack(side="left", padx=(5, 10))
        self.button_containers.append((text_label, container))

        for widget in [container, icon_label, text_label]:
            widget.bind("<Enter>", lambda e, c=container: c.configure(fg_color="#656565"))
            widget.bind("<Leave>", lambda e, c=container: c.configure(fg_color="#2D2D2D"))
            widget.bind("<Button-1>", lambda e, t=text: self.on_button_click(t))

    def on_button_click(self, text):
        if not self.sidebar_expanded:
            self.toggle_sidebar()
        else:
            if text in self.sidebar_commands:
                self.sidebar_commands[text]()
                self.toggle_sidebar()
            else:
                print(f"{text} Clicked")


    def set_command(self, label_text, command_func):
        self.sidebar_commands[label_text] = command_func

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        target_width = self.expanded_width if self.sidebar_expanded else self.collapsed_width
        self.animate_sidebar(self.sidebar_frame.winfo_width(), target_width)

    def animate_sidebar(self, current, target):
        if abs(target - current) <= self.animation_speed:
            self.sidebar_frame.configure(width=target)
            self.update_label_visibility()
            return
        step = self.animation_speed if target > current else -self.animation_speed
        self.sidebar_frame.configure(width=current + step)
        self.sidebar_frame.after(10, lambda: self.animate_sidebar(current + step, target))

    def hide_labels_initially(self):
        for label, _ in self.button_containers:
            label.pack_forget()

    def update_label_visibility(self):
        if self.sidebar_expanded:
            for label, _ in self.button_containers:
                label.pack(side="left", padx=(5, 10))
        else:
            self.hide_labels_initially()

    def get_frame(self):
        return self.sidebar_frame
