# Import necessary libraries
import csv
import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog as sd
import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from tkinter import messagebox
from tkinter import PhotoImage
import os


# Function to open the "Add Item" window
def open_add_item_window(inventory, inventoryList, log_file):
    add_item_window = tk.Toplevel(root)
    add_item_window.title("Add Item")
    addItem(inventory, inventoryList, add_item_window, log_file)

# Function to open the "Create Order" window
def open_create_order_window():
    create_order_window = tk.Toplevel(root)
    create_order_window.title("Create Order")
    createOrder(create_order_window)

# Function to add item to the inventory
def addItem(inventory, inventoryList, add_item_window, log_file):
    # Labels and entry widgets for item details
    tk.Label(add_item_window, text="Item Name:").grid(row=0, column=0, sticky=tk.W)
    tk.Label(add_item_window, text="Quantity:").grid(row=1, column=0, sticky=tk.W)
    tk.Label(add_item_window, text="User:").grid(row=2, column=0, sticky=tk.W)

    itemNameEntry = tk.Entry(add_item_window)
    userInputEntry = tk.Entry(add_item_window)
    userIDEntry = tk.Entry(add_item_window)

    itemNameEntry.grid(row=0, column=1, sticky=tk.W + tk.E)
    userInputEntry.grid(row=1, column=1, sticky=tk.W + tk.E)
    userIDEntry.grid(row=2, column=1, sticky=tk.W + tk.E)

    # Function to add the item to the inventory
    def addItemToList():
        itemName = itemNameEntry.get()
        userInput = userInputEntry.get()
        userID = userIDEntry.get()  # Retrieve user input

        if itemName and userInput and userID:
            try:
                quantity = int(userInput)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity.")
                return

            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if itemName in inventory:
                old_quantity, old_timestamp, old_user = inventory[itemName]
                new_quantity = old_quantity + quantity
                inventory[itemName] = (new_quantity, timestamp, userID)  # Include user in the tuple
            else:
                inventory[itemName] = (quantity, timestamp, userID)

            printInventory(inventory, inventoryList, log_file)
            itemNameEntry.delete(0, tk.END)
            userInputEntry.delete(0, tk.END)
            userIDEntry.delete(0, tk.END)
            add_item_window.destroy()

    addButton = tk.Button(add_item_window, text="Add", command=addItemToList)
    addButton.grid(row=3, column=1, sticky=tk.W + tk.E)


# Function to load inventory from a CSV file
def loadInventory(filename):
    inventory = {}

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader)  # Read the header row
        for row in reader:
            if len(row) == len(header):
                itemName, quantity, timeStamp, user = row
                inventory[itemName] = (int(quantity), timeStamp, user)
            elif len(row) == len(header) - 1:
                itemName, quantity, timeStamp = row
                inventory[itemName] = (int(quantity), timeStamp)
            else:
                # Handle the case when the number of values is incorrect
                print(f"Skipping invalid row: {row}")

    return inventory


# Function to save inventory to a CSV file
def saveInventory(filename, inventory):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Item', 'Quantity', 'Last Update', 'User'])
        for itemName, itemData in inventory.items():
            if len(itemData) == 3:
                quantity, timeStamp, user = itemData
                writer.writerow([itemName, quantity, timeStamp, user])
            elif len(itemData) == 2:
                quantity, timeStamp = itemData
                writer.writerow([itemName, quantity, timeStamp])


# Function to handle double-click on an item in the inventory list
def on_item_double_click(event, inventory, inventoryList, log_file):
    item = inventoryList.focus()
    selected_item = inventoryList.item(item)
    item_name = selected_item['values'][0]  # Extract the item name from the selected item
    changeQuantity(inventoryList, inventory, item_name, log_file)


# Function to print inventory to the GUI and log to a file
def printInventory(inventory, inventoryList, log_file=None):
    inventoryList.delete(*inventoryList.get_children())
    for item in inventory:
        item_data = inventory[item]
        quantity, timestamp, user_id = item_data if len(item_data) == 3 else (item_data[0], item_data[1], None)
        inventoryList.insert("", "end", values=(item, quantity, timestamp, user_id))

    # Log the inventory to the log file
    if log_file:
        log_writer = csv.writer(log_file)
        for item, item_data in inventory.items():
            quantity, timestamp, user_id = item_data if len(item_data) == 3 else (item_data[0], item_data[1], None)
            log_writer.writerow([item, quantity, timestamp, user_id])


