import random
import shutil
from multiprocessing import Process
import webbrowser
import customtkinter as ctk
from PIL import Image
import pyglet
import threading
import pandas as pd
from urllib.request import urlopen
import io
import sys
import os
import json

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller unpacking path
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pyglet.font.add_file(resource_path("Fonts/JetbrainsMonoRegular-RpvmM.ttf"))
pyglet.font.add_file(resource_path('Fonts/SourceSans3-VariableFont_wght.ttf'))

#Global variables
current_screen = None
search_text = None
search_index = None     #Highest Rated=1 or Budget Friendly=2 or Premium=3

PRODUCTS_JSON_PATH = os.path.join("data", "product_data.json")
os.makedirs('data', exist_ok=True)

def load_or_initialize_product_data():
    if os.path.exists(PRODUCTS_JSON_PATH):
        try:
            with open(PRODUCTS_JSON_PATH, "r") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
                else:
                    print("⚠️ JSON structure is invalid. Initializing empty dictionary.")
        except json.JSONDecodeError:
            print("⚠️ JSON decode error. Initializing empty dictionary.")
    else:
        print("ℹ️ JSON file not found. Creating a new one.")

    # Initialize empty dict if file doesn't exist or is invalid
    empty_data = {'products': []}
    with open(PRODUCTS_JSON_PATH, "w") as file:
        json.dump(empty_data, file, indent=4)
    return empty_data

product_details = load_or_initialize_product_data()

def show_frame(frame):
    global current_screen

    #Hide all other frames
    for widget in app.winfo_children():
        if isinstance(widget, ctk.CTkFrame):
            widget.pack_forget()
    #Show the selected Frame
    frame.pack(fill="both", expand=True)
    current_screen = frame


def empty_directory(path):
    if os.path.exists(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)     #for file or link deletion
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)       #for folder deletion
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        print("Directory doesn't exist")


#-------------------------------------Screens in App-----------------------------------------

def create_loader(show_text):
    # Create loading frame
    loading_frame = ctk.CTkFrame(app, fg_color="#00AB98")
    loading_frame.place(x=0, y=0, relwidth=1, relheight=1)
    loading_frame.is_loading_frame = True  # Tag it

    original_img = Image.open(resource_path("Images/loader.png")).resize((80, 80))
    angle = [0]

    img = ctk.CTkImage(original_img, size=original_img.size)
    loader_label = ctk.CTkLabel(loading_frame, text="", image=img, fg_color='transparent')
    loader_label.image = img
    loader_label.place(relx=0.5, rely=0.5, anchor="center")

    if show_text:
        loader_text = ctk.CTkLabel(loading_frame,
                                   text="Buddy is getting the best for you...",
                                   font=('JetBrains Mono', 30),
                                   text_color="white",
                                   fg_color='transparent')
        loader_text.place(relx=0.5, rely=0.58, anchor="center")

        texts = ['Please Wait...', 'Buddy is getting the best for you...', 'Almost Done...']

        def change_text():
            loader_text.configure(text=texts[random.randint(0, len(texts) - 1)])
            loading_frame.after(2000, change_text)

        change_text()

    def rotate_loader():
        rotated = original_img.rotate(angle[0])
        ctk_rotated = ctk.CTkImage(rotated, size=rotated.size)
        loader_label.configure(image=ctk_rotated)
        loader_label.image = ctk_rotated
        angle[0] = (angle[0] + 10) % 360
        loader_label.after(50, rotate_loader)

    rotate_loader()

    navigation.get_frame().lift()

    return loading_frame

#This is just for the comparing purpose, don't use this it'll run sequentially which takes time.
#Instead, Use Multi Processing
# def run_scrapers_queue(q,p):
#     from scripts import flipkart_scrapper
#     from scripts import croma_scrapper
#     from scripts import vijaysales_scrapper
#     from scripts import reliance_scrapper
#
#     flipkart_scrapper.run_scraper(q,p)
#     croma_scrapper.run_scraper(q)
#     vijaysales_scrapper.run_scraper(q)
#     reliance_scrapper.run_scraper(q)
#
#     paths = [f'CSV_Dataset/{q}_Flipkart.csv',
#              f'CSV_Dataset/{q}_Croma.csv',
#              f'CSV_Dataset/{q}_VijaySales.csv',
#              f'CSV_Dataset/{q}_Reliance.csv']
#
#     while not all(os.path.exists(p) for p in paths):
#         time.sleep(0.1)

