from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsBlurEffect, QGraphicsColorizeEffect
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt6.QtGui import QPainter, QColor, QPixmap, QTransform, QColor
from numpy import interp
import math

import tuner.utils as utility

class StrobeWheel(QWidget):
    def __init__(self, parent=None, order=0, target_frequency=None, mode='auto'):
        super().__init__(parent)
        self.setAutoFillBackground(False)

        self.tuner = parent.tuner

        self.order = order
        self.num_segments = (order + 1)  # Number of segments in the strobe wheel
        self.segment_width = round(self.width() / (2 * self.num_segments))
        self.segment_angle = 360 / self.num_segments  # Angle per segment
        
        self.segment_texture = None
        self.strobe_texture = None
        
        self.strobe_xoffset = 0
        self.strobe_max_speed = 10
        
        self.frequency = None
        self.midi = None
        self.midi_target = None
        self.midi_delta = None

        self.auto_target = True

        # Create and set the blur effect
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(0)  # Adjust the radius for the desired blur amount
        self.setGraphicsEffect(self.blur_effect)

        if target_frequency is None:
            self.target_frequency = -1
        else:
            self.target_frequency = target_frequency
            self.auto_target = False
            self.midi_target = utility.frequency_to_midi_with_cents(target_frequency)

        self.note_label = QLabel()
        self.frequency_label = QLabel()
        self.delta_label = QLabel()

        self.label_layout = QVBoxLayout(self)
        self.label_layout.addWidget(self.note_label)
        self.label_layout.addWidget(self.frequency_label)
        self.label_layout.addWidget(self.delta_label)

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

        colors_tune = [QColor(0, 255, 0), QColor(0, 20, 0)]
        colors_detune = [QColor(220, 220, 0), QColor(16, 20, 0)]
        colors_noise = [QColor(128, 128, 0), QColor(16, 20, 0)]

        deviation = abs(self.midi_delta) / 100
        factor = int(interp(deviation, [1, 0], [0, 100]))

        if deviation >= 0.5:
            foreground_color = colors_noise[0]
            background_color = colors_noise[1]
        else:
            foreground_color = self.lerp_color(deviation, colors_tune[0], colors_detune[0])
            background_color = self.lerp_color(deviation, colors_tune[1], colors_detune[1])
            

        # Paint the left half green
        painter.fillRect(0, 0, width // 2, height, QColor(foreground_color))
        
        # Paint the right half black
        painter.fillRect(width // 2, 0, width // 2, height, QColor(background_color))

        # End the painting
        painter.end()

        return pixmap
    
    def lerp_color(self, t, color1, color2):
        """
        Interpolates between two colors.
        
        :param color1: QColor, the starting color
        :param color2: QColor, the target color
        :param t: float, interpolation factor (0.0 to 1.0)
        :return: QColor, the interpolated color
        """
        if not (0.0 <= t <= 1.0):
            raise ValueError("Interpolation factor t must be between 0.0 and 1.0")

        r = color1.red() * (1 - t) + color2.red() * t
        g = color1.green() * (1 - t) + color2.green() * t
        b = color1.blue() * (1 - t) + color2.blue() * t
        a = color1.alpha() * (1 - t) + color2.alpha() * t

        return QColor(int(r), int(g), int(b), int(a))
    
    def create_strobe_texture(self, strobe_width, segment_texture):
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

    def set_strobe_texture(self, texture: QPixmap):
        """Set a custom texture for the strobe segment."""

        self.strobe_texture = texture
    
    def set_wheel_data(self, i, frequency, magnitude, auto_target=True, target_frequency=None):
        """Sets strobe parameters such as input frequency, target note and note difference for strobe movement."""

        self.auto_target = auto_target

        if self.auto_target:
            self.midi_target = utility.frequency_to_midi(frequency)
        else:
            if target_frequency is not None:
                self.midi_target = utility.frequency_to_midi_with_cents(target_frequency)
        
        self.midi = utility.frequency_to_midi_with_cents(frequency)
        self.frequency = frequency

        self.midi_delta = self.midi - self.midi_target

        radius = interp(abs(self.midi_delta), [0, 1], [4, 8])
        self.blur_effect.setBlurRadius(radius)  # Adjust the radius for the desired blur amount

        self.set_label_texts()
    
    def set_label_texts(self):
        self.note_label.text = utility.midi_to_note_name(self.midi_target)
        self.frequency_label.text = f"{round(self.frequency, 2)}"
        self.delta_label.text = f"{round(self.midi_delta, 2)}"


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.eraseRect(self.rect())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.midi_delta is None:
            self.label_layout.update()
            return
        
        speed_scale = 1000 / self.tuner.audio_processor.buffer_size

        self.strobe_xoffset += self.midi_delta * self.strobe_max_speed * speed_scale
        self.strobe_xoffset = round(self.strobe_xoffset % self.segment_width)
        self.segment_texture = self.create_segment_texture(self.segment_width, self.height())  # Size of the segment texture
        self.strobe_texture = self.create_strobe_texture(self.width(), self.segment_texture)
        
        self.setGraphicsEffect(self.blur_effect)

        transform = QTransform().translate(self.strobe_xoffset - self.segment_width, 0)
        painter.setTransform(transform)
        painter.drawPixmap(0, 0, self.strobe_texture)
        transform.reset()
        painter.end()

        self.label_layout.update()


