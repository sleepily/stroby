import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from tuner.strobe_container import StrobeContainer
from tuner.spectrum_container import SpectrumContainer

import tuner.utils as utility

class TunerWindow(QWidget):
    def __init__(self, tuner):
        super().__init__()
        self.tuner = tuner

        self.setWindowTitle("stroby")
        self.setGeometry(0, 0, 720, 720)

        self.desktop_container = QVBoxLayout()

        self.spectrum_container = SpectrumContainer()
        self.strobe_container = StrobeContainer(strobe_count=3)

        self.buffer_pause_button = QPushButton("Freeze Input")
        self.buffer_pause_button.clicked.connect(self.tuner.toggle_input_freeze)
        self.buffer_larger_button = QPushButton("Buffer x2")
        self.buffer_larger_button.clicked.connect(self.tuner.buffer_increase)
        self.buffer_smaller_button = QPushButton("Buffer //2")
        self.buffer_smaller_button.clicked.connect(self.tuner.buffer_decrease)

        graphics_buttons_container = QHBoxLayout()
        graphics_buttons_container.addWidget(self.buffer_pause_button)
        graphics_buttons_container.addWidget(self.buffer_larger_button)
        graphics_buttons_container.addWidget(self.buffer_smaller_button)

        # TODO: break out, include octave scrolling
        scale_buttons_panel = QHBoxLayout()
        scale_buttons = []
        for i in range(12):
            button_midi = utility.frequency_to_midi(440) + i
            button_text = utility.midi_to_note_name(button_midi)

            is_sharp = '#' in button_text  # Simplified sharp check
            button = QPushButton(button_text)
            button.setStyleSheet(f"background-color: white; color: black;")

            if is_sharp:
                button.setStyleSheet(f"background-color: black; color: white;")
            
            button.clicked.connect(lambda _, midi=button_midi: self.strobe_container.set_target(midi))
            scale_buttons.append(button)
            scale_buttons_panel.addWidget(button)

        # strobe_layout = QVBoxLayout()
        self.desktop_container.addWidget(self.strobe_container)
        self.desktop_container.addWidget(self.spectrum_container)
        self.desktop_container.addLayout(scale_buttons_panel)
        self.desktop_container.addLayout(graphics_buttons_container)

        # TODO: break out into separate function
        self.setLayout(self.desktop_container)
    
    def closeEvent(self, event):
        """Handle window close event to stop the worker."""
        # print("Window closed and audio worker stopped.")
        self.tuner.audio_processor.stop_audio_worker()  # Stop the worker when closing the window
        event.accept()  # Accept the close event and close the window

    def paintEvent(self, event):
        # print("updating ui")
        self.spectrum_container.update()
        self.strobe_container.update()
        pass

    def update_display_fft_data(self, data):
        """Update the strobe effect with the FFT data."""
        # print(f"freq {positive_frequencies}")
        # print(f"peaks {peak_frequencies}")
        positive_frequencies, positive_magnitudes, peaks_idx, peak_frequencies, peak_magnitudes = data
        self.spectrum_container.set_spectrum_data(positive_frequencies, positive_magnitudes, peaks_idx)
        self.strobe_container.set_strobe_data(peak_frequencies, peak_magnitudes)
        