#Run Simultaneously all the scrapers to get all the products speedily
def run_scrapers_simultaneously(q,hardcore):
    from scripts.flipkart_scrapper import run_scraper as scrap_flipkart
    from scripts.croma_scrapper import run_scraper as scrap_croma
    from scripts.vijaysales_scrapper import run_scraper as scrap_vijay_sales
    from scripts.reliance_scrapper import run_scraper as scrap_reliance

    scrapers = [
        (scrap_flipkart,(q,hardcore)),
        (scrap_croma,(q,)),
        (scrap_vijay_sales,(q,)),
        (scrap_reliance,(q,))
    ]

    processes = []
    for func, args in scrapers:
        p = Process(target=func, args=args)
        p.daemon = True
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
        print("Scraper processes were forcefully terminated.")

def show_loading_and_wait():
    #1.Show Loading Screen
    loading_screen = create_loader(True)

    def run_scrapper():
        # Get the Data From the Scrapper
        query = str(search_text).lower()
        hardcore_search = False

        # run_scrapers_queue(query,pages)
        run_scrapers_simultaneously(query,hardcore_search)

        app.after(0,lambda : show_result_screen(loading_screen))

    #2.Start Background Task
    threading.Thread(target=run_scrapper,daemon=True).start()

def show_result_screen(loader_frame):
    def background_task():
        search_txt = str(search_text).lower()
        dataset = get_data_from_csv(search_txt)

        def build_ui():
            loader_frame.destroy()  # ✅ reuse & destroy original loader
            create_search_result_frame(dataset, search_txt)

        app.after(0, build_ui)

    threading.Thread(target=background_task, daemon=True).start()


def show_loading_only(delay,target_frame):
    print('Back Clicked')
    for widget in app.winfo_children():
        if isinstance(widget, ctk.CTkFrame) and getattr(widget, "is_loading_frame", False):
            return  # Already loading, do nothing

    loading_screen = create_loader(False)
    loading_screen.after(delay*1000,lambda: (
        loading_screen.destroy(),
        show_frame(home_screen),
        reset_home_screen()
    ))

def reset_home_screen():
    global loaded
    loaded = 0
    home_screen.search_entry.delete(0, "end")
    home_screen.var.set(1)

def create_home_screen():
    home_frame = ctk.CTkFrame(app,fg_color='#00AB98')
    home_frame.place(x=0, y=0, relwidth=1, relheight=1)

    # ------------------ Search Frame ------------------
    search_frame = ctk.CTkFrame(home_frame, width=1080, height=650,fg_color='#00AB98')
    search_frame.place(relx=0.5, rely=0.4, anchor="center")
    search_frame.pack_propagate(False)

    # Search Logo
    s_logo_img = Image.open(resource_path("Images/search_blogo.png"))
    s_logo_img = ctk.CTkImage(s_logo_img, size=(305, 181))
    s_logo_label = ctk.CTkLabel(search_frame, image=s_logo_img, text="")
    s_logo_label.pack(pady=(150, 20))

    # ------------------ Search Bar ------------------

    search_bar_frame = ctk.CTkFrame(search_frame, fg_color="#00AB98")
    search_bar_frame.pack(pady=10)

    # Search Icon
    s_icon_img = Image.open(resource_path("Images/b_icon.png"))
    s_icon_img = ctk.CTkImage(s_icon_img, size=(58, 59))
    s_icon_label = ctk.CTkLabel(search_bar_frame, image=s_icon_img, text="")
    s_icon_label.pack(side="left")

    # Entry and Button
    entry_frame = ctk.CTkFrame(search_bar_frame, fg_color="#ECEEEC", width=700, height=50, corner_radius=0)
    entry_frame.pack()
    entry_frame.pack_propagate(False)

    search_img = Image.open(resource_path("Images/search_icon.png"))
    search_img = ctk.CTkImage(search_img)
    search_icon = ctk.CTkLabel(entry_frame, image=search_img, text="", bg_color="#ECEEEC")
    search_icon.pack(side="left", padx=(10, 5))

    home_frame.search_entry = ctk.CTkEntry(entry_frame,
                                placeholder_text="Search for Products, Brands and More",
                                font=("JetBrains Mono", 16),
                                fg_color="#ECEEEC",
                                border_width=0,
                                text_color="black",
                                width=480)
    home_frame.search_entry.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=10)


    #------------------------Radio Buttons-----------------------
    selection_frame = ctk.CTkFrame(search_frame,fg_color="transparent")
    selection_frame.pack(pady=20)

    home_frame.var = ctk.IntVar(value=1)
    ctk.CTkRadioButton(selection_frame,
                      text='Highest Rated',
                      font=("JetBrains Mono", 16, "bold"),
                      text_color='white',
                       fg_color='white',
                      variable=home_frame.var,
                      value=1).grid(row=0, column=0, padx=20, pady=10)
    ctk.CTkRadioButton(selection_frame,
                       text='Budget Friendly',
                       font=("JetBrains Mono", 16, "bold"),
                       text_color='white',
                       fg_color='white',
                       variable=home_frame.var,
                       value=2).grid(row=0, column=1, padx=20, pady=10)
    ctk.CTkRadioButton(selection_frame,
                       text='Premium One',
                       font=("JetBrains Mono", 16, "bold"),
                       text_color='white',
                       fg_color='white',
                       variable=home_frame.var,
                       value=3).grid(row=0, column=2, padx=20, pady=10)

    # Search Button
    home_frame.search_button = ctk.CTkButton(search_frame,
                                  text="Search",
                                  width=200,
                                  height=50,
                                  font=("JetBrains Mono", 25, "bold"),
                                  fg_color="#2EE4C2",
                                  hover_color="#1CC1A1",
                                  text_color="white",
                                  corner_radius=10,
                                  command=lambda : (set_search_text_and_index(home_frame.search_entry,home_frame.var.get()),search_the_products()))
    home_frame.search_button.pack(anchor='center', pady=(30, 10))

    navigation.get_frame().lift()

    return home_frame

