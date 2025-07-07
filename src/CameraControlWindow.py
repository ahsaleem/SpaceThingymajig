from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QFormLayout, QSlider, QColorDialog, QCheckBox,
                            QComboBox, QPushButton, QLabel, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QPixmap

class CameraControlWindow(QDialog):
    camera_target_changed = pyqtSignal(str) 
    light_settings_changed = pyqtSignal(float, list)
    def __init__(self, simulation_display, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Camera Control")
        self.setModal(True)
        self.simulation_display = simulation_display
        self.custom_color = [1.0, 1.0, 1.0]
        self.layout = QVBoxLayout()
        
        # Target selection group
        target_group = QGroupBox("Camera Target")
        target_layout = QFormLayout()
        
        self.target_combo = QComboBox()
        self.target_combo.addItem("Planet (default)")
        
        
        # Get satellites from the simulation display
        if (hasattr(simulation_display, 'sim')) and simulation_display.sim() is not None:
            sim = simulation_display.sim()
            for i in range(sim.nsat()):
                self.target_combo.addItem(sim.sat(i).get_name())
        
        target_layout.addRow("Focus on:", self.target_combo)
        target_group.setLayout(target_layout)
        
        # Camera settings group
        settings_group = QGroupBox("Camera Settings")
        settings_layout = QFormLayout()
        settings_layout.addRow(QLabel("Additional camera controls"))
        settings_group.setLayout(settings_layout)

        light_group = QGroupBox("Light Settings")
        light_layout = QFormLayout()

        # Intensity slider (keep existing)
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(30, 500)
        self.intensity_slider.setValue(100)
        self.intensity_value = QLabel("100%")
        self.intensity_slider.valueChanged.connect(
            lambda v: self.intensity_value.setText(f"{v}%"))
        
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(self.intensity_slider)
        intensity_layout.addWidget(self.intensity_value)
        light_layout.addRow("Intensity:", intensity_layout)

        # Color Temperature (keep existing but simplified)
        self.color_temp = QComboBox()
        self.color_temp.addItems([
            "5500K (Pure White)", 
            "3000K (Warm Yellow)", 
            "7000K (Cool Blue)",
            "2000K (Sunset Orange)"
        ])
        light_layout.addRow("Color Temperature:", self.color_temp)

        # Add new Custom Color option as a separate control
        self.use_custom_color = QCheckBox("Use Custom Color")
        self.use_custom_color.stateChanged.connect(self.on_custom_color_toggled)
        
        self.custom_color_button = QPushButton("Pick Color")
        self.custom_color_button.setEnabled(False)
        self.custom_color_button.clicked.connect(self.pick_custom_color)
        
        # Color preview (shared between both options)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(20, 20)
        self.update_color_preview()
        
        # Layout for custom color controls
        custom_color_layout = QHBoxLayout()
        custom_color_layout.addWidget(self.use_custom_color)
        custom_color_layout.addWidget(self.custom_color_button)
        custom_color_layout.addWidget(self.color_preview)
        custom_color_layout.addStretch()
        
        light_layout.addRow(custom_color_layout)
        light_group.setLayout(light_layout)
        self.layout.addWidget(light_group)

        # Buttons
        self.apply_button = QPushButton("Apply")
        self.cancel_button = QPushButton("Cancel")
        
        # Layout
        self.layout.addWidget(target_group)
        self.layout.addWidget(settings_group)
        self.layout.addWidget(self.apply_button)
        self.layout.addWidget(self.cancel_button)
        
        self.setLayout(self.layout)
        
        # Connections
        self.apply_button.clicked.connect(self.apply_changes)
        self.cancel_button.clicked.connect(self.reject)
        self.intensity_slider.valueChanged.connect(self.update_color_preview)
        self.color_temp.currentIndexChanged.connect(self.update_color_preview)
    
    def apply_changes(self):
        selected_target = self.target_combo.currentText()
        if selected_target != "Planet (default)":
            self.camera_target_changed.emit(selected_target)
        else:
            self.camera_target_changed.emit("") 
        
        # Get current light settings and emit signal
        intensity = self.intensity_slider.value() / 100.0  # Convert from % to 0.0-3.0
        color = self.get_color_from_temp()
        self.light_settings_changed.emit(intensity, color)
        
        self.accept()


    def update_color_preview(self):
        color = self.get_color_from_temp()
        pixmap = QPixmap(20, 20)
        pixmap.fill(QColor(*[int(c*255) for c in color]))
        self.color_preview.setPixmap(pixmap)
        
    def get_color_from_temp(self):
        """More pronounced color differences"""
        temp = self.color_temp.currentText()
        if "3000" in temp: return [1.0, 0.85, 0.6]    # Strong warm yellow
        elif "7000" in temp: return [0.7, 0.8, 1.0]   # Noticeable cool blue
        elif "2000" in temp: return [1.0, 0.6, 0.3]   # Vibrant orange
        return [1.0, 1.0, 1.0]  # Pure white
    
    def on_custom_color_toggled(self, state):
        """Enable/disable custom color picker based on checkbox"""
        self.custom_color_button.setEnabled(state == Qt.Checked)
        self.color_temp.setEnabled(state != Qt.Checked)
        self.update_color_preview()
    
    def pick_custom_color(self):
        """Open color dialog to pick custom light color"""
        color = QColorDialog.getColor(
            initial=QColor(
                int(self.custom_color[0] * 255),
                int(self.custom_color[1] * 255),
                int(self.custom_color[2] * 255)
            ),
            parent=self,
            title="Select Light Color"
        )
        
        if color.isValid():
            self.custom_color = [
                color.red() / 255.0,
                color.green() / 255.0,
                color.blue() / 255.0
            ]
            self.update_color_preview()
    
    def update_color_preview(self):
        """Update the color preview based on current selection"""
        if self.use_custom_color.isChecked():
            color = self.custom_color
        else:
            color = self.get_color_from_temp()
        
        pixmap = QPixmap(20, 20)
        pixmap.fill(QColor(*[int(c*255) for c in color]))
        self.color_preview.setPixmap(pixmap)
    
    def get_color_from_temp(self):
        """Get color based on temperature selection"""
        temp = self.color_temp.currentText()
        if "3000" in temp: return [1.0, 0.85, 0.6]    # Warm yellow
        elif "7000" in temp: return [0.7, 0.8, 1.0]   # Cool blue
        elif "2000" in temp: return [1.0, 0.6, 0.3]   # Sunset orange
        return [1.0, 1.0, 1.0]  # Pure white
    
    def apply_changes(self):
        """Apply all changes when OK is clicked"""
        selected_target = self.target_combo.currentText()
        if selected_target != "Planet (default)":
            self.camera_target_changed.emit(selected_target)
        else:
            self.camera_target_changed.emit("") 
        
        # Get current settings
        intensity = self.intensity_slider.value() / 100.0
        
        # Get color based on selection
        if self.use_custom_color.isChecked():
            color = self.custom_color
        else:
            color = self.get_color_from_temp()
        
        # Emit signal with updated settings
        self.light_settings_changed.emit(intensity, color)
        self.accept()