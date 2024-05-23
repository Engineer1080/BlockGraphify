import os
import json
from PyQt5.QtWidgets import QApplication, QSlider, QPushButton, QLineEdit, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QCheckBox
from conversion_logic import process_images_in_directory
from conversion_logic import generate_java_colors_file
from PIL import Image, ImageOps
import sys

font = QFont()
font.setPointSize(12)  # Schriftgröße festlegen


class ImageToBlockGraphicApp(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BlockGraphify")
        self.setStyleSheet("background-color: rgb(52, 155, 130)")

        self.init_ui()

        config = self.load_config()
        self.load_gui_size()  # GUI-Auflösung laden
        if 'img_path' in config:
            self.img_path_edit.setText(config['img_path'])
        if 'output_path' in config:
            self.output_path_edit.setText(config['output_path'])

    def init_ui(self):
        self.resize(300, 400)
        layout = QVBoxLayout()  # Hauptlayout

        # Bildpfadelemente
        self.img_path_label = QLabel('Bilder-Verzeichnis', self)
        self.img_path_label.setStyleSheet('color: white')
        self.img_path_label.setFont(font)
        self.img_path_edit = QLineEdit(self)
        self.img_path_edit.setText(os.getcwd())  # Setze das aktuelle Verzeichnis als Standardtext
        self.img_path_edit.setStyleSheet('color: white')
        self.img_path_button = QPushButton('Ordner auswählen', self)
        self.img_path_button.setStyleSheet('color: white')
        self.img_path_button.clicked.connect(self.open_directory_dialog1)
        img_path_layout = QVBoxLayout()
        img_path_layout.addWidget(self.img_path_label)
        img_path_layout.addWidget(self.img_path_edit)
        img_path_layout.addWidget(self.img_path_button)

        # Blockgrößenelemente
        self.block_size_label = QLabel('Auflösung', self)
        self.block_size_label.setStyleSheet('color: white')
        self.block_size_label.setFont(font)

        self.block_size_slider = QSlider(Qt.Horizontal, self)
        self.block_size_slider.setMinimum(1)
        self.block_size_slider.setMaximum(20)
        self.block_size_slider.setValue(4)
        self.block_size_slider.setTickInterval(1)
        self.block_size_slider.setTickPosition(QSlider.TicksBelow)
        block_size_layout = QVBoxLayout()
        block_size_layout.addWidget(self.block_size_label)
        block_size_layout.addWidget(self.block_size_slider)
        self.block_size_slider.valueChanged.connect(self.update_block_size_label)

        # Ausgabepfadelemente
        self.output_path_label = QLabel('Ausgabe-Verzeichnis', self)
        self.output_path_label.setStyleSheet('color: white')
        self.output_path_label.setFont(font)
        self.output_path_edit = QLineEdit(self)
        self.output_path_edit.setText(os.getcwd())  # Setze das aktuelle Verzeichnis als Standardtext
        self.output_path_edit.setStyleSheet('color: white')
        self.output_path_button = QPushButton('Ordner auswählen', self)
        self.output_path_button.setStyleSheet('color: white')
        self.output_path_button.clicked.connect(self.open_directory_dialog2)
        output_path_layout = QVBoxLayout()
        output_path_layout.addWidget(self.output_path_label)
        output_path_layout.addWidget(self.output_path_edit)
        output_path_layout.addWidget(self.output_path_button)

        self.convert_button = QPushButton('Konvertieren', self)
        self.convert_button.setStyleSheet('color: white')
        self.convert_button.setFont(font)
        self.convert_button.clicked.connect(self.convert_clicked)

        self.bw_checkbox = QCheckBox('Schwarz-Weiß', self)
        self.bw_checkbox.setStyleSheet('color: white')

        self.negative_checkbox = QCheckBox('Negativ', self)
        self.negative_checkbox.setStyleSheet('color: white')

        self.borderless_checkbox = QCheckBox('Randlos', self)
        self.borderless_checkbox.setStyleSheet('color: white')

        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.bw_checkbox)
        checkbox_layout.addWidget(self.negative_checkbox)
        checkbox_layout.addWidget(self.borderless_checkbox)
        checkbox_layout.addStretch()

        self.author_label = QLabel('von Mario Michael Heinrich', self)
        self.author_label.setStyleSheet('color: white')
        self.author_label.setFont(font)

        layout.setSpacing(10)  # Setzt den Abstand zwischen den Widgets in Pixeln
        layout.addLayout(img_path_layout)
        layout.addStretch(1)  # Fügt einen dehnbaren Raum hinzu
        layout.addLayout(output_path_layout)
        layout.addStretch(1)
        layout.addLayout(block_size_layout)
        layout.addStretch(1)
        layout.addLayout(checkbox_layout)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.author_label)
        self.setLayout(layout)
        self.update_block_size_label(self.block_size_slider.value())

    def convert_clicked(self):
        input_directory = self.img_path_edit.text()
        output_directory = self.output_path_edit.text()
        block_size = self.block_size_slider.value()
        bw_mode = self.bw_checkbox.isChecked()
        neg_mode = self.negative_checkbox.isChecked()
        bl_mode = self.borderless_checkbox.isChecked()

        if not os.path.isdir(input_directory):
            print(
                f"Der angegebene Pfad {input_directory} ist kein gültiges Verzeichnis. Ein neuer Ordner wird erstellt.")
            os.makedirs(input_directory)

        if not os.path.isdir(output_directory):
            print(
                f"Der angegebene Pfad {output_directory} ist kein gültiges Verzeichnis. Ein neuer Ordner wird erstellt.")
            os.makedirs(output_directory)

        try:
            java_commands = process_images_in_directory(input_directory, block_size, bw_mode, neg_mode, bl_mode)
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            return

        colors_file_path = os.path.join(output_directory, "colors.java")
        generate_java_colors_file(colors_file_path)
        filename = self.get_unique_java_filename(output_directory, bw_mode, neg_mode, bl_mode)
        with open(os.path.join(output_directory, filename), "w") as f:
            for command in java_commands:
                # Fügt nach jedem Befehl ';' und zwei Zeilenumbrüche hinzu
                f.write(command + "\n\n")

        print(
            f"Die Konvertierung wurde abgeschlossen. Die Ergebnisse wurden in die Datei {filename} im Verzeichnis {output_directory} geschrieben.")

        # Speichern der Pfade nach erfolgreicher Konvertierung
        config = {
            'img_path': self.img_path_edit.text(),
            'output_path': self.output_path_edit.text(),
        }
        self.save_config(config)

        # Öffnet den Ausgabe-Ordner im Datei-Explorer
        os.startfile(output_directory)

    def update_block_size_label(self, value):
        if value == 1:
            self.block_size_label.setText(f'Auflösung = {value} (Original)')
        elif 2 <= value <= 4:
            self.block_size_label.setText(f'Auflösung = {value} (hoch)')
        elif 5 <= value <= 10:
            self.block_size_label.setText(f'Auflösung = {value} (mittel)')
        else:
            self.block_size_label.setText(f'Auflösung = {value} (niedrig)')

    def save_config(self, config):
        with open('config.json', 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                return json.load(f)
        return {}

    def get_unique_java_filename(self, directory, bw_mode, neg_mode, bl_mode):
        base_filename = "output"
        extension = ".java"
        counter = 0

        # Füge Suffixe basierend auf den Modus-Optionen hinzu
        if bw_mode:
            base_filename += "_bw"
        if neg_mode:
            base_filename += "_negativ"
        if bl_mode:
            base_filename += "_randlos"

        while True:
            if counter == 0:
                filename = f"{base_filename}{extension}"
            else:
                filename = f"{base_filename}{counter}{extension}"
            if not os.path.isfile(os.path.join(directory, filename)):
                return filename
            counter += 1

    def open_directory_dialog1(self):
        directory_path = QFileDialog.getExistingDirectory(self, 'Wählen Sie das Bilder-Verzeichnis')
        self.img_path_edit.setText(directory_path)

    def open_directory_dialog2(self):
        directory_path = QFileDialog.getExistingDirectory(self, 'Wählen Sie das Ausgabe-Verzeichnis')
        self.output_path_edit.setText(directory_path)

    def closeEvent(self, event):
        config = {}
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

        config['size'] = [self.width(), self.height()]  # GUI-Auflösung speichern

        with open('config.json', 'w') as f:
            json.dump(config, f)

    def load_gui_size(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)  # GUI-Auflösung laden
            size = config.get('size', [300, 400])
            self.resize(size[0], size[1])
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print("Die Fenstergröße konnte nicht geladen werden:", e)


app = QApplication([])
window = ImageToBlockGraphicApp()
window.show()
app.exec_()