def home_button_pressed():
    if current_screen == home_screen:
        print('Already home screen')
        return
    else:
        show_loading_only(2,home_screen)

def set_search_text_and_index(entry,index):
    global search_text
    global search_index
    search_text = entry.get()
    search_index = index

def search_the_products():
    query = search_text
    if query == '' or len(str(query)) < 3:
        pass
    else:
        csv_path = f'Saved CSVs/{query}_Combined.csv'
        if os.path.exists(csv_path):
            print('Exists...')
            loading_frame = create_loader(True)
            # dataset = pd.read_csv(f'Saved CSVs/{query}_Combined.csv')
            dataset = pd.read_csv(csv_path)
            loading_frame.after(3000,lambda: (create_search_result_frame(dataset,query),loading_frame.destroy()))

        else:
            show_loading_and_wait()

def create_search_result_frame(dataset,search_txt):
    search_result_frame = ctk.CTkFrame(app, fg_color="#00AB98")
    search_result_frame.place(x=0,y=0,relwidth=1, relheight=1)

    search_result_frame.grid_rowconfigure(2, weight=1)  # Row 1: data_frame should expand vertically
    search_result_frame.grid_columnconfigure(0, weight=1)  # Column 0: allow horizontal stretch

    add_searchbar_in_taskbar(search_result_frame)

    search_txt = search_txt.lower()
    search_text_frame = ctk.CTkFrame(search_result_frame, fg_color='#EBEDEA',corner_radius=25)
    search_text_frame.grid(row=1,column=0,padx=20,pady=20)
    ctk.CTkLabel(search_text_frame,
                 text=f"SEARCH RESULT: '{search_txt}'",
                 fg_color="transparent",
                 text_color='#202B3F',
                 font=('SourceSans3', 25, 'bold'), ).pack(anchor="center", pady=10,padx=10)

    data_frame = ctk.CTkScrollableFrame(search_result_frame, fg_color="white",border_width=2,border_color='#E2E2E2')
    data_frame.grid(row=2,column=0,padx=(200,200),pady=10,sticky='nsew')


    def fast_scroll(event):
        data_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 0.8)), "units")  # Tune 1 as needed

    # Bind mousewheel to increase scroll speed
    data_frame._parent_canvas.bind_all("<MouseWheel>", fast_scroll)

    data_frame.pack_propagate(False)
    data_frame.grid_columnconfigure(0, weight=1)


    load_products(data_frame,dataset)

    show_frame(search_result_frame)
    navigation.get_frame().lift()


