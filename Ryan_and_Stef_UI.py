import tkinter as tk
from tkinter import ttk
import psycopg2

def connect_to_db():
    try:
        # Connect to your PostgreSQL database on PgAdmin
        conn = psycopg2.connect(
            host="localhost",  # or another host if your database is on a different server
            database="milestone2db",
            user="postgres",  # Replace with your PgAdmin username
            password="2312")  # Replace with your PgAdmin password
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def list_states():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT state FROM business ORDER BY state;")
    states = cur.fetchall()
    cur.close()
    conn.close()
    return states

def list_cities(state):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT city FROM business WHERE state = %s ORDER BY city;", (state,))
    cities = cur.fetchall()
    cur.close()
    conn.close()
    return cities

def list_zipcodes(city):
    conn = connect_to_db()
    cur = conn.cursor()
    print(city)
    cur.execute("SELECT DISTINCT zipcode FROM business WHERE city = %s ORDER BY zipcode;", (city,))
    zipcodes = cur.fetchall()
    print(zipcodes)
    cur.close()
    conn.close()
    return zipcodes

def list_categories(zipcode):
    conn = connect_to_db()
    cur = conn.cursor()
    print(zipcode)
    cur.execute("SELECT DISTINCT category FROM business WHERE zipcode = %s ORDER BY category;", (zipcode,))
    categories = cur.fetchall()
    print(categories)
    cur.close()
    conn.close()
    return categories

# def list_businesses(city, state, zipcode, category):
#     conn = connect_to_db()
#     cur = conn.cursor()
#     cur.execute("SELECT name, city, state, zipcode, category FROM business WHERE city = %s AND state = %s AND zipcode = %s AND category = %s ORDER BY name;", (city, state, zipcode, category))
#     businesses = cur.fetchall()
#     cur.close()
#     conn.close()
#     return businesses

def list_businesses(city, state, zipcode):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT name, city, state, zipcode FROM business WHERE city = %s AND state = %s AND zipcode = %s ORDER BY name;", (city, state, zipcode))
    businesses = cur.fetchall()
    cur.close()
    conn.close()
    return businesses

def on_state_selected(event):
    # Clear the city listbox
    city_listbox.delete(0, tk.END)
    zipcode_listbox.delete(0, tk.END)
    category_listbox.delete(0, tk.END)
    business_treeview.delete(*business_treeview.get_children())

    # Get selected state and list cities
    selected_state = state_listbox.get(state_listbox.curselection())
    
    cities = list_cities(selected_state)
    for city in cities:
        city_listbox.insert(tk.END, city[0])

def on_city_selected(event):
    # Clear the business treeview
    zipcode_listbox.delete(0, tk.END)
    category_listbox.delete(0, tk.END)
    business_treeview.delete(*business_treeview.get_children())

    # Get selected state and city
    selected_state = state_listbox.get(state_listbox.curselection())
    selected_city = city_listbox.get(city_listbox.curselection())
    
    zipcodes = list_zipcodes(selected_city)
    for zipcode in zipcodes:
        zipcode_listbox.insert(tk.END, zipcode[0])
    
    
def on_zipcode_selected(event):
    # Clear the business treeview
    category_listbox.delete(0, tk.END)
    business_treeview.delete(*business_treeview.get_children())

    # Get selected state and city
    selected_state = state_listbox.get(state_listbox.curselection())
    selected_city = city_listbox.get(city_listbox.curselection())
    selected_zipcode = zipcode_listbox.get(zipcode_listbox.curselection())
    
    # categories = list_categories(selected_zipcode)
    # for category in categories:
    #     category_listbox.insert(tk.END, category[0])
        
    if selected_city and selected_state and selected_zipcode:
        businesses = list_businesses(selected_city, selected_state, selected_zipcode)
        for business in businesses:
            business_treeview.insert('', 'end', values=business)
            
