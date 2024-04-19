import tkinter as tk
from tkinter import ttk
import psycopg2
from scipy import stats

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="milestone3db",
            user="postgres",
            password="2321")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def list_states():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT state FROM Business ORDER BY state;")
    states = cur.fetchall()
    cur.close()
    conn.close()
    return states

def list_cities(state):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT city FROM Business WHERE state = %s ORDER BY city;", (state,))
    cities = cur.fetchall()
    cur.close()
    conn.close()
    return cities

def list_zipcodes(city):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT zipcode FROM Business WHERE city = %s ORDER BY zipcode;", (city,))
    zipcodes = cur.fetchall()
    cur.close()
    conn.close()
    return zipcodes

def list_categories(zipcode):
    conn = connect_to_db()
    cur = conn.cursor()
    # This query has been updated to correctly join and fetch unique categories for a given zipcode
    cur.execute("""
        SELECT DISTINCT c.name 
        FROM Category c
        JOIN BusinessCategory bc ON c.category_id = bc.category_id
        JOIN Business b ON bc.business_id = b.business_id
        WHERE b.zipcode = %s
        ORDER BY c.name;
    """, (zipcode,))
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return categories

def list_businesses(city, state, zipcode, category=None):
    conn = connect_to_db()
    cur = conn.cursor()
    # The SQL query needs to handle an optional category filter
    query = """
        SELECT b.name, b.address || ', ' || b.city, b.city, ROUND(b.stars::numeric, 1), COUNT(r.review_id), 
               COALESCE(ROUND(AVG(r.stars)::numeric, 1), 0) AS average_rating, COALESCE(SUM(ci.num_checkins), 0)
        FROM Business b
        LEFT JOIN Review r ON b.business_id = r.business_id
        LEFT JOIN CheckIn ci ON b.business_id = ci.business_id
        LEFT JOIN BusinessCategory bc ON b.business_id = bc.business_id
        LEFT JOIN Category c ON bc.category_id = c.category_id
        WHERE b.city = %s AND b.state = %s AND b.zipcode = %s
    """
    params = [city, state, zipcode]
    
    if category:
        query += " AND c.name = %s"
        params.append(category)
        
    query += " GROUP BY b.business_id ORDER BY b.name;"
    cur.execute(query, params)
    businesses = cur.fetchall()
    cur.close()
    conn.close()
    return businesses


def list_top_categories(zipcode, min_count=5):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, COUNT(*) as business_count
        FROM Category c
        JOIN BusinessCategory bc ON c.category_id = bc.category_id
        JOIN Business b ON bc.business_id = b.business_id
        WHERE b.zipcode = %s
        GROUP BY c.name
        HAVING COUNT(*) >= %s
        ORDER BY business_count DESC;
    """, (zipcode, min_count))
    top_categories = cur.fetchall()
    cur.close()
    conn.close()
    return top_categories

def list_zipcode_stats(zipcode):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.zipcode, COUNT(b.business_id) AS num_businesses, zs.population, zs.average_income
        FROM Business b
        LEFT JOIN ZipcodeStats zs ON b.zipcode = zs.zipcode
        WHERE b.zipcode = %s
        GROUP BY b.zipcode, zs.population, zs.average_income;
    """, (zipcode,))
    stats = cur.fetchone()
    cur.close()
    conn.close()
    return stats

def clear_all():
    # Clear listboxes
    state_listbox.delete(0, tk.END)
    city_listbox.delete(0, tk.END)
    zipcode_listbox.delete(0, tk.END)
    category_listbox.delete(0, tk.END)
    top_categories_listbox.delete(0, tk.END)
    
    # Clear the treeview
    business_treeview.delete(*business_treeview.get_children())
    
    # Optionally, you can re-populate the state listbox if needed
    for state in list_states():
        state_listbox.insert(tk.END, state[0])






def on_state_selected(event):
    if not state_listbox.curselection():
        return
    selected_state = state_listbox.get(state_listbox.curselection())
    cities = list_cities(selected_state)
    city_listbox.delete(0, tk.END)
    zipcode_listbox.delete(0, tk.END)
    category_listbox.delete(0, tk.END)
    business_treeview.delete(*business_treeview.get_children())
    for city in cities:
        city_listbox.insert(tk.END, city[0])

