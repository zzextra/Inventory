import csv
import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog as sd
import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from tkinter import messagebox
import os



def open_add_item_window(inventory, inventoryList, log_file):
    add_item_window = tk.Toplevel(root)
    add_item_window.title("Add Item")
    addItem(inventory, inventoryList, add_item_window, log_file)


def addItem(inventory, inventoryList, add_item_window, log_file):
    tk.Label(add_item_window, text="Item Name:").grid(row=0, column=0, sticky=tk.W)
    tk.Label(add_item_window, text="Quantity:").grid(row=1, column=0, sticky=tk.W)

    itemNameEntry = tk.Entry(add_item_window)
    userInputEntry = tk.Entry(add_item_window)

    itemNameEntry.grid(row=0, column=1, sticky=tk.W + tk.E)
    userInputEntry.grid(row=1, column=1, sticky=tk.W + tk.E)

    def addItemToList():
        itemName = itemNameEntry.get()
        userInput = userInputEntry.get()
        if itemName and userInput:
            try:
                quantity = int(userInput)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity.")
                return
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if itemName in inventory:
                old_quantity, old_timestamp = inventory[itemName]
                new_quantity = old_quantity + quantity
                inventory[itemName] = (new_quantity, timestamp)
            else:
                inventory[itemName] = (quantity, timestamp)
            printInventory(inventory, inventoryList, log_file)
            itemNameEntry.delete(0, tk.END)
            userInputEntry.delete(0, tk.END)
            add_item_window.destroy()

    addButton = tk.Button(add_item_window, text="Add", command=addItemToList)
    addButton.grid(row=2, column=1, sticky=tk.W + tk.E)



def loadInventory(filename):
    inventory = {}

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)  # skip header row
        for row in reader:
            itemName, quantity, timeStamp = row
            inventory[itemName] = (int(quantity), timeStamp)

    return inventory


def saveInventory(filename, inventory):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['Item', 'Quantity', 'Last Update'])
        for itemName, itemData in inventory.items():
            quantity, timeStamp = itemData
            writer.writerow([itemName, quantity, timeStamp])


def on_item_double_click(event, inventory, inventoryList, log_file):
    item = inventoryList.focus()
    selected_item = inventoryList.item(item)
    item_name = selected_item['values'][0]  # Extract the item name from the selected item
    changeQuantity(inventoryList, inventory, item_name, log_file)


def printInventory(inventory, inventoryList, log_file=None):
    inventoryList.delete(*inventoryList.get_children())
    for item in inventory:
        quantity, timestamp = inventory[item]
        inventoryList.insert("", "end", values=(item, quantity, timestamp))

    # Log the inventory to the log file
    if log_file:
        log_writer = csv.writer(log_file)
        for item in inventory:
            quantity, timestamp = inventory[item]
            log_writer.writerow([item, quantity, timestamp])

        def update_item():
            global inventory, inventoryList, log_file
            item = inventoryList.focus()
            selected_item = inventoryList.item(item)
            item_name = selected_item['values'][0]  # Extract the item name from the selected item
            user_input = sd.askstring("Update Item", "Enter a new name and quantity for " + str(
                item_name) + " separated by a comma (,)")
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


def changeQuantity(inventoryList, inventory, item_name, log_file=None):
    current_quantity, current_timestamp = inventory[item_name]
    user_input = sd.askinteger("Change Quantity", "Enter a new quantity for " + str(item_name), initialvalue=current_quantity)
    if user_input is not None:
        if user_input < 0:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return
        inventory[item_name] = (user_input, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        printInventory(inventory, inventoryList, log_file)


def save():
    saveInventory('inventory.csv', inventory)




#def removeItem():
   # itemName = itemNameEntry.get()
   # userInput = '-' + userInputEntry.get()
   # inventory = invChange(inventory, itemName, userInput)
   # printInventory(inventory)

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



def export_to_pdf(inventory):
    # Create a new PDF document with landscape page orientation
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"inventory_{timestamp}.pdf"

    pdf = SimpleDocTemplate(file_name, pagesize=landscape(letter))

    # Create the table data with headers
    table_data = [["Item", "Quantity", "Last Update"]]
    for item_name, item_data in inventory.items():
        quantity, timestamp = item_data
        table_data.append([item_name, quantity, timestamp])

    # Create a Table object with the table data
    table = Table(table_data)

    # Apply table formatting
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.aliceblue, colors.lavender]),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Add the table to the PDF document and build it
    pdf.build([table])

    # Display a message box indicating that the PDF was exported successfully
    messagebox.showinfo("Export PDF", f"PDF exported successfully as '{file_name}'.")