def on_category_selected(event):
    # Clear the business treeview
    business_treeview.delete(*business_treeview.get_children())

    # Get selected state and city
    selected_state = state_listbox.get(state_listbox.curselection())
    selected_city = city_listbox.get(city_listbox.curselection())
    selected_zipcode = zipcode_listbox.get(zipcode_listbox.curselection())
    selected_category = category_listbox.get(category_listbox.curselection())

    if selected_city and selected_state and selected_zipcode and selected_category:
        businesses = list_businesses(selected_city, selected_state, selected_zipcode, selected_category)
        for business in businesses:
            business_treeview.insert('', 'end', values=business)

    

    

# Set up the main window
root = tk.Tk()
root.title("Milestone 1 - page1")

# Create a label for the header 'State/City'
header_label = ttk.Label(root, text="State/City")
header_label.grid(row=0, column=0, padx=10, pady=5)

# Set up the state listbox with a label
state_frame = tk.Frame(root)
state_frame.grid(row=1, column=0, sticky='nwes', padx=10)
state_label = ttk.Label(state_frame, text="State")
state_label.pack(side=tk.TOP, fill=tk.X)
state_scrollbar = ttk.Scrollbar(state_frame, orient=tk.VERTICAL)
state_listbox = tk.Listbox(state_frame, yscrollcommand=state_scrollbar.set, exportselection=0)
state_scrollbar.config(command=state_listbox.yview)
state_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
state_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
state_listbox.bind("<<ListboxSelect>>", on_state_selected)

# Set up the city listbox with a label
city_frame = tk.Frame(root)
city_frame.grid(row=2, column=0, sticky='nwes', padx=10)
city_label = ttk.Label(city_frame, text="City")
city_label.pack(side=tk.TOP, fill=tk.X)
city_scrollbar = ttk.Scrollbar(city_frame, orient=tk.VERTICAL)
city_listbox = tk.Listbox(city_frame, yscrollcommand=city_scrollbar.set, exportselection=0)
city_scrollbar.config(command=city_listbox.yview)
city_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
city_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
city_listbox.bind("<<ListboxSelect>>", on_city_selected)
            
# Set up the zipcode with a label
zipcode_frame = tk.Frame(root)
zipcode_frame.grid(row=3, column=0, sticky='nwes', padx=10)
zipcode_label = ttk.Label(zipcode_frame, text="Zipcode")
zipcode_label.pack(side=tk.TOP, fill=tk.X)
zipcode_scrollbar = ttk.Scrollbar(zipcode_frame, orient=tk.VERTICAL)
zipcode_listbox = tk.Listbox(zipcode_frame, yscrollcommand=zipcode_scrollbar.set, exportselection=0)
zipcode_scrollbar.config(command=zipcode_listbox.yview)
zipcode_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
zipcode_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
zipcode_listbox.bind("<<ListboxSelect>>", on_zipcode_selected)

# Set up the category with a label
category_frame = tk.Frame(root)
category_frame.grid(row=4, column=0, sticky='nwes', padx=10)
category_label = ttk.Label(category_frame, text="Category")
category_label.pack(side=tk.TOP, fill=tk.X)
category_scrollbar = ttk.Scrollbar(category_frame, orient=tk.VERTICAL)
category_listbox = tk.Listbox(category_frame, yscrollcommand=zipcode_scrollbar.set, exportselection=0)
category_scrollbar.config(command=category_listbox.yview)
category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
category_listbox.bind("<<ListboxSelect>>", on_category_selected)


# Populate the state listbox
for state in list_states():
    state_listbox.insert(tk.END, state[0])

# Set up the business treeview with headings
business_frame = tk.Frame(root)
business_frame.grid(row=0, column=1, rowspan=3, sticky='nwes', padx=10, pady=10)
business_treeview = ttk.Treeview(business_frame, columns=("business", "city", "state"), show='headings')
business_treeview.heading('business', text='Business')
business_treeview.heading('city', text='City')
business_treeview.heading('state', text='State')
business_treeview.column('business', stretch=tk.YES, minwidth=100, width=200)
business_treeview.column('city', stretch=tk.YES, minwidth=100, width=100)
business_treeview.column('state', stretch=tk.YES, minwidth=50, width=50)
business_treeview.pack(fill=tk.BOTH, expand=True)

root.mainloop()