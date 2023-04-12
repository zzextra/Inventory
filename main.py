import csv
import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog as sd
import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from tkinter import messagebox

def invChange(inventory, itemName, userInput):
    newValue = inventory.get(itemName, (0, None))[0] + int(userInput)

    if newValue < 0:
        print("Error: The new value is negative. Please enter a positive number.")
    else:
        timeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inventory[itemName] = (newValue, timeStamp)
        print("The new value for", itemName, "is:", newValue, "at", timeStamp)

    return inventory


    return inventory

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



def printInventory(inventory, inventoryList):
    for i in inventoryList.get_children():
        inventoryList.delete(i)

    for itemName, itemData in inventory.items():
        quantity, timeStamp = itemData
        inventoryList.insert('', 'end', values=(itemName, quantity, timeStamp))



    def on_item_double_click(event):
        item = inventoryList.focus()
        selected_item = inventoryList.item(item)
        item_name = selected_item['values'][0]  # Extract the item name from the selected item
        changeQuantity(inventoryList, inventory, item_name)

    inventoryList.bind("<Double-Button-1>", on_item_double_click)


def changeQuantity(inventoryList, inventory, item_name):
    current_quantity, _ = inventory.get(item_name, (0, None))
    user_input = sd.askinteger("Change Quantity", "Enter a new quantity for " + str(item_name))
    if user_input is not None:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inventory[item_name] = (user_input, timestamp)
        printInventory(inventory, inventoryList)


def save():
    saveInventory('inventory.csv', inventory)

def addItem(inventory, inventoryList):
    global itemNameEntry, userInputEntry

    itemName = itemNameEntry.get().strip()
    userInput = userInputEntry.get().strip()

    if not itemName:
        messagebox.showerror("Error", "Please enter an item name.")
        return

    if not userInput:
        messagebox.showerror("Error", "Please enter a quantity.")
        return

    try:
        userInput = int(userInput)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid quantity.")
        return

    invChange(inventory, itemName, userInput)
    printInventory(inventory, inventoryList)

    itemNameEntry.delete(0, tk.END)
    userInputEntry.delete(0, tk.END)
    itemNameEntry.focus()


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
    pdf = SimpleDocTemplate("inventory.pdf", pagesize=landscape(letter))

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
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.aliceblue, colors.lavender]),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Add the table to the PDF document and build it
    pdf.build([table])

def main():
    global root, inventory, itemNameEntry, userInputEntry, inventoryList

    inventory = loadInventory('inventory.csv')

    root = tk.Tk()
    root.title("Inventory Management")

    # Configure rows
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=0)
    root.grid_rowconfigure(2, weight=0)
    root.grid_rowconfigure(3, weight=1)
    root.grid_rowconfigure(4, weight=0)

    # Configure columns
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=0)
    root.grid_columnconfigure(2, weight=1)
    root.grid_columnconfigure(3, weight=1)

    tk.Label(root, text="Item Name:").grid(row=0, column=0, sticky=tk.W)
    tk.Label(root, text="Quantity:").grid(row=1, column=0, sticky=tk.W)

    itemNameEntry = tk.Entry(root)
    userInputEntry = tk.Entry(root)

    itemNameEntry.grid(row=0, column=1, sticky=tk.W)
    userInputEntry.grid(row=1, column=1, sticky=tk.W)

    addButton = tk.Button(root, text="Add Item", command=lambda: addItem(inventory, inventoryList))
    saveButton = tk.Button(root, text="Save", command=save)
    quitButton = tk.Button(root, text="Quit", command=quit)
    exportButton = tk.Button(root, text="Export PDF", command=lambda: export_to_pdf(inventory))  # Added Export PDF button

    addButton.grid(row=2, column=0, sticky=tk.W)
    saveButton.grid(row=2, column=1, sticky=tk.W)
    exportButton.grid(row=3, column=1, sticky=tk.W)  # Added Export PDF button to the grid
    quitButton.grid(row=3, column=0, columnspan=1, sticky=tk.W+tk.E)

    inventoryList = ttk.Treeview(root, columns=("Item", "Quantity", "Last Update"), show="headings")
    inventoryList.heading("Item", text="Item")
    inventoryList.heading("Quantity", text="Quantity")
    inventoryList.heading("Last Update", text="Last Update")
    inventoryList.column("Item", width=150, anchor="center")
    inventoryList.column("Quantity", width=100, anchor="center")
    inventoryList.column("Last Update", width=150, anchor="center")
    inventoryList.grid(row=0, rowspan=5, column=2, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

    printInventory(inventory, inventoryList)

    root.mainloop()



if __name__ == '__main__':
    main()