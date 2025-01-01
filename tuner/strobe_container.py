import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush

import tuner.utils as utility
from tuner.strobe_wheel import StrobeWheel

class StrobeContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.strobe_count = 3  # Example: Number of strobes
        self.strobe_height = 0  # Will be updated in paintEvent
        self.strobe_data = None # Holds strobe data (frequencies, magnitudes)
        self.strobe_wheels = None
        
    
    def reset_strobe_wheels(self):
        self.strobe_wheels = []

        for i in range(self.strobe_count):
            self.strobe_wheels.append(StrobeWheel(self, i))

        strobe_layout = QVBoxLayout()
        
        for wheel in self.strobe_wheels:
            strobe_layout.addWidget(wheel)

        self.setLayout(strobe_layout)

    def set_strobe_data(self, frequencies, magnitudes):
        """Set the data for the strobes and trigger a repaint."""
        self.strobe_data = list(zip(frequencies, magnitudes))  # Combine frequencies and magnitudes

        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        """Paint the strobe effects on the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clear the background
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        if self.strobe_data == None:
            # print("waiting for strobe data...")
            return  # No data to render

        # Calculate strobe height based on the widget height
        self.strobe_height = self.height() // self.strobe_count

        if len(self.strobe_data) == 0:
            print(f"strobe data size 0. aborting...")
            return

        for i, (frequency, magnitude) in enumerate(self.strobe_data[-self.strobe_count:]):
            # print(f"setting wheel #{i} data: {round(frequency, 2)} Hz @{round(1 - magnitude, 1)}dB")
            self.strobe_wheels[i].set_wheel_data(i, frequency, magnitude)

    def draw_strobe_old(self, painter, index, frequency, magnitude):
        """Draw a single strobe effect based on frequency and magnitude."""
        # Calculate strobe's vertical position (based on the index)
        strobe_x = int(self.width()/2)
        strobe_y = int (self.strobe_height * index) + 20

        strobe_delta = utility.frequency_to_midi(frequency) - utility.frequency_to_midi_with_cents(frequency)
        # print(strobe_delta)

        # Color based on frequency and magnitude (example logic)
        color_intensity = int(np.interp(magnitude, [0, 1000], [0, 255]))  # Adjust the magnitude range as needed
        color = QColor(color_intensity, 255 - color_intensity, 0)

        # Calculate width and position (based on frequency)
        strobe_width = int(frequency % self.width())  # Just an example of how frequency can affect width
        strobe_rect = QRect(strobe_width, strobe_y, 10, self.strobe_height)

        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawText(strobe_x, strobe_y, f"{round(frequency, 2)}")
        painter.drawText(strobe_x, strobe_y+14, f"@{round(strobe_delta, 2)}")
