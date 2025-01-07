import usb.core
import usb.util
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox, QMessageBox

# Nyugta sablon, amely a nyugta szövegét formázza
nyugta_sablon = """
========= Pizzakaravan =================

    HÁZHOZSZÁLLÍTÁS NYUGTA
      www.pizzakaravan.hu
---------------------------------------
Sorszam: {rendeles_szam}  Datum: {datum} {ido}
---------------------------------------
Vasarlo: {vasarlo_neve}
Cim: {vasarlo_cim}
Tel.: {vasarlo_telefon}
--------------------------------------
Termekek:
{termekek}
--------------------------------------
Teljes osszeg: {osszeg} Ft  
Kedvezmeny: {kedvezmeny} Ft
---------------------------------------
   |Vegosszeg: {vegeosszeg} Ft|
-------------------------------------
     Koszonjuk a rendeleset!
       www.pizzakaravan.hu
-------------------------------------
Nyugta: {generalt}
====================================
"""

class Printer:
    def __init__(self, vendor_id, product_id):
        self.dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if self.dev is None:
            raise ValueError("Nyomtató nem található")
        self.dev.set_configuration()

    def print_receipt(self, receipt_text):
        try:
            # Nyugta szöveg kódolása Windows-1250-re
            receipt_text = receipt_text.encode('windows-1250', errors='replace')

            # ESC/POS parancs a vastag betűtípushoz
            ESC_BOLD_ON = b'\x1b\x45\x01'  # Vastag betű
            ESC_BOLD_OFF = b'\x1b\x45\x00'  # Alap betűtípus

            # Nyugta szöveg nyomtatása vastag betűkkel
            receipt_text = ESC_BOLD_ON + receipt_text + ESC_BOLD_OFF  # Alkalmazza a vastagítást
            self.dev.write(0x01, receipt_text, timeout=1000)

            # Új sorok, hogy jobban elváljanak az egyes szakaszok
            self.dev.write(0x01, b'\n\n\n\n\n', timeout=1000)
            print("Nyugta sikeresen nyomtatva!")
        except Exception as e:
            raise Exception(f"A nyugta nyomtatása nem sikerült: {e}")


