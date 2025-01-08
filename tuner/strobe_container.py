import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush
from math import sin, cos, pi

import tuner.utils as utility
from tuner.strobe_wheel import StrobeWheel

class StrobeContainer(QWidget):
    def __init__(self, parent=None, strobe_count=3):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.tuner = parent.tuner
        self.strobe_count = strobe_count
        self.strobe_height = 0  # Will be updated in paintEvent
        self.strobe_data = None # Holds strobe data (frequencies, magnitudes)
        self.strobe_wheels = None
    
    def reset_strobe_wheels(self):
        self.strobe_wheels = []

        for i in range(self.strobe_count):
            self.strobe_wheels.append(StrobeWheel(self, i, target_frequency=440))

        strobe_layout = QVBoxLayout(self)
        
        for wheel in self.strobe_wheels:
            strobe_layout.addWidget(wheel)

        self.setLayout(strobe_layout)

    def set_strobe_data(self, frequencies, magnitudes):
        """Set the data for the strobes and trigger a repaint."""
        self.strobe_data = list(zip(frequencies, magnitudes))  # Combine frequencies and magnitudes
        self.buffer_size = len(frequencies)

        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        """Paint the strobe effects on the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clear the background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        if self.strobe_data == None:
            return  # No data to render

        # Calculate strobe height based on the widget height
        self.strobe_height = round(self.height() / self.strobe_count)

        if len(self.strobe_data) == 0:
            print(f"warning: strobe FFT data empty.")
            return

        for i, (frequency, magnitude) in enumerate(self.strobe_data[-self.strobe_count:]):
            wheel = self.strobe_wheels[i]
            wheel.set_wheel_data(i, frequency, magnitude, wheel.auto_target)
        
    def set_target_midi(self, target_midi):
        for i, (frequency, magnitude) in enumerate(self.strobe_data[-self.strobe_count:]):
            f = utility.midi_to_frequency(target_midi)
            self.strobe_wheels[i].set_wheel_data(i, frequency, magnitude, auto_target=False, target_frequency=f)

class StrobeSettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tuner = parent.tuner

        self.panel = QHBoxLayout()
        self.setMinimumHeight(200)
        self.setMinimumWidth(400)

        self.note_wheel_widget = NoteWheel(self)
        self.note_wheel_controls = NoteWheelControls(self)

        self.panel.addWidget(self.note_wheel_widget)
        self.panel.addWidget(self.note_wheel_controls)

        self.setLayout(self.panel)

    def paintEvent(self, event):
        """Paint the strobe effects on the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

class NoteWheel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tuner = parent.tuner

        self.setFixedSize(180, 180)

        self.note_buttons = [None] * 12

        self.note_names = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        self.radius = 70  # Radius of the circle
        self.octave = 4

        self.label = QLabel("A4", self)
        self.label.setStyleSheet("font-size: 40px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(self.rect().center().x() - 50, self.rect().center().y() - 50, 100, 100)

        for i, note_name in enumerate(self.note_names):
            # Calculate angle for each button (12 notes = 360 degrees = 2π radians)
            angle = (2 * pi / len(self.note_names)) * i

            center = self.rect().center()
            # Calculate button position
            x = center.x() + self.radius * cos(angle) - 15  # Subtract half button width for centering
            y = center.y() + self.radius * sin(angle) - 15  # Subtract half button height for centering

            is_sharp = '#' in note_name

            self.note_buttons[i] = QPushButton(note_name, self)
            self.note_buttons[i].setGeometry(QRect(int(x), int(y), 30, 30))  # Position and size

            style_circle = "border-radius: 15px;"
            style_key_colors = f"background-color: white; color: black;" if not is_sharp else f"background-color: black; color: white;"
            style_font = f"font-size: 20px;"

            self.note_buttons[i].setStyleSheet(style_circle + style_key_colors + style_font)
            midi = utility.semitone_to_midi((i + 9)%12, octave=self.octave)
            
            self.note_buttons[i].clicked.connect(lambda _, m=midi: self.tuner.set_target(m))  # Pass note to slot

class NoteWheelControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMaximumSize(100, 100)

        self.incremental_buttons = [None] * 4
        self.incremental_buttons[0] = QPushButton("+1", self)
        self.incremental_buttons[1] = QPushButton("-1", self)
        self.incremental_buttons[2] = QPushButton("+12", self)
        self.incremental_buttons[3] = QPushButton("-12", self)

        self.st_label = QLabel("semitones")
        self.st_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.box = QGridLayout(self)

        self.box.addWidget(self.incremental_buttons[0], 0, 0)
        self.box.addWidget(self.incremental_buttons[1], 2, 0)
        self.box.addWidget(self.st_label,               1, 0, 1, 2)
        self.box.addWidget(self.incremental_buttons[2], 0, 1)
        self.box.addWidget(self.incremental_buttons[3], 2, 1)
        
        self.setLayout(self.box)