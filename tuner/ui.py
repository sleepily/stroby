import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from tuner.strobe_container import StrobeContainer, StrobeSettingsPanel
from tuner.spectrum_container import SpectrumContainer

import tuner.utils as utility

class TunerWindow(QWidget):
    def __init__(self, tuner):
        super().__init__()
        self.tuner = tuner

        self.setWindowTitle("stroby")
        self.setGeometry(0, 0, 360, 360)

        self.desktop_container = QVBoxLayout()

        self.spectrum_container = SpectrumContainer()
        self.spectrum_container.setFixedHeight(80)

        self.strobe_container = StrobeContainer(self, strobe_count=3)
        self.strobe_settings = StrobeSettingsPanel(self)

        self.buffer_pause_button = QPushButton("Freeze Input")
        self.buffer_pause_button.clicked.connect(self.tuner.toggle_input_freeze)

        self.buffer_larger_button = QPushButton("Buffer x2")
        self.buffer_larger_button.setFixedWidth(60)
        self.buffer_larger_button.clicked.connect(self.tuner.buffer_increase)

        self.buffer_smaller_button = QPushButton("Buffer //2")
        self.buffer_smaller_button.setFixedWidth(60)
        self.buffer_smaller_button.clicked.connect(self.tuner.buffer_decrease)

        graphics_buttons_container = QHBoxLayout()
        graphics_buttons_container.addWidget(self.buffer_pause_button)
        graphics_buttons_container.addWidget(self.buffer_larger_button)
        graphics_buttons_container.addWidget(self.buffer_smaller_button)


        # strobe_layout = QVBoxLayout()
        self.desktop_container.addWidget(self.strobe_container)
        self.desktop_container.addWidget(self.spectrum_container)
        self.desktop_container.addWidget(self.strobe_settings)
        self.desktop_container.addLayout(graphics_buttons_container)

        # TODO: break out into separate function
        self.setLayout(self.desktop_container)
    
    def closeEvent(self, event):
        """Handle window close event to stop the worker."""
        self.tuner.audio_processor.stop_audio_worker()  # Stop the worker when closing the window
        event.accept()  # Accept the close event and close the window

    def paintEvent(self, event):
        self.spectrum_container.update()
        self.strobe_container.update()
        pass

    def update_display_fft_data(self, data):
        """Update the strobe effect with the FFT data."""
        
        positive_frequencies, positive_magnitudes, peaks_idx, peak_frequencies, peak_magnitudes = data
        self.spectrum_container.set_spectrum_data(positive_frequencies, positive_magnitudes, peaks_idx)
        self.strobe_container.set_strobe_data(peak_frequencies, peak_magnitudes)
        