def main():
    global root, inventory, inventoryList, log_file

    inventory = loadInventory('inventory.csv')
    log_file = open('inventory_log.csv', 'a', newline='')
    log_writer = csv.writer(log_file)

    if not os.path.isfile('inventory_log.csv') or os.path.getsize('inventory_log.csv') == 0:
        # Write the header row to the log file if it's empty
        log_writer.writerow(['Item', 'New Value', 'Timestamp'])

    root = tk.Tk()
    root.title("Resource OH Inventory")

    # Check if the inventory file exists, create it if it doesn't
    if not os.path.isfile('inventory.csv') or os.path.getsize('inventory.csv') == 0:
        with open('inventory.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['item_name', 'quantity', 'timestamp'])

    # Check if the log file exists, create it if it doesn't
    if not os.path.isfile('inventory_log.csv') or os.path.getsize('inventory_log.csv') == 0:
        with open('inventory_log.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['old_name', 'new_name', 'old_quantity', 'new_quantity', 'old timestamp', 'new timestamp'])




    # Configure rows
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=0)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=0)
    root.grid_rowconfigure(4, weight=0)   # New row for buttons

    # Configure columns
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    root.grid_columnconfigure(3, weight=1)

    addButton = tk.Button(root, text="Add Item", command=lambda: open_add_item_window(inventory, inventoryList, log_file))

    saveButton = tk.Button(root, text="Save", command=save)
    quitButton = tk.Button(root, text="Quit", command=quit)
    exportButton = tk.Button(root, text="Export PDF",
                             command=lambda: export_to_pdf(inventory))  # Added Export PDF button
    quit1Button = tk.Button(root, text="Placeholder", command=quit)
    quit2Button = tk.Button(root, text="Placeholder", command=quit)
    quit3Button = tk.Button(root, text="Placeholder", command=quit)
    quit4Button = tk.Button(root, text="Placeholder", command=quit)

    addButton.grid(row=3, column=0, sticky=tk.W + tk.E)
    saveButton.grid(row=3, column=1, sticky=tk.W + tk.E)  # Moved Save button to row 3
    exportButton.grid(row=3, column=2, sticky=tk.W + tk.E)  # Moved Export PDF button to row 3
    quitButton.grid(row=3, column=3, sticky=tk.W + tk.E)  # Moved Quit button to row 3

    quit1Button.grid(row=4, column=0, sticky=tk.W + tk.E)
    quit2Button.grid(row=4, column=1, sticky=tk.W + tk.E)  # Moved Save button to row 3
    quit3Button.grid(row=4, column=2, sticky=tk.W + tk.E)  # Moved Export PDF button to row 3
    quit4Button.grid(row=4, column=3, sticky=tk.W + tk.E)  # Moved Quit button to row 3

    inventoryList = ttk.Treeview(root, columns=("Item", "Quantity", "Last Update"), show="headings")
    inventoryList.heading("Item", text="Item")
    inventoryList.heading("Quantity", text="Quantity")
    inventoryList.heading("Last Update", text="Last Update")
    inventoryList.column("Item", width=150, anchor="center")
    inventoryList.column("Quantity", width=100, anchor="center")
    inventoryList.column("Last Update", width=150, anchor="center")
    inventoryList.grid(row=2, rowspan=1, column=0, columnspan=4, sticky=tk.N + tk.S + tk.E + tk.W)

    # Add this line to bind the double-click event to the on_item_double_click function
    inventoryList.bind("<Double-1>", lambda event: on_item_double_click(event, inventory, inventoryList, log_file))


    printInventory(inventory, inventoryList, log_file)

    root.mainloop()
    log_file.close()


if __name__ == '__main__':
    main()