# Function to update an item in the inventory
def update_item():
    global inventory, inventoryList, log_file
    item = inventoryList.focus()
    selected_item = inventoryList.item(item)
    item_name = selected_item['values'][0]  # Extract the item name from the selected item
    user_input = sd.askstring("Update Item",
                              "Enter a new name and quantity for " + str(item_name) + " separated by a comma (,)")
    if user_input is not None:
        new_item_name, new_quantity = user_input.split(",")
        new_item_name = new_item_name.strip()
        new_quantity = int(new_quantity.strip())
        if not new_item_name:
            messagebox.showerror("Error", "Please enter a new item name.")
            return
        if new_quantity < 0:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        old_quantity, old_timestamp = inventory[item_name]
        inventory[new_item_name] = (new_quantity, timestamp)
        del inventory[item_name]

        # Log the change to the log file
        log_writer = csv.writer(log_file)
        log_writer.writerow([item_name, new_item_name, old_quantity, new_quantity, old_timestamp, timestamp])

        printInventory(inventory, inventoryList, log_file)


# Function to change the quantity of an item in the inventory
def changeQuantity(inventoryList, inventory, item_name, log_file=None):
    item_data = inventory[item_name]
    current_quantity, current_timestamp, current_user_id = item_data if len(item_data) == 3 else (
    item_data[0], item_data[1], None)

    # Ask for a user ID as a string
    user_id = sd.askstring("User ID", f"Enter a User ID", initialvalue=current_user_id)
    user_input = sd.askinteger("Change Quantity", f"Enter a new quantity for {item_name}", initialvalue=current_quantity)

    if user_input is not None and user_id is not None:
        if user_input < 0:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        # Update the inventory with the correct values
        inventory[item_name] = (user_input, datetime.datetime.now().strftime('%H:%M:%S %m-%d-%Y '), user_id)

        # After updating, print the inventory to reflect changes
        printInventory(inventory, inventoryList, log_file)


# Function to create an order
# Function to create an order
def createOrder(create_order_window):

    orderNameEntry = tk.Entry(create_order_window)
    poNumberEntry = tk.Entry(create_order_window)
    dueDateEntry = tk.Entry(create_order_window)

    tk.Label(create_order_window, text="Order Name:").grid(row=0, column=0, sticky=tk.W)
    tk.Label(create_order_window, text="PO Number:").grid(row=1, column=0, sticky=tk.W)
    tk.Label(create_order_window, text="Due Date:").grid(row=2, column=0, sticky=tk.W)

    orderNameEntry.grid(row=0, column=2, sticky=tk.W + tk.E)
    poNumberEntry.grid(row=1, column=2, sticky=tk.W + tk.E)
    dueDateEntry.grid(row=2, column=2, sticky=tk.W + tk.E)

    def createOrderAction():
        order_name = orderNameEntry.get()
        po_number = poNumberEntry.get()
        due_date = dueDateEntry.get()

        if order_name and po_number and due_date:
            # Write order details to a CSV file
            with open('orders.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([order_name, po_number, due_date])

            messagebox.showinfo("Order Created", "Order created successfully.")
            create_order_window.destroy()

    createOrderButton = tk.Button(create_order_window, text="Create Order", command=createOrderAction)
    createOrderButton.grid(row=3, column=1, sticky=tk.W + tk.E)



# Function to open the "View Order" window
def open_view_order_window():
    view_order_window = tk.Toplevel(root)
    view_order_window.title("View Order")
    viewOrder(view_order_window)

# Function to view an order
# Function to view an order
# Function to view orders
def viewOrders():
    view_orders_window = tk.Toplevel(root)
    view_orders_window.title("View Orders")

    # Create a Treeview to display order details
    order_tree = ttk.Treeview(view_orders_window, columns=("Order Name", "PO Number", "Due Date"), show="headings")

    order_tree.heading("Order Name", text="Order Name")
    order_tree.heading("PO Number", text="PO Number")
    order_tree.heading("Due Date", text="Due Date")

    order_tree.pack(padx=10, pady=10)

    # Read order data from the CSV file
    try:
        with open('orders.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = next(reader)  # Skip the header row
            for row in reader:
                order_tree.insert("", "end", values=row)
    except FileNotFoundError:
        messagebox.showinfo("No Orders", "No orders found.")

    # Close the view orders window
    close_button = tk.Button(view_orders_window, text="Close", command=view_orders_window.destroy)
    close_button.pack()



# Function to save the current state of the inventory
def save():
    saveInventory('inventory.csv', inventory)
    messagebox.showinfo("Save successful", "You have saved inventory.csv")

# Function to handle the Quit operation
def quit():
    save_confirmation = messagebox.askyesnocancel("Quit", "Do you want to save changes before quitting?")
    if save_confirmation is None:
        # User clicked "Cancel"
        return
    elif save_confirmation:
        # User clicked "Yes"
        saveInventory('inventory.csv', inventory)
    # User clicked "No" or saved successfully
    root.destroy()

# Function to display information about the application
def aboutSection():
    with open('README.md', 'r') as file:
        # Read the contents of the file
        file_contents = file.read()
    new_window = tk.Toplevel(root)
    new_window.title("About")
    tk.Label(new_window, text=file_contents).grid(row=0, column=0)

# Function to export the inventory to a PDF file
def export_to_pdf(inventory):
    try:
        # Create a new PDF document with portrait page orientation
        timestamp = datetime.datetime.now().strftime('%S%Y-%M-%d_%H-%m')
        file_name = f"inventory_{timestamp}.pdf"

        pdf = SimpleDocTemplate(file_name, pagesize=landscape(letter))

        # Create the table data with headers
        table_data = [["Item", "Quantity", "Last Update", "User"]]
        for item_name, item_data in inventory.items():
            quantity, timestamp, user = item_data if len(item_data) == 3 else (item_data[0], item_data[1], None)
            table_data.append([item_name, quantity, timestamp, user])

        # Create a Table object with the table data
        table = Table(table_data)

        # Apply table formatting
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 14),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.aliceblue, colors.lavender]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        # Add the table to the PDF document and build it
        pdf.build([table])

        # Display a message box indicating that the PDF was exported successfully
        messagebox.showinfo("Export PDF", f"PDF exported successfully as '{file_name}'.")
    except Exception as e:
        messagebox.showerror("Export PDF Error", f"An error occurred: {str(e)}")

# Main function to initialize the GUI and start the application
def main():
    global root, inventory, inventoryList, log_file

    inventory = loadInventory('inventory.csv')
    log_file = open('inventory_log.csv', 'a', newline='')
    log_writer = csv.writer(log_file)

    root = tk.Tk()
    root.title("Inventory")

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Save", command=save)
    file_menu.add_separator()
    file_menu.add_command(label="Export PDF", command=lambda: export_to_pdf(inventory))

    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=quit)

    # Modify the Order menu in the main() function
    order_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Order", menu=order_menu)
    order_menu.add_separator()
    order_menu.add_command(label="Create an Order", command=open_create_order_window)
    order_menu.add_command(label="View Orders", command=viewOrders)


    # Help menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=aboutSection)

    # Configure rows and columns
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    root.grid_columnconfigure(3, weight=1)

    inventoryList = ttk.Treeview(root, columns=("Item", "Quantity", "Last Update", 'User'), show="headings")
    inventoryList.heading("Item", text="Item")
    inventoryList.heading("Quantity", text="Quantity")
    inventoryList.heading("Last Update", text="Last Update")
    inventoryList.heading("User", text="User")
    inventoryList.column("Item", width=250, anchor="w")
    inventoryList.column("Quantity", width=150, anchor="center")
    inventoryList.column("Last Update", width=150, anchor="center")
    inventoryList.column("User", width=150, anchor="center")
    inventoryList.grid(row=0, rowspan=4, column=0, columnspan=4, sticky=tk.N + tk.S + tk.E + tk.W, pady=40, padx=20)

    # Bind the double-click event to the on_item_double_click function
    inventoryList.bind("<Double-1>", lambda event: on_item_double_click(event, inventory, inventoryList, log_file))

    # Load and display the application logo
    logo_image = PhotoImage(file="Inventory/logo.png").subsample(6, 6)
    logo_label = tk.Label(root, image=logo_image)
    logo_label.grid(row=4, rowspan=2, column=0, columnspan=2, sticky=tk.W + tk.E, padx=20, pady=20)

    # Buttons for various actions
    addButton = tk.Button(root, text="Add Item", command=lambda: open_add_item_window(inventory, inventoryList, log_file))
    saveButton = tk.Button(root, text="Save", command=save)
    exportButton = tk.Button(root, text="Export PDF", command=lambda: export_to_pdf(inventory))
    quitButton = tk.Button(root, text="Quit", command=quit)

    # Grid placement for buttons
    addButton.grid(row=4, column=2, sticky=tk.W + tk.E, pady=5, padx=5)
    saveButton.grid(row=4, column=3, sticky=tk.W + tk.E, pady=5, padx=5)
    exportButton.grid(row=5, column=2, sticky=tk.W + tk.E, pady=5, padx=5)
    quitButton.grid(row=5, column=3, sticky=tk.W + tk.E, pady=5, padx=5)



    # Display the initial inventory
    printInventory(inventory, inventoryList, log_file)

    # Start the main event loop
    root.mainloop()
    log_file.close()

# Entry point for the application
if __name__ == '__main__':
    main()

