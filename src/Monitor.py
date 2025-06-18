from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.QtGui import QPalette, QColor, QKeyEvent
from src.Simulation import Simulation
from src.GuiConstants import GuiConstants
import sys

class Monitor(QWidget):
    def __init__(self, sim, parent=None, refresh_rate=0):
        super(Monitor, self).__init__(parent)
        
        self.m_sim = sim
        self.m_refresh_rate = refresh_rate
        
        # Setup widget appearance
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(100, 100, 100))
        palette.setColor(QPalette.Foreground, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        
        # Create labels
        self.title_label = QLabel(self)
        self.time_label = QLabel(self)
        
        # Add widgets to layout
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.time_label)
        
        # Update labels if simulation is available
        if self.m_sim is not None:
            self.title_label.setText(self.m_sim.name)
            self.time_label.setText(f"t = {self.m_sim.t} s")
        
        # Set the layout
        self.setLayout(self.main_layout)
        
        # Setup timer
        self.m_timer = QTimer()
        if self.m_refresh_rate == 0 and self.m_sim is not None:
            self.m_timer.start(int(1000 * self.m_sim.dt / self.m_sim.speed))
        else:
            self.m_timer.start(refresh_rate)
        
        # Connect signals
        self.m_timer.timeout.connect(self.update_slot)
        
        # Position the widget
        if parent:
            self.move(0, parent.height() - GuiConstants.monitorH)
            self.setMinimumSize(parent.width(), GuiConstants.monitorH)
    
    def set_simulation(self, sim):
        self.m_sim = sim
        
        if self.m_sim is not None:
            self.title_label.setText(self.m_sim.name)
            self.time_label.setText(f"t = {self.m_sim.t} s")
            
            if self.m_refresh_rate == 0:
                self.m_timer.start(int(1000 * self.m_sim.dt / self.m_sim.speed))
    
    @pyqtSlot()
    def update_slot(self):
        """Update the display with current simulation information"""
        if self.m_sim is not None:
            self.title_label.setText(self.m_sim.name)
            self.time_label.setText(f"t = {self.m_sim.t} s")
            
            if self.m_refresh_rate == 0:
                self.m_timer.setInterval(int(1000 * self.m_sim.dt / self.m_sim.speed))
    
    def on_resize(self, w, h):
        self.move(0, h - GuiConstants.monitorH)
        self.setMinimumSize(w, GuiConstants.monitorH)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            print("jcsuej")
            self.move(0, 50)