def get_data_from_csv(query):
    #Getting Data From CSV
    dataset = None
    sources = ['Flipkart', 'Croma', 'VijaySales', 'Reliance']
    csv_dir = 'CSV_Dataset'
    dataframes = []

    for source in sources:
        file_path = os.path.join(csv_dir,f'{query}_{source}.csv')
        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
            try:
                df = pd.read_csv(file_path)
                dataframes.append(df)
            except pd.errors.EmptyDataError:
                print(f"{file_path} is empty. Skipping.")
        else:
            print(f"{file_path} not found or empty. Skipping.")

    combined_data = pd.concat(dataframes, ignore_index=True)
    empty_directory(csv_dir)
    combined_data.to_csv(f'Saved CSVs/{query}_Combined.csv', index=False)
    index = search_index
    match index:
        # ------------------------Highest Rated-----------------------
        case 1:
            combined_data['Rating'] = pd.to_numeric(combined_data['Rating'], errors='coerce')
            dataset = combined_data.sort_values('Rating', ascending=False).reset_index(drop=True)

        # ------------------------Budget Friendly-----------------------
        case 2:
            combined_data['Price'] = combined_data['Price'].fillna(0)
            combined_data['Price'] = combined_data['Price'].apply(format_inr)
            dataset = combined_data.sort_values('Price', ascending=True).reset_index(drop=True)
            dataset['Price'] = dataset['Price'].apply(lambda x: f'{x:,}')

        # ------------------------Premium One-----------------------
        case 3:
            combined_data['Price'] = combined_data['Price'].apply(format_inr)
            dataset = combined_data.sort_values('Price', ascending=False).reset_index(drop=True)
            dataset['Price'] = dataset['Price'].apply(lambda x: f'{x:,}')

    return dataset

def format_inr(price_str):
    try:
        value = int(price_str.replace(',', ''))
        # return f'{value:,}'
        return value
    except:
        return price_str


