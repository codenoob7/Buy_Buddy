import customtkinter
import pyglet
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

pyglet.font.add_file(resource_path('Fonts/SourceSans3-VariableFont_wght.ttf'))

class BudgetPopup(ctk.CTkToplevel):
    def __init__(self, master,product_data: dict,in_wishlist,on_add_callback=None):
        self.master = master
        self.product_data = product_data
        self.on_add_callback = on_add_callback
        self.in_wishlist = in_wishlist

        # Create overlay FIRST
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.5)
        self.overlay.configure(fg_color="black")
        self.overlay.bind("<Button-1>", self.on_overlay_click)

        # THEN create the popup
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("500x350")
        self.configure(fg_color="#757575")

        # Now ensure popup is above overlay
        self.lift()
        self.focus_force()

        self.slider_min,self.slider_max,self.step_count = (
            self.calculate_budget_for_slider(self.product_data.get('price',0)))

        self.create_popup()
        self.update_overlay_position()
        self.master.bind("<Configure>", self.update_overlay_position)
        self.after(100, self.on_resize)


    def calculate_budget_for_slider(self,price):
        if price <= 1000:
            slider_min = max(0, price - 600)   # 60% drop
        elif price <= 3000:
            slider_min = int(price * 0.5)      # 50% drop
        elif price <= 10000:
            slider_min = int(price * 0.35)    # 65% drop
        elif price <= 20000:
            slider_min = int(price * 0.3)     # 70% drop
        else:
            slider_min = int(price * 0.25)    # 75% drop

        slider_max = price

        # Dynamically choose step count based on price range
        price_range = slider_max - slider_min
        if price_range <= 1000:
            steps = price_range // 50
        elif price_range <= 5000:
            steps = price_range // 100
        elif price_range <= 10000:
            steps = price_range // 250
        else:
            steps = price_range // 500

        steps = max(1, steps)  # Avoid 0

        return slider_min, slider_max, steps

    def create_overlay(self):
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.5)
        self.overlay.configure(fg_color='black')
        self.overlay.bind("<Button-1>",self.on_overlay_click)

    def create_popup(self):
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("500x350")
        self.configure(fg_color="#757575")

        self.popup_frame = ctk.CTkFrame(self, corner_radius=30, fg_color='#00AC98',
                                        bg_color='transparent', border_width=3, border_color='white')
        self.popup_frame.place(x=0, y=0, relwidth=1, relheight=1)
        txt = 'RESET BUDGET' if self.in_wishlist else 'SET YOUR BUDGET'
        ctk.CTkLabel(self.popup_frame, text=txt,
                     text_color='white',font=("Arial", 25, "bold")).pack(pady=(15, 15))

        self.slider_label = ctk.CTkLabel(self.popup_frame, text="", text_color='white',
                                         font=("SourceSans3", 16, "bold"))
        self.slider_label.place(x=0, y=0)

        self.slider = ctk.CTkSlider(self.popup_frame, from_=self.slider_min, to=self.slider_max,
                                    number_of_steps=self.step_count, height=30,
                                    fg_color='white', progress_color='#06E5C3',
                                    button_color='#D9D9D9', button_hover_color='#00665F',
                                    command=self.update_slider_label)
        self.slider.set((self.slider_min + self.slider_max) // 2)
        self.slider.pack(pady=(50, 10), fill="x", padx=80)

        self.add_btn = ctk.CTkButton(self.popup_frame, text="Add Product",
                                     fg_color="#2D2D2D", width=170, height=45,
                                     font=("SourceSans3", 19, "bold"),
                                     corner_radius=10, border_width=0,
                                     hover_color='#656565', text_color="white",
                                     command=self.on_add_product)
        self.add_btn.pack(pady=(25, 15))

        self.info_frame = ctk.CTkFrame(self.popup_frame, fg_color="transparent")
        self.info_frame.pack(fill='x', anchor='center', pady=25, padx=10)

        info_img = Image.open(resource_path('Images/info.png')).resize((50, 50), Image.LANCZOS)
        info_img = ctk.CTkImage(info_img, size=info_img.size)

        self.icon = ctk.CTkLabel(self.info_frame, image=info_img, text='')
        self.icon.grid(row=0, column=0, sticky="w", padx=(20, 5))
        self.text_label = ctk.CTkLabel(self.info_frame, text='You’ll be notified via mail, when product price comes in your budget.',
                     font=("SourceSans3", 16, "bold"), text_color='white',
                     wraplength=400, justify='left')
        self.text_label.grid(row=0, column=1, sticky="w", padx=5)

    def update_slider_label(self, value):
        value = int(float(value))
        self.slider_label.configure(text=f"₹{value}")
        rel_x = (value - self.slider_min) / (self.slider_max - self.slider_min)
        slider_width = self.slider.winfo_width()
        if slider_width > 0:
            x_pos = self.slider.winfo_x() + int(slider_width * rel_x)
            self.slider_label.place(x=x_pos - 20, y=self.slider.winfo_y() - 35)

    def on_resize(self, event=None):
        self.update_slider_label(self.slider.get())

    def update_overlay_position(self, event=None):
        if self.overlay.winfo_exists() and self.master.winfo_exists():
            self.overlay.geometry(f"{self.master.winfo_width()}x{self.master.winfo_height()}+"
                                  f"{self.master.winfo_rootx()}+{self.master.winfo_rooty()}")
        if self.winfo_exists():
            x = self.master.winfo_rootx() + (self.master.winfo_width() - 400) // 2 - 50
            y = self.master.winfo_rooty() + (self.master.winfo_height() - 200) // 2 - 100
            self.geometry(f"+{x}+{y}")

    def on_overlay_click(self, event):
        clicked = self.overlay.winfo_containing(event.x_root, event.y_root)
        if not self.is_descendant(self, clicked):
            self.close()

    def is_descendant(self, parent, widget):
        while widget:
            if widget == parent:
                return True
            widget = widget.master
        return False

    def on_add_product(self):
        budget_value = int(self.slider.get())
        result = {**self.product_data, 'budget': budget_value}
        if self.on_add_callback:
            self.on_add_callback(result)
        self.show_success()
        self.after(2000,self.close)

    def show_success(self):
        for widget in self.popup_frame.winfo_children():
            if widget != self.info_frame:
                widget.destroy()

        done_img = Image.open(resource_path('Images/done.png')).resize((60, 60), Image.LANCZOS)
        done_img = ctk.CTkImage(done_img, size=done_img.size)
        self.icon.configure(image=done_img)
        self.icon.image = done_img
        self.geometry('600x120')

        self.text_label.configure(text='Product is successfully added to your Wishlist.',
                                  text_color='white',
                                  font=("SourceSans3", 20, "bold"),
                                  wraplength=400, justify='left')

    def close(self):
        if self.overlay.winfo_exists():
            self.overlay.destroy()
        if self.winfo_exists():
            self.destroy()
        self.master.unbind("<Configure>")