def on_city_selected(event):
    if not city_listbox.curselection():
        return
    selected_city = city_listbox.get(city_listbox.curselection())
    zipcodes = list_zipcodes(selected_city)
    zipcode_listbox.delete(0, tk.END)
    category_listbox.delete(0, tk.END)
    business_treeview.delete(*business_treeview.get_children())
    for zipcode in zipcodes:
        zipcode_listbox.insert(tk.END, zipcode[0])

def on_zipcode_selected(event):
    # Clear previous selections and entries in listboxes and treeview
    category_listbox.delete(0, tk.END)
    top_categories_listbox.delete(0, tk.END)
    business_treeview.delete(*business_treeview.get_children())

    # Get the currently selected zipcode
    selected_index = zipcode_listbox.curselection()
    if not selected_index:
        return
    selected_zipcode = zipcode_listbox.get(selected_index)
    stats = list_zipcode_stats(selected_zipcode)
    if stats:
        num_businesses, population, avg_income = stats[1], stats[2], stats[3]
        num_businesses_label.config(text=f"Number of Businesses: {num_businesses}")
        population_label.config(text=f"Total Population: {population}")
        avg_income_label.config(text=f"Average Income: ${avg_income:.2f}" if avg_income else "Average Income: N/A")
    else:
        num_businesses_label.config(text="Number of Businesses: N/A")
        population_label.config(text="Total Population: N/A")
        avg_income_label.config(text="Average Income: N/A")
    # Update categories for the selected zipcode
    categories = list_categories(selected_zipcode)
    for category in categories:
        category_listbox.insert(tk.END, category[0])

    # Fetch top categories for the selected zipcode
    top_categories = list_top_categories(selected_zipcode, min_count=5)
    for category, count in top_categories:
        category_str = f"{count} - {category}"  # Format: "count - category name"
        top_categories_listbox.insert(tk.END, category_str)

def on_category_selected(event):
    if not category_listbox.curselection():
        return
    selected_category = category_listbox.get(category_listbox.curselection())
    selected_state_idx = state_listbox.curselection()
    selected_city_idx = city_listbox.curselection()
    selected_zipcode_idx = zipcode_listbox.curselection()
    
    # Only proceed if all selections are made
    if selected_state_idx and selected_city_idx and selected_zipcode_idx and selected_category:
        selected_state = state_listbox.get(selected_state_idx)
        selected_city = city_listbox.get(selected_city_idx)
        selected_zipcode = zipcode_listbox.get(selected_zipcode_idx)
        
        # Fetch businesses based on the selections, with the category filter applied
        businesses = list_businesses(selected_city, selected_state, selected_zipcode, selected_category)
        business_treeview.delete(*business_treeview.get_children())
        
        # Insert each business into the TreeView
        for business in businesses:
            # Format data as needed before insertion into the TreeView
            formatted_business = (business[0], 
                                  business[1], 
                                  business[2], 
                                  f"{business[3]:.1f}",  # Stars rounded to one decimal place
                                  business[4],            # Review count
                                  f"{business[5]:.1f}" if business[5] else "N/A",  # Average rating, check for None
                                  business[6])            # Number of check-ins
            business_treeview.insert('', 'end', values=formatted_business)


def on_search_clicked():
    # Get selected items from the listboxes
    try:
        selected_state_idx = state_listbox.curselection()[0]
        selected_city_idx = city_listbox.curselection()[0]
        selected_zipcode_idx = zipcode_listbox.curselection()[0]
        # Check if a category is selected as well
        selected_category_idx = category_listbox.curselection()
        selected_category = category_listbox.get(selected_category_idx) if selected_category_idx else None
    except IndexError:
        tk.messagebox.showinfo("Selection Error", "Please select a state, city, and zipcode.")
        return

    selected_state = state_listbox.get(selected_state_idx)
    selected_city = city_listbox.get(selected_city_idx)
    selected_zipcode = zipcode_listbox.get(selected_zipcode_idx)

    # Fetch businesses based on the selections, possibly with a category filter applied
    businesses = list_businesses(selected_city, selected_state, selected_zipcode, selected_category)
    business_treeview.delete(*business_treeview.get_children())
    
    # Insert each business into the TreeView
    for business in businesses:
        # Format data as needed before insertion into the TreeView
        formatted_business = (business[0], 
                              business[1], 
                              business[2], 
                              f"{business[3]:.1f}",  # Stars rounded to one decimal place
                              business[4],            # Review count
                              f"{business[5]:.1f}" if business[5] else "N/A",  # Average rating, check for None
                              business[6])            # Number of check-ins
        business_treeview.insert('', 'end', values=formatted_business)





    

    

# Set up the main window
root = tk.Tk()
root.title("Milestone 1 - page1")

# Create a label for the header 'State/City'
header_label = ttk.Label(root, text="State/City")
header_label.grid(row=0, column=0, padx=10, pady=5)

# Set up the state listbox with a label
state_frame = tk.Frame(root)
state_frame.grid(row=0, column=0, sticky='nwes', padx=10)
state_label = ttk.Label(state_frame, text="State")
state_label.pack(side=tk.TOP, fill=tk.X)
state_scrollbar = ttk.Scrollbar(state_frame, orient=tk.VERTICAL)
state_listbox = tk.Listbox(state_frame, height=10, yscrollcommand=state_scrollbar.set, exportselection=0)
state_scrollbar.config(command=state_listbox.yview)
state_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
state_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
state_listbox.bind("<<ListboxSelect>>", on_state_selected)

# Set up the city listbox with a label
city_frame = tk.Frame(root)
city_frame.grid(row=1, column=0, sticky='nwes', padx=10)
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

# Set up the business treeview with the corrected columns
business_frame = tk.Frame(root)
business_frame.grid(row=0, column=1, rowspan=5, sticky='nsew', padx=10, pady=5)
business_treeview = ttk.Treeview(business_frame, columns=("name", "address", "city", "stars", "review_count", "review_rating", "num_checkins"), show='headings')
business_treeview.pack(fill=tk.BOTH, expand=True)

# Configure column headings
business_treeview.heading('name', text='Business Name')
business_treeview.heading('address', text='Address')
business_treeview.heading('city', text='City')
business_treeview.heading('stars', text='Stars')
business_treeview.heading('review_count', text='Review Count')
business_treeview.heading('review_rating', text='Review Rating')  # Add this line for the Review Rating heading
business_treeview.heading('num_checkins', text='Number of Check-ins')

# Configure column widths (you can adjust these as needed)
business_treeview.column('name', minwidth=0, width=200, stretch=tk.NO)
business_treeview.column('address', minwidth=0, width=200, stretch=tk.NO)
business_treeview.column('city', minwidth=0, width=100, stretch=tk.NO)
business_treeview.column('stars', minwidth=0, width=50, stretch=tk.NO)
business_treeview.column('review_count', minwidth=0, width=100, stretch=tk.NO)
business_treeview.column('review_rating', minwidth=0, width=100, stretch=tk.NO)  # Add this line to configure the Review Rating column
business_treeview.column('num_checkins', minwidth=0, width=130, stretch=tk.NO)

#Set up the search button
search_button = ttk.Button(root, text="Search", command=on_search_clicked)
search_button.grid(row=5, column=0, padx=10, pady=5, sticky='ew')

# Set up the zipcode statistics frame
stats_frame = tk.Frame(root)
stats_frame.grid(row=1, column=3, rowspan=4, sticky='nsew', padx=10, pady=5)
stats_label = ttk.Label(stats_frame, text="Zipcode Statistics")
stats_label.pack(side=tk.TOP, fill=tk.X)
num_businesses_label = ttk.Label(stats_frame, text="Number of Businesses: ")
num_businesses_label.pack(side=tk.TOP, anchor='w')
population_label = ttk.Label(stats_frame, text="Total Population: ")
population_label.pack(side=tk.TOP, anchor='w')
avg_income_label = ttk.Label(stats_frame, text="Average Income: ")
avg_income_label.pack(side=tk.TOP, anchor='w')

# Set up the clear button
clear_button = ttk.Button(root, text="Clear", command=clear_all)
clear_button.grid(row=6, column=0, padx=10, pady=5, sticky='ew')

# Add a new frame and listbox to display top business categories
top_categories_frame = tk.Frame(root)
top_categories_frame.grid(row=1, column=2, rowspan=4, sticky='nsew', padx=10, pady=5)
top_categories_label = ttk.Label(top_categories_frame, text="Top Categories")
top_categories_label.pack(side=tk.TOP, fill=tk.X)
top_categories_scrollbar = ttk.Scrollbar(top_categories_frame, orient=tk.VERTICAL)
top_categories_listbox = tk.Listbox(top_categories_frame, yscrollcommand=top_categories_scrollbar.set, exportselection=0)
top_categories_scrollbar.config(command=top_categories_listbox.yview)
top_categories_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
top_categories_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)



# Populate the state listbox
for state in list_states():
    state_listbox.insert(tk.END, state[0])

root.mainloop()