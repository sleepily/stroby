import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from tuner.strobe_container import StrobeContainer
from tuner.spectrum_container import SpectrumContainer

class TunerWindow(QWidget):
    def __init__(self, tuner):
        super().__init__()
        self.tuner = tuner

        self.setWindowTitle("stroby")
        self.setGeometry(0, 0, 720, 720)

        self.spectrum_container = SpectrumContainer()
        self.strobe_container = StrobeContainer()

        self.tuning_button = QPushButton("Pause Tuning")
        self.tuning_button.clicked.connect(self.tuner.toggle_tuning_input)
        self.buffer_larger_button = QPushButton("Buffer x2")
        self.buffer_larger_button.clicked.connect(self.tuner.buffer_increase)
        self.buffer_smaller_button = QPushButton("Buffer //2")
        self.buffer_smaller_button.clicked.connect(self.tuner.buffer_decrease)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.tuning_button)
        button_layout.addWidget(self.buffer_larger_button)
        button_layout.addWidget(self.buffer_smaller_button)

        # strobe_layout = QVBoxLayout()
        layout.addWidget(self.strobe_container)
        layout.addWidget(self.spectrum_container)
        layout.addLayout(button_layout)

        self.setLayout(layout)
    
    def closeEvent(self, event):
        """Handle window close event to stop the worker."""
        # print("Window closed and audio worker stopped.")
        self.tuner.audio_processor.stop_audio_worker()  # Stop the worker when closing the window
        event.accept()  # Accept the close event and close the window

    def paintEvent(self, event):
        self.spectrum_container.update()
        self.strobe_container.update()
        pass

    def update_display_fft_data(self, positive_frequencies, positive_magnitudes, peaks_idx, peak_frequencies, peak_magnitudes):
        """Update the strobe effect with the FFT data."""
        # print(f"freq {positive_frequencies}")
        # print(f"peaks {peak_frequencies}")
        self.spectrum_container.set_spectrum_data(positive_frequencies, positive_magnitudes, peaks_idx)
        self.strobe_container.set_strobe_data(peak_frequencies, peak_magnitudes)
        

