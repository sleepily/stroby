from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt6.QtGui import QPainter, QColor, QPixmap, QTransform
import math

import tuner.utils as utility

class StrobeWheel(QWidget):
    def __init__(self, parent=None, order=0):
        super().__init__(parent)
        self.setAutoFillBackground(False)

        self.order = order
        self.num_segments = (order + 1)  # Number of segments in the strobe wheel
        self.segment_width = round(self.width() / (2 * self.num_segments))
        self.segment_angle = 360 / self.num_segments  # Angle per segment
        
        self.segment_texture = None
        self.strobe_texture = None
        
        self.strobe_delta = 0
        self.strobe_xoffset = 0
        self.strobe_max_speed = 50

        # print(f"wheel width {self.width()}")
        # print(f"wheel height {self.height()}")
        # print(f"segment width {self.segment_width}")

        # print(f"wheel #{self.order} init")

    def create_segment_texture(self, width, height, antialiasing=True):
        self.num_segments = (self.order + 1)  # Number of segments in the strobe wheel
        self.segment_width = round(self.width() / (2 * self.num_segments))

        pixmap = QPixmap(width, height)

        # Create a QPainter object to paint on the pixmap
        painter = QPainter(pixmap)
        
        # Set the render hint for smoothness (optional)
        # painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Get the size of the pixmap
        width = pixmap.width()
        height = pixmap.height()

        # Paint the left half green
        painter.fillRect(0, 0, width // 2, height, QColor(0, 255, 0))  # Green
        
        # Paint the right half black
        painter.fillRect(width // 2, 0, width // 2, height, QColor(0, 0, 0))  # Black

        # End the painting
        painter.end()

        return pixmap

    def set_strobe_texture(self, texture: QPixmap):
        """Set a custom texture for the strobe segment."""
        self.strobe_texture = texture
    
    def set_wheel_data(self, i, frequency, magnitude, auto_target=True, target_frequency=None):
        if auto_target:
            target_midi = utility.frequency_to_midi(frequency)
        else:
            print(f"wheel #{i}: no target frequency provided. did you mean to use auto=True?")
            target_midi = utility.frequency_to_midi_with_cents(target_frequency)
        
        midi = utility.frequency_to_midi_with_cents(frequency)

        self.strobe_delta = midi - target_midi

    def paintEvent(self, event):
        # print(f"strobe {self.order} paintEvent")
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clear the background with black color
        painter.fillRect(self.rect(), QColor(100, 100, 100))

        # Calculate the center of the widget (strobe wheel center)
        # center = self.rect().center()
        # radius = min(self.width(), self.height()) // 3  # Radius of the strobe wheel

        self.strobe_xoffset += self.strobe_delta * self.strobe_max_speed

        self.strobe_xoffset = round(self.strobe_xoffset % self.segment_width)

        self.segment_texture = self.create_segment_texture(self.segment_width, self.height())  # Size of the segment texture

        self.strobe_texture = self.repeat_segment_texture_on_strobe(self.width(), self.segment_texture)
        
        transform = QTransform().translate(self.strobe_xoffset - self.segment_width, 0)
        painter.setTransform(transform)
        painter.drawPixmap(0, 0, self.strobe_texture)

    def repeat_segment_texture_on_strobe(self, strobe_width, segment_texture):
        # Create a QPixmap that will hold the full strobe texture (width x height)
        strobe_texture = QPixmap(strobe_width + segment_texture.width(), segment_texture.height())

        # Start painting on the strobe texture
        painter = QPainter(strobe_texture)
        
        # Calculate how many segments fit across the width
        num_segments = round(strobe_width / segment_texture.width())
        
        # Draw the segment texture repeatedly across the entire width of the strobe texture
        for i in range(num_segments + 1):
            # Draw the segment at the correct horizontal position
            painter.drawPixmap(i * segment_texture.width(), 0, segment_texture)
        
        # End painting
        painter.end()

        # Return the resulting strobe texture
        return strobe_texture