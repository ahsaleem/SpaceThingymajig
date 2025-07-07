from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal
from math import sqrt, cos, sin, pi

class OrbitPreviewWidget(QWidget):
    orbit_changed = pyqtSignal(float, float)  # a, e
    
    def __init__(self, planet, parent=None):
        super().__init__(parent)
        self.planet = planet
        self.a = planet.a_geo()  # Default to GEO
        self.e = 0.0  # Circular
        self.setMinimumSize(500, 300)
        self.setMaximumSize(500, 300)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
    def update_orbit(self, a, e):
        """Update the displayed orbit parameters"""
        self.a = a
        self.e = e
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate drawing area (top portion for orbit, bottom for text)
        width = self.width()
        height = self.height()
        orbit_area_height = height * 0.5  # top 50% for orbit

        # New orbit center (higher up)
        center = QPointF(width / 2, orbit_area_height / 2)

        # Scale factors - leave 10% margin within orbit area
        max_dim = min(width, orbit_area_height) * 0.9
        scale = max_dim / (2 * self.a * (1 + self.e))

        # Draw background
        painter.fillRect(self.rect(), QColor(30, 30, 40))

        # Compute orbit dimensions
        a_px = self.a * scale
        try:
            b_px = self.a * sqrt(1 - self.e**2) * scale
        except ValueError:
            b_px = self.a * scale 
        c_px = self.a * self.e * scale

        # Orbit ellipse
        orbit_rect = QRectF(center.x() - a_px + c_px,
                            center.y() - b_px,
                            2 * a_px,
                            2 * b_px)

        # Orbit path
        pen = QPen(QColor(100, 200, 255), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(orbit_rect)

        # Planet at focus
        planet_radius = max(5, self.planet.get_radius() * scale / 1000)
        painter.setBrush(QBrush(QColor(70, 120, 200)))
        painter.drawEllipse(center, planet_radius, planet_radius)

        # Periapsis and apoapsis
        pen.setColor(QColor(255, 100, 100))
        painter.setPen(pen)
        periapsis = QPointF(center.x() - a_px * (1 - self.e) + c_px, center.y())
        apoapsis = QPointF(center.x() + a_px * (1 + self.e) + c_px, center.y())
        painter.drawEllipse(periapsis, 3, 3)
        painter.drawEllipse(apoapsis, 3, 3)
        painter.drawLine(periapsis, apoapsis)

        # Draw satellite if available
        if hasattr(self, 'current_angle'):
            angle_rad = self.current_angle * pi / 180
            r = self.a * (1 - self.e**2) / (1 + self.e * cos(angle_rad))
            x = r * cos(angle_rad) * scale
            y = r * sin(angle_rad) * scale
            painter.setBrush(QBrush(Qt.yellow))
            painter.drawEllipse(QPointF(center.x() + x, center.y() + y), 4, 4)

        # Draw orbital parameters below orbit
        text_y_start = int(height * 0.55)
        line_spacing = 20
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        painter.drawText(10, text_y_start, f"Semi-major axis: {self.a:.1f} km")
        painter.drawText(10, text_y_start + line_spacing, f"Eccentricity: {self.e:.3f}")
        if self.e > 0:
            painter.drawText(10, text_y_start + 2 * line_spacing, f"Periapsis: {self.a * (1 - self.e):.1f} km")
            painter.drawText(10, text_y_start + 3 * line_spacing, f"Apoapsis: {self.a * (1 + self.e):.1f} km")
            painter.drawText(10, text_y_start + 4 * line_spacing, f"Focal distance: {self.a * self.e:.1f} km")

    
    def mousePressEvent(self, event: QMouseEvent):
        """Allow changing eccentricity by clicking"""
        if event.button() == Qt.LeftButton:
            center = QPointF(self.width()/2, self.height()/2)
            pos = event.pos()
            
            # Calculate relative position from center
            dx = pos.x() - center.x()
            dy = pos.y() - center.y()
            distance = sqrt(dx*dx + dy*dy)
            
            # Calculate maximum possible distance (apoapsis)
            max_dim = min(self.width(), self.height()) * 0.9
            max_dist = max_dim / 2
            
            # Calculate new eccentricity based on click position
            # Limit to 0.0-0.99 to avoid division by zero
            new_e = min(0.99, distance / max_dist)
            
            # Only update if significantly different
            if abs(new_e - self.e) > 0.01:
                self.e = new_e
                self.orbit_changed.emit(self.a, self.e)
                self.update()
    
    def set_current_angle(self, angle_deg):
        """Set the current angle for position indicator"""
        self.current_angle = angle_deg
        self.update()