loaded = 0
current_page = 0
def load_products(parent_frame,dataset):
    global current_page
    PRODUCTS_PER_PAGE = 10

    # Clear all product UI except buttons
    for child in parent_frame.winfo_children():
        widget_info = child.grid_info()
        if int(widget_info.get('row', -1)) < 1000:  # Only destroy product rows (below 1000)
            child.destroy()

    parent_frame._parent_canvas.yview_moveto(0)

    def create_product_ui(index,row_num):

        if index >= len(dataset['Title']):
            print('Index out of range')
            return

        product_frame = ctk.CTkFrame(parent_frame, fg_color='white', border_width=2, border_color='#E2E2E2', width=900,
                                     height=225)
        product_frame.grid(row=row_num, column=0, padx=5, pady=5, sticky='ew')
        product_frame.grid_propagate(False)

        image_frame = ctk.CTkFrame(product_frame, width=200, height=200, fg_color='white')
        image_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10)
        image_frame.propagate(False)

        def load_image():
            img = get_image_from_link(dataset['Image-Link'][index])
            if img:
                app.after(0, lambda: (
                    ctk.CTkLabel(image_frame, text='', image=img).place(relx=0.5, rely=0.5, anchor='center')))

        threading.Thread(target=load_image, daemon=True).start()

        # Product Info
        info_frame = ctk.CTkFrame(product_frame, fg_color='white')
        info_frame.grid(row=0, column=1, sticky='w', pady=10, padx=10)
        title = dataset['Title'][index]
        rating = dataset['Rating'][index]
        price = dataset['Price'][index]
        platform = dataset['Platform'][index]
        link = dataset['Link'][index]
        avl = dataset['Available'][index]

        data_dict = {
            'name': title,
            'rating': rating,
            'price': format_inr(price),
            'url': link,
            'availability': avl,
            'platform': platform,
        }

        # Add product text info
        # title
        ctk.CTkLabel(info_frame,
                     text=title,
                     font=('SourceSans3', 22),
                     text_color='#202B3F').grid(row=0, column=0, sticky='w', padx=5, pady=(5, 5))

        # rating
        rating_frame = ctk.CTkFrame(info_frame, fg_color='#FFD900', width=100, height=30, corner_radius=7)
        rating_frame.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        star_img = Image.open(resource_path('Images/star.png'))
        star_img = ctk.CTkImage(star_img, size=star_img.size)
        ctk.CTkLabel(rating_frame, text='', image=star_img).grid(row=0, column=0, sticky='w', padx=(10, 2), pady=1)
        ctk.CTkLabel(rating_frame, text=rating, font=('SourceSans3', 18), text_color='#575D5E').grid(row=0, column=1,
                                                                                                     sticky='w',
                                                                                                     padx=(2, 10),
                                                                                                     pady=1)

        # Price
        ctk.CTkLabel(info_frame, text=f'Rs.{price}', font=('SourceSans3', 26, 'bold'), text_color='black').grid(row=2,
                                                                                                                column=0,
                                                                                                                sticky='w',
                                                                                                                padx=5,
                                                                                                                pady=(5,
                                                                                                                      5))

        # Availability
        ctk.CTkLabel(info_frame, text=f'{avl}', font=('SourceSans3', 18), text_color='#0FC306').grid(row=3, column=0,
                                                                                                     sticky='w', padx=5,
                                                                                                     pady=(5, 0))

        # Platform Link
        last_frame = ctk.CTkFrame(info_frame, fg_color='transparent')
        last_frame.grid(row=4, column=0, padx=5, pady=5, sticky='w')

        link_frame = ctk.CTkFrame(last_frame, fg_color='#10867E', corner_radius=7)
        link_frame.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        click_img = Image.open(resource_path('Images/click.png'))
        click_img = ctk.CTkImage(click_img, size=click_img.size)
        link_img = (ctk.CTkLabel(link_frame, text='', image=click_img))
        link_img.grid(row=0, column=0, sticky='w', padx=(10, 2), pady=5)
        platform_name = ctk.CTkLabel(link_frame, text=platform, font=('SourceSans3', 18), text_color='white')
        platform_name.grid(row=0, column=1, sticky='w', padx=(2, 10), pady=5)
        # For link_frame hover and click
        for frame in [link_frame, link_img, platform_name]:
            frame.bind("<Enter>", lambda e: link_frame.configure(fg_color='#0C955A'))
            frame.bind('<Leave>', lambda e: link_frame.configure(fg_color='#10867E'))
            frame.bind('<Button-1>', lambda e: open_link(link))

        # Add to wishlist
        wish_frame = ctk.CTkFrame(last_frame, fg_color='#2D2D2D', corner_radius=7)
        wish_frame.grid(row=0, column=1, padx=20, pady=5, sticky='w')
        like_img = Image.open(resource_path('Images/like.png'))
        like_img = ctk.CTkImage(like_img, size=like_img.size)
        wish_img = ctk.CTkLabel(wish_frame, text='', image=like_img)
        wish_img.grid(row=0, column=0, sticky='w', padx=(10, 2), pady=5)
        wish_text = ctk.CTkLabel(wish_frame, text='Add to Wishlist', font=('SourceSans3', 18), text_color='white')
        wish_text.grid(row=0, column=1, sticky='w', padx=(2, 10), pady=5)

        def check_islisted():
            for i,data in enumerate(product_details['products']):
                if data['name'] == title:
                    return i,True
            return False

        def set_in_wishlist():
            wish_frame.configure(fg_color='#DE1B35')
            tick_img = Image.open(resource_path('Images/done.png')).resize((20, 20), Image.LANCZOS)
            tick_img = ctk.CTkImage(tick_img, size=tick_img.size)
            wish_img.configure(image=tick_img)
            wish_text.configure(text='Wishlisted')
            bind_hover('#DE1B35', '#FF0022')

        def bind_hover(f_color,h_color):
            # # For wish_frame hover and click
            for frame in [wish_frame, wish_img, wish_text]:
                frame.bind('<Enter>', lambda e: wish_frame.configure(fg_color=h_color))
                frame.bind('<Leave>', lambda e: wish_frame.configure(fg_color=f_color))

        def bind_click():
            for frame in [wish_frame,wish_img,wish_text]:
                frame.bind('<Button-1>', lambda e: open_budget_popup(data_dict,check_islisted(),set_in_wishlist))

        if check_islisted():
            set_in_wishlist()
            bind_click()
        else:
            bind_hover('#2D2D2D', '#656565')
            bind_click()


    def go_to_page(delta):
        global current_page
        new_page = current_page + delta
        max_page = (len(dataset['Title']) - 1) // PRODUCTS_PER_PAGE
        if 0 <= new_page <= max_page:
            current_page = new_page
            load_products(parent_frame, dataset)

    # Create navigation buttons
    def create_nav_buttons():
        nav_frame = ctk.CTkFrame(parent_frame, fg_color='white')
        nav_frame.grid(row=1000, column=0, pady=(10, 10))

        if current_page > 0:
            ctk.CTkButton(nav_frame, text="Previous", width=150,height=45,
                          fg_color='#2D2D2D',hover_color='#656565',font=('SourceSans3', 18, 'bold'),
                          command=lambda: go_to_page(-1)).pack(side='left',padx=20,pady=10)

        if (current_page + 1) * PRODUCTS_PER_PAGE < len(dataset['Title']):
            ctk.CTkButton(nav_frame, text="Next", width=150,height=45,
                          fg_color='#2D2D2D',hover_color='#656565', font=('SourceSans3', 18, 'bold'),
                          command=lambda: go_to_page(1)).pack(side='right',padx=20,pady=10)

    # Calculate start and end index for this page
    start = current_page * PRODUCTS_PER_PAGE
    end = min(start + PRODUCTS_PER_PAGE, len(dataset['Title']))

    for i,idx in enumerate(range(start, end)):
        create_product_ui(idx, i)

    # Remove old nav buttons before creating new ones
    for child in parent_frame.winfo_children():
        widget_info = child.grid_info()
        if int(widget_info.get('row', -1)) == 1000:
            child.destroy()

    create_nav_buttons()


