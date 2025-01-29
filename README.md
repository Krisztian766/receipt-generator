# Receipt Printing Application

## Overview
This is a receipt printing application developed using Python, PyQt5 for the graphical user interface, and the `pyusb` library for USB communication with receipt printers. The application is designed for a pizza delivery business and allows users to enter customer details, select products, apply discounts, preview receipts, and print them using a compatible thermal receipt printer.

## Features
- Graphical user interface (GUI) with PyQt5.
- USB receipt printer support.
- Customer information input fields (name, address, phone number).
- Product selection from a predefined list (loaded from a text file).
- Discount application (0% to 20%).
- Receipt preview before printing.
- Auto-incrementing order number.
- Uses ESC/POS commands for formatted receipt printing.

## Requirements
- Python 3.x
- PyQt5
- `pyusb` for USB communication

## Installation
1. Clone this repository or download the source files.
2. Install the required dependencies using pip:
   ```bash
   pip install pyqt5 pyusb
   ```
3. Ensure that your receipt printer is connected and recognized by your system.

## Usage
1. Run the application:
   ```bash
   python main.py
   ```
2. Enter customer details.
3. Select products from the dropdown list.
4. Apply any applicable discounts.
5. Click "Preview Receipt" to see a formatted receipt.
6. Click "Print Receipt" to send the receipt to the connected thermal printer.

## Configuration
- The list of available products and their prices should be stored in a `termekek.txt` file in the following format:
  ```
  ProductName1,Price1
  ProductName2,Price2
  ```
- Update the `Printer` class with the correct `vendor_id` and `product_id` of your thermal printer.

## Troubleshooting
- If the printer is not detected, ensure that the correct vendor and product IDs are used.
- If the text is not printing correctly, check the encoding (`windows-1250`) and adjust based on your printer’s language support.
- Run the script with administrator privileges if necessary to access USB devices.

## Author
Developed by Czeczó Krisztián.

