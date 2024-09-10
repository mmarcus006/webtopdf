import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QSpinBox, QCheckBox, QComboBox, 
                             QTextEdit, QProgressBar, QFileDialog, QLabel, QDoubleSpinBox, 
                             QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon
import asyncio
from web_to_pdf_converter import WebToPDFConverter, main as converter_main

class WebToPDFConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web to PDF Converter")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.loadSettings()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # URL Input
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL or path to URL list file")
        url_layout.addWidget(self.url_input)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browseURLs)
        url_layout.addWidget(self.browse_button)
        main_layout.addLayout(url_layout)

        # Options Panel
        options_group = QGroupBox("Options")
        options_layout = QFormLayout()

        self.concurrency_spinner = QSpinBox()
        self.concurrency_spinner.setRange(1, 10)
        self.concurrency_spinner.setValue(5)
        options_layout.addRow("Concurrency:", self.concurrency_spinner)

        self.rate_limit_spinner = QDoubleSpinBox()
        self.rate_limit_spinner.setRange(0.1, 10)
        self.rate_limit_spinner.setValue(1.0)
        self.rate_limit_spinner.setSingleStep(0.1)
        options_layout.addRow("Rate Limit (req/s):", self.rate_limit_spinner)

        self.css_selector_input = QLineEdit()
        options_layout.addRow("CSS Selector:", self.css_selector_input)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Output Directory
        output_layout = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Output Directory")
        output_layout.addWidget(self.output_input)
        self.output_browse_button = QPushButton("Browse")
        self.output_browse_button.clicked.connect(self.browseOutputDir)
        output_layout.addWidget(self.output_browse_button)
        main_layout.addLayout(output_layout)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Conversion")
        self.start_button.clicked.connect(self.startConversion)
        button_layout.addWidget(self.start_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancelConversion)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

    def browseURLs(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select URL List File", "", "Text Files (*.txt)")
        if file_name:
            self.url_input.setText(file_name)

    def browseOutputDir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_input.setText(directory)

    def startConversion(self):
        self.setUIEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_output.clear()

        url = self.url_input.text()
        output_dir = self.output_input.text()
        concurrency = self.concurrency_spinner.value()
        rate_limit = self.rate_limit_spinner.value()
        css_selector = self.css_selector_input.text() if self.css_selector_input.text() else None

        self.converter_thread = ConverterThread(url, output_dir, concurrency, rate_limit, css_selector)
        self.converter_thread.progressUpdate.connect(self.updateProgress)
        self.converter_thread.logUpdate.connect(self.updateLog)
        self.converter_thread.conversionComplete.connect(self.conversionFinished)
        self.converter_thread.start()

    def cancelConversion(self):
        if hasattr(self, 'converter_thread'):
            self.converter_thread.stop()
        self.updateLog("Conversion cancelled by user.")
        self.conversionFinished()

    def updateProgress(self, value):
        self.progress_bar.setValue(value)

    def updateLog(self, message):
        self.log_output.append(message)

    def conversionFinished(self):
        self.setUIEnabled(True)
        self.cancel_button.setEnabled(False)
        self.saveSettings()

    def setUIEnabled(self, enabled):
        for widget in [self.url_input, self.browse_button, self.concurrency_spinner,
                       self.rate_limit_spinner, self.css_selector_input, self.output_input,
                       self.output_browse_button, self.start_button]:
            widget.setEnabled(enabled)

    def loadSettings(self):
        settings = QSettings("WebToPDFConverter", "GUI")
        self.url_input.setText(settings.value("url", ""))
        self.output_input.setText(settings.value("output_dir", ""))
        self.concurrency_spinner.setValue(int(settings.value("concurrency", 5)))
        self.rate_limit_spinner.setValue(float(settings.value("rate_limit", 1.0)))
        self.css_selector_input.setText(settings.value("css_selector", ""))

    def saveSettings(self):
        settings = QSettings("WebToPDFConverter", "GUI")
        settings.setValue("url", self.url_input.text())
        settings.setValue("output_dir", self.output_input.text())
        settings.setValue("concurrency", self.concurrency_spinner.value())
        settings.setValue("rate_limit", self.rate_limit_spinner.value())
        settings.setValue("css_selector", self.css_selector_input.text())

class ConverterThread(QThread):
    progressUpdate = pyqtSignal(int)
    logUpdate = pyqtSignal(str)
    conversionComplete = pyqtSignal()

    def __init__(self, url, output_dir, concurrency, rate_limit, css_selector):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.concurrency = concurrency
        self.rate_limit = rate_limit
        self.css_selector = css_selector
        self.running = True

    def run(self):
        asyncio.run(self.run_conversion())

    async def run_conversion(self):
        try:
            await converter_main(self.url, self.output_dir, self.concurrency, self.rate_limit, self.css_selector,
                                 progress_callback=self.update_progress, log_callback=self.update_log)
        except Exception as e:
            self.logUpdate.emit(f"Conversion error: {str(e)}")
        finally:
            self.conversionComplete.emit()

    def update_progress(self, value):
        self.progressUpdate.emit(value)

    def update_log(self, message):
        self.logUpdate.emit(message)

    def stop(self):
        self.running = False

def main():
    app = QApplication(sys.argv)
    window = WebToPDFConverterGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()