from scripts.budget_popup import BudgetPopup
def open_budget_popup(product_data,in_wishlist,func_on_add):
    def on_add(data):
        #Delete the existing data
        if in_wishlist:
            del product_details['products'][in_wishlist[0]]
        func_on_add()
        print('Product Added: ')
        product_details['products'].append(data)

        with open(PRODUCTS_JSON_PATH,'w') as json_file:
            json.dump(product_details, json_file,indent=4)

    BudgetPopup(app, product_data,in_wishlist, on_add_callback=on_add)

def add_searchbar_in_taskbar(parent_frame):
    # Adding searchbar in the middle of taskbar
    search_entry_frame = ctk.CTkFrame(parent_frame, fg_color='#EBEDEA')
    search_entry_frame.grid(row=0, column=0, padx=100, pady=10, sticky='ew')
    s_icon = Image.open(resource_path('Images/search_icon.png'))
    s_icon = ctk.CTkImage(s_icon, size=s_icon.size)
    ctk.CTkLabel(search_entry_frame, text='',
                 image=s_icon,
                 fg_color="transparent").grid(row=0, column=0, padx=10, pady=5)
    search_entry_frame.grid_columnconfigure(1, weight=1)
    search_entry = ctk.CTkEntry(search_entry_frame,
                                        placeholder_text="Search for Products, Brands and More",
                                        font=("JetBrains Mono", 16),
                                        fg_color="#EBEDEA",
                                        border_width=0,
                                        height=40,
                                        text_color="black")
    search_entry.grid(row=0, column=1, padx=10, pady=5, sticky='nsew')


def open_link(url):
    webbrowser.open(url)

def get_image_from_link(link):
    try:
        url = urlopen(link).read()
        image = Image.open(io.BytesIO(url)).convert("RGBA")  # Ensure it's in the right format
        image.thumbnail((180, 180), Image.Resampling.LANCZOS)
        photo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
        return photo
    except Exception as e:
        print("Image load error:", e)
        return None

from scripts.navigation_sidebar import Sidebar
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()  # Needed for Windows .exe

    # Run the App
    # App setup
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")  # or "blue", "dark-blue"

    app = ctk.CTk()
    app.title("BuyBuddy")
    app.geometry("1440x1080")
    app.minsize(800,600)
    app.iconbitmap(resource_path('Images/logo_icon.ico'))

    os.makedirs('CSV_Dataset',exist_ok=True)
    os.makedirs('Saved CSVs',exist_ok=True)
    # Main content frame (right side)
    content_frame = ctk.CTkFrame(app, fg_color="#2D2D2D")
    content_frame.pack(fill="both", expand=True)

    navigation = Sidebar(app)
    navigation.set_command('HOME',home_button_pressed)

    home_screen = create_home_screen()
    current_screen = home_screen

    app.mainloop()