class NyugtaApp(QWidget):
    def __init__(self):
        super().__init__()

        self.printer = None  # Nyomtató
        self.products = {}  # Termékek és áraik
        self.rendeles_szam_counter = 1  # Rendelés számláló
        self.selected_products = []  # Kiválasztott termékek
        self.initUI()
        self.load_products_from_txt()

    def initUI(self):
        form_layout = QFormLayout()

        # Beviteli mezők
        self.rendeles_szam = QLineEdit(self)
        self.rendeles_szam.setReadOnly(True)
        self.rendeles_szam.setText(str(self.rendeles_szam_counter))
        self.datum = QLineEdit(time.strftime("%Y-%m-%d"), self)
        self.ido = QLineEdit(time.strftime("%H:%M"), self)
        self.vasarlo_neve = QLineEdit(self)
        self.vasarlo_cim = QLineEdit(self)
        self.vasarlo_telefon = QLineEdit(self)
        self.kedvezmeny = QComboBox(self)
        self.kedvezmeny.addItems(["0%", "5%", "10%", "15%", "20%"])
        self.termekek_combo = QComboBox(self)
        self.termekek_combo.setEditable(True)
        self.termekek_combo.setPlaceholderText("Válasszon terméket")

        # Gombok
        self.add_product_button = QPushButton('Termék hozzáadása', self)
        self.add_product_button.clicked.connect(self.add_product)

        self.print_button = QPushButton('Nyugta nyomtatása', self)
        self.print_button.clicked.connect(self.print_receipt)

        self.preview_button = QPushButton('Nyugta előnézete', self)
        self.preview_button.clicked.connect(self.show_receipt_preview)

        # Elrendezés
        form_layout.addRow('Rendelés szám:', self.rendeles_szam)
        form_layout.addRow('Dátum:', self.datum)
        form_layout.addRow('Idő:', self.ido)
        form_layout.addRow('Vásárló neve:', self.vasarlo_neve)
        form_layout.addRow('Vásárló címe:', self.vasarlo_cim)
        form_layout.addRow('Vásárló telefon:', self.vasarlo_telefon)
        form_layout.addRow('Kedvezmény:', self.kedvezmeny)
        form_layout.addRow('Termékek:', self.termekek_combo)
        form_layout.addRow(self.add_product_button)

        self.selected_products_label = QLabel("Kiválasztott termékek: ", self)
        form_layout.addRow(self.selected_products_label)

        form_layout.addRow(self.preview_button)
        form_layout.addRow(self.print_button)

        self.setLayout(form_layout)
        self.setWindowTitle('Nyugtázó')
        self.setGeometry(100, 100, 500, 500)

    def load_products_from_txt(self):
        try:
            with open("termekek.txt", "r", encoding="utf-8") as f:
                for line in f:
                    name, price = line.strip().split(",")
                    self.products[name] = int(price)
                    self.termekek_combo.addItem(name)
        except Exception as e:
            QMessageBox.warning(self, "Hiba", f"A termékek betöltése nem sikerült: {str(e)}")
            
    def add_product(self):
        # A kiválasztott termék lekérdezése a legördülő menüből
        termek_name = self.termekek_combo.currentText()
        if termek_name and termek_name in self.products:
            # A kiválasztott termék hozzáadása a listához
            self.selected_products.append(termek_name)
            # Előfordulások számlálása a kiválasztott termékek között
            product_count = {termek: self.selected_products.count(termek) for termek in set(self.selected_products)}
            # Szöveg készítése a termékek listájáról és azok darabszámáról
            product_list_text = ", ".join(f"{termek} (x{count})" for termek, count in product_count.items())
            # Frissíti a kiválasztott termékek címkét
            self.selected_products_label.setText("Kiválasztott termékek: " + product_list_text)

    def print_receipt(self):
        try:
            if not self.printer:
                self.printer = Printer(vendor_id=0x1504, product_id=0x0025)

            adatok = {
                "rendeles_szam": self.rendeles_szam.text(),
                "datum": self.datum.text(),
                "ido": self.ido.text(),
                "vasarlo_neve": self.vasarlo_neve.text(),
                "vasarlo_cim": self.vasarlo_cim.text(),
                "vasarlo_telefon": self.vasarlo_telefon.text(),
                "osszeg": "0",
                "kedvezmeny": self.kedvezmeny.currentText(),
                "vegeosszeg": "0",
                "generalt": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            total = 0
            termekek_list = []

            for termek_name in self.selected_products:
                termek_ar = self.products[termek_name]
                total += termek_ar
                termekek_list.append(f"{termek_name} - {termek_ar} Ft")

            kedvezmeny_perc = int(self.kedvezmeny.currentText().strip('%'))
            kedvezmeny = total * kedvezmeny_perc / 100
            vegeosszeg = total - kedvezmeny

            adatok["termekek"] = "\n".join(termekek_list)
            adatok["osszeg"] = str(total)
            adatok["vegeosszeg"] = str(vegeosszeg)
            adatok["kedvezmeny"] = str(kedvezmeny)

            nyugta = nyugta_sablon.format(**adatok)
            self.printer.print_receipt(nyugta)

            self.rendeles_szam_counter += 1
            self.rendeles_szam.setText(str(self.rendeles_szam_counter))

        except Exception as e:
            QMessageBox.warning(self, "Hiba", str(e))

    def show_receipt_preview(self):
        adatok = {
            "rendeles_szam": self.rendeles_szam.text(),
            "datum": self.datum.text(),
            "ido": self.ido.text(),
            "vasarlo_neve": self.vasarlo_neve.text(),
            "vasarlo_cim": self.vasarlo_cim.text(),
            "vasarlo_telefon": self.vasarlo_telefon.text(),
            "osszeg": "0",
            "kedvezmeny": self.kedvezmeny.currentText(),
            "vegeosszeg": "0",
            "generalt": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        total = 0
        termekek_list = []

        for termek_name in self.selected_products:
            termek_ar = self.products[termek_name]
            total += termek_ar
            termekek_list.append(f"{termek_name} - {termek_ar} Ft")

        kedvezmeny_perc = int(self.kedvezmeny.currentText().strip('%'))
        kedvezmeny = total * kedvezmeny_perc / 100
        vegeosszeg = total - kedvezmeny

        adatok["termekek"] = "\n".join(termekek_list)
        adatok["osszeg"] = str(total)
        adatok["vegeosszeg"] = str(vegeosszeg)
        adatok["kedvezmeny"] = str(kedvezmeny)

        nyugta = nyugta_sablon.format(**adatok)
        QMessageBox.information(self, "Nyugta előnézete", nyugta)


if __name__ == '__main__':
    app = QApplication([])
    window = NyugtaApp()
    window.show()
    app.exec_()
