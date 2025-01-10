from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush, QPainterPath
import numpy as np

class SpectrumContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self.bar_count = 3  # Example: Number of strobes
        self.strobe_height = 0  # Will be updated in paintEvent
        self.spectrum_data = None  # Holds strobe data (frequencies, magnitudes)
        self.spectrum_size = 0
        self.zoom_range = QPoint(36, 4000)
        self.peaks_idx = None

        self.max = 0

    def set_spectrum_data(self, frequencies, magnitudes, peaks_idx):
        """Set the data for the strobes and trigger a repaint."""

        self.spectrum_data = list(zip(frequencies, magnitudes))  # Combine frequencies and magnitudes
        self.highest_frequency = frequencies[len(frequencies) - 1]
        self.peaks_idx = peaks_idx
        self.max = max(magnitudes)
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        if self.spectrum_data == None:
            return  # No data to render

        if len(self.spectrum_data) == 0:
            print("warning: spectrum: FFT data empty.")
            return  # No data to render

        # Calculate strobe height based on the widget height
        self.strobe_width = 1

        self.visualize_spectrum()

    def visualize_spectrum(self):
        """Paint the strobe effects on the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clear the background
        painter.eraseRect(self.rect())

        self.spectrum_point_pairs = []
        last_point = None
        max_flag = False
        for i, (frequency, magnitude) in enumerate(self.spectrum_data):                
            point = self.calculate_spectrum_point(painter, i, frequency, magnitude)

            if last_point == None:
                last_point = point
            
            pair = (last_point, point)

            self.spectrum_point_pairs.append(pair)
            
            # Draw each strobe
            painter.drawLines(pair)
            
            last_point = point

    # TODO: retain max. magnitude for automated vertical scaling and peak hold visualization option  
    def calculate_spectrum_point(self, painter, index, frequency, magnitude):
        """Draw a single strobe effect based on frequency and magnitude."""

        if frequency <= 0.0:
            band_x = -1
        else:
            band_x = int(np.interp(np.log10(frequency), [0, 3.8], [0, self.width()]))

        band_y = int(np.interp(magnitude, [0, self.max], [self.height(), 0]))
    
        # Calculate width and position (based on frequency)
        band_point = QPoint(band_x, band_y)

        return band_point
