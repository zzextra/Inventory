# Inventory
Inventory is a Python script that provides a simple graphical user interface (GUI) to manage and track inventory items. The script allows users to add items, change their quantities, save changes to a CSV file, log inventory updates, and export the inventory list as a PDF.

Features
Add items to the inventory with a specified quantity
Modify the quantity of items in the inventory
Save the inventory to a CSV file
Log inventory updates with timestamps to a separate CSV file
Export the inventory list to a PDF file
Double-click on an item to change its quantity
Requirements
Python 3.x
tkinter
ReportLab
To install the ReportLab library, use the following command:

pip install reportlab

How to Run
Ensure you have Python 3.x installed and the required libraries.
Open a terminal or command prompt in the directory containing the script.
Run the script using the following command:

python resource_oh_inventory.py

Usage
Use the "Add Item" button to add a new item to the inventory.
Double-click on an item in the inventory list to change its quantity.
Use the "Save" button to save the inventory to a CSV file.
Use the "Export PDF" button to export the inventory list as a PDF file.
Use the "Quit" button to exit the program. You will be prompted to save changes before quitting.
Files
inventory.csv: Contains the inventory data, including item names, quantities, and last update timestamps.
inventory_log.csv: Logs inventory updates, including old and new values, and timestamps for each update.
Please note that the code provided may need to be modified slightly to remove the placeholder buttons before using it in a production environment.
