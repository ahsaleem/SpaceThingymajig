from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QFormLayout, QComboBox,
                           QPushButton, QLineEdit, QDoubleSpinBox, QMessageBox, QWidget, QScrollArea)
from PyQt5.QtCore import pyqtSlot, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QFormLayout,
                           QPushButton, QLineEdit, QDoubleSpinBox, QMessageBox,
                           QHBoxLayout, QLabel, QFileDialog)
from PyQt5.QtGui import QPixmap
from src.OrbitPreviewWidget import OrbitPreviewWidget
import os
import math
from src.Constants import Constants
from src.Satellite import Satellite
from src.Planet import Planet
from src.NORAD.TLE_Importer import TLEImporter

class SatelliteWindow(QDialog):
    """
    Dialog for configuring a satellite in the simulation
    """
    
    def __init__(self, is_new, sat, planet, simulation = None, parent=None):
        """
        Initialize the satellite configuration dialog
        
        Args:
            is_new (bool): True if creating a new satellite, False if editing
            sat (Satellite): The satellite to configure
            planet (Planet): The planet the satellite orbits
            simulation (Simulation, optional): Current simulation. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super(SatelliteWindow, self).__init__(parent)
        
        self.m_is_new = is_new
        self.m_sat = sat
        self.m_planet = planet
        self.m_simulation = simulation

        self.setModal(True)
        self.setWindowTitle("Configure satellite")
        self.setFixedSize(520, 700)  # Fixed size for scrollable window

        # Outer layout that contains everything
        outer_layout = QVBoxLayout(self)

        # Scroll area setup
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Scrollable container widget and layout
        scroll_content = QWidget()
        self.main_layout = QVBoxLayout(scroll_content) 
        self.sat_frame = QGroupBox("General information", self)
        self.orb_frame = QGroupBox("Orbit", self)
        self.att_frame = QGroupBox("Attitude", self)
        
        # Add frames to layout
        self.main_layout.addWidget(self.sat_frame)
        self.main_layout.addWidget(self.orb_frame)
        self.main_layout.addWidget(self.att_frame)
       
        # Create form layouts
        self.sat_form = QFormLayout(self.sat_frame)
        self.orb_form = QFormLayout(self.orb_frame)
        self.att_form = QFormLayout(self.att_frame)
        
        # General information section
        self.sat_name_field = QLineEdit()
        self.sat_form.addRow("Satellite name:", self.sat_name_field)
        # Set validator to prevent spaces and brackets
        filter_regex = QRegExp("^[^/\\[\\] ]+$")
        validator = QRegExpValidator(filter_regex)
        self.sat_name_field.setValidator(validator)
        if is_new:
            self.parent_body_group = QGroupBox("Parent Body")
            self.parent_body_layout = QFormLayout()
            
            self.parent_type_combo = QComboBox()
            self.parent_type_combo.addItem("Planet", "planet")
            self.parent_type_combo.addItem("Satellite", "satellite")
            self.parent_body_layout.addRow("Parent type:", self.parent_type_combo)
            
            self.parent_sat_combo = QComboBox()
            self.parent_sat_combo.setEnabled(False)  # Disabled by default (planet selected)
            
            # Populate satellite list if we have a simulation
            if self.m_simulation:
                for i in range(self.m_simulation.nsat()):
                    sat = self.m_simulation.sat(i)
                    self.parent_sat_combo.addItem(sat.get_name(), sat)
            
            self.parent_body_layout.addRow("Parent satellite:", self.parent_sat_combo)
            
            # Connect signal to enable/disable satellite combo
            self.parent_type_combo.currentTextChanged.connect(self.on_parent_type_changed)
            
            self.parent_body_group.setLayout(self.parent_body_layout)
            self.sat_form.addRow(self.parent_body_group)
        self.import_button = QPushButton("Import satellite")
        self.sat_form.addWidget(self.import_button)


        # NORAD ID field and import button
        self.norad_id_field = QLineEdit()
        self.import_from_norad_button = QPushButton("Import from NORAD ID")
        self.sat_form.addRow("NORAD ID:", self.norad_id_field)
        self.sat_form.addWidget(self.import_from_norad_button)
        
        # Connect NORAD button
        self.import_from_norad_button.clicked.connect(self.import_from_norad_slot)
        
        # Semi-major axis
        self.a_box = QDoubleSpinBox()
        self.a_box.setDecimals(3)
        self.a_box.setSingleStep(1.0)
        self.a_box.setMinimum(self.m_planet.get_radius())
        self.a_box.setMaximum(Constants.maxSatA)
        self.a_box.setToolTip(f"[{self.a_box.minimum()}, {self.a_box.maximum()}]")
        self.orb_form.addRow("Semimajor axis (km):", self.a_box)
        
        # Eccentricity
        self.e_box = QDoubleSpinBox()
        self.e_box.setDecimals(8)
        self.e_box.setSingleStep(0.01)
        self.e_box.setMinimum(0.0)
        self.e_box.setMaximum(0.999)
        self.e_box.setToolTip(f"[{self.e_box.minimum()}, {self.e_box.maximum()}]")
        self.orb_form.addRow("Eccentricity:", self.e_box)
        
        # Inclination
        self.i_box = QDoubleSpinBox()
        self.i_box.setDecimals(4)
        self.i_box.setSingleStep(0.1)
        self.i_box.setMinimum(0.0)
        self.i_box.setMaximum(Constants.pi)
        self.i_box.setToolTip(f"[{self.i_box.minimum()}, {self.i_box.maximum()}]")
        self.orb_form.addRow("Inclination (rad):", self.i_box)
        
        # Longitude of the ascending node
        self.om_box = QDoubleSpinBox()
        self.om_box.setDecimals(4)
        self.om_box.setSingleStep(0.1)
        self.om_box.setMinimum(0.0)
        self.om_box.setMaximum(Constants.twopi)
        self.om_box.setToolTip(f"[{self.om_box.minimum()}, {self.om_box.maximum()}]")
        self.orb_form.addRow("Longitude of the ascending node (rad):", self.om_box)
        
        # Argument of periapsis
        self.om_small_box = QDoubleSpinBox()
        self.om_small_box.setDecimals(4)
        self.om_small_box.setSingleStep(0.1)
        self.om_small_box.setMinimum(0.0)
        self.om_small_box.setMaximum(Constants.twopi)
        self.om_small_box.setToolTip(f"[{self.om_small_box.minimum()}, {self.om_small_box.maximum()}]")
        self.orb_form.addRow("Argument of periapsis (rad):", self.om_small_box)
        
        # Epoch
        self.tp_box = QDoubleSpinBox()
        self.tp_box.setDecimals(4)
        self.tp_box.setSingleStep(1.0)
        period = 1.0 / Constants.twopi * math.sqrt(pow(self.a_box.value(), 3.0) / self.m_planet.get_mu())
        self.tp_box.setRange(-period, period)
        self.tp_box.setToolTip(f"[{self.tp_box.minimum()}, {self.tp_box.maximum()}]")
        self.orb_form.addRow("Epoch (s) - can be negative:", self.tp_box)

        self.orbit_preview = OrbitPreviewWidget(self.m_planet)
        self.orbit_preview.setMinimumSize(300, 300)
        self.orb_form.addRow(self.orbit_preview)
    
        self.a_box.valueChanged.connect(self.update_orbit_preview)
        self.e_box.valueChanged.connect(self.update_orbit_preview)
        
        self.orbit_preview.orbit_changed.connect(self.on_preview_changed)

        self.rx_box = QDoubleSpinBox()
        self.rx_box.setRange(-360, 360)  # Degrees for user input
        self.rx_box.setDecimals(1)
        self.rx_box.setSuffix("°")
        self.rx_box.valueChanged.connect(self.update_attitude)
        self.att_form.addRow("Rotation X:", self.rx_box)

        # Rotation around Y
        self.ry_box = QDoubleSpinBox()
        self.ry_box.setRange(-360, 360)
        self.ry_box.setDecimals(1)
        self.ry_box.setSuffix("°")
        self.ry_box.valueChanged.connect(self.update_attitude)
        self.att_form.addRow("Rotation Y:", self.ry_box)

        # Rotation around Z
        self.rz_box = QDoubleSpinBox()
        self.rz_box.setRange(-360, 360)
        self.rz_box.setDecimals(1)
        self.rz_box.setSuffix("°")
        self.rz_box.valueChanged.connect(self.update_attitude)
        self.att_form.addRow("Rotation Z:", self.rz_box)
        if not is_new:
            # Convert radians to degrees for display
            self.rx_box.setValue(math.degrees(self.m_sat.get_rx()))
            self.ry_box.setValue(math.degrees(self.m_sat.get_ry()))
            self.rz_box.setValue(math.degrees(self.m_sat.get_rz()))
        else:
            # Default to zero rotation
            self.rx_box.setValue(0)
            self.ry_box.setValue(0)
            self.rz_box.setValue(0)
             
        # Add Appearance group
        self.appearance_group = QGroupBox("Appearance")
        self.appearance_layout = QFormLayout()
        
        # Size control
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(0.1, 1000.0)
        self.size_spin.setSingleStep(0.1)
        self.size_spin.setValue(1.0)
        self.appearance_layout.addRow("Size scaling:", self.size_spin)
        
        # Texture selection
        self.texture_field = QLineEdit()
        self.texture_field.setReadOnly(True)
        self.browse_button = QPushButton("Browse...")
        
        texture_layout = QHBoxLayout()
        texture_layout.addWidget(self.texture_field)
        texture_layout.addWidget(self.browse_button)
        self.appearance_layout.addRow("Texture:", texture_layout)
        
        # Texture preview
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(100, 100)
        self.preview_label.setScaledContents(True)
        self.appearance_layout.addRow("Preview:", self.preview_label)
        
        self.appearance_group.setLayout(self.appearance_layout)
        self.main_layout.addWidget(self.appearance_group)
        
        # Connect signals
        self.browse_button.clicked.connect(self.browse_texture)
        
        # Set existing values if editing
        if not is_new:
            self.size_spin.setValue(sat.get_size())
            if sat.has_texture():
                self.texture_field.setText(sat.get_texture_path())
                self.update_preview(sat.get_texture_path())
        self.rotation_group = QGroupBox("Day Length")
        self.rotation_layout = QFormLayout()

        # Axis selection
        self.rotation_axis_combo = QComboBox()
        self.rotation_axis_combo.addItems(["X-axis", "Y-axis", "Z-axis"])
        self.rotation_layout.addRow("Rotation Axis:", self.rotation_axis_combo)

        self.rotation_period_spin = QDoubleSpinBox()
        self.rotation_period_spin.setRange(0.0, 1000000.0)  # 0 to 1,000,000 seconds
        self.rotation_period_spin.setSuffix(" s")
        self.rotation_period_spin.setSpecialValueText("No rotation")  # Shows when value is 0
        self.rotation_period_spin.setSingleStep(1.0)
        self.rotation_period_spin.setValue(0.0)  # Default to no rotation
        self.rotation_layout.addRow("Rotation period (day length):", self.rotation_period_spin)

        self.rotation_group.setLayout(self.rotation_layout)
        self.main_layout.addWidget(self.rotation_group)

        # Set existing values if editing
        if not is_new:
            # Determine which axis has rotation and set the UI accordingly
            if sat.get_rx() != 0:
                self.rotation_axis_combo.setCurrentIndex(0)  # X-axis
                period = 0 if sat.get_rx() == 0 else (2 * math.pi) / abs(sat.get_rx())
                self.rotation_period_spin.setValue(period)
            elif sat.get_ry() != 0:
                self.rotation_axis_combo.setCurrentIndex(1)  # Y-axis
                period = 0 if sat.get_ry() == 0 else (2 * math.pi) / abs(sat.get_ry())
                self.rotation_period_spin.setValue(period)
            elif sat.get_rz() != 0:
                self.rotation_axis_combo.setCurrentIndex(2)  # Z-axis
                period = 0 if sat.get_rz() == 0 else (2 * math.pi) / abs(sat.get_rz())
                self.rotation_period_spin.setValue(period)
            else:
                self.rotation_axis_combo.setCurrentIndex(2)  # Default to Z-axis
                self.rotation_period_spin.setValue(0.0)
            # Set existing value if editingz
        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)
        # Confirm button
        self.confirm_button = QPushButton()
        self.confirm_button.setText("Add satellite" if is_new else "Apply")
        self.confirm_button.setDefault(True)
        outer_layout.addWidget(self.confirm_button)

        # Final layout setup
        self.setLayout(outer_layout)
  
        # If existing satellite, use its values in form, else default values
        if not is_new:
            self.sat_name_field.setText(self.m_sat.get_name())
            self.a_box.setValue(self.m_sat.get_orbit().get_a())
            self.a_box.setMinimum(self.m_planet.get_radius() / (1.0 - self.m_sat.get_orbit().get_e()))
            self.a_box.setToolTip(f"[{self.a_box.minimum()}, {self.a_box.maximum()}]")
            self.e_box.setValue(self.m_sat.get_orbit().get_e())
            self.e_box.setMaximum(1.0 - self.m_planet.get_radius() / self.m_sat.get_orbit().get_a())
            self.e_box.setToolTip(f"[{self.e_box.minimum()}, {self.e_box.maximum()}]")
            self.i_box.setValue(self.m_sat.get_orbit().get_i())
            self.om_box.setValue(self.m_sat.get_orbit().get_omega())
            self.om_small_box.setValue(self.m_sat.get_orbit().get_omega_small())
            self.tp_box.setValue(self.m_sat.get_orbit().get_tp())
            self.rx_box.setValue(self.m_sat.get_rx())
            self.ry_box.setValue(self.m_sat.get_ry())
            self.rz_box.setValue(self.m_sat.get_rz())
        else:
            self.sat_name_field.setText("Satellite")
            self.a_box.setValue(self.m_planet.a_geo())
            self.e_box.setValue(0.0)
            self.i_box.setValue(0.0)
            self.om_box.setValue(0.0)
            self.om_small_box.setValue(0.0)
            self.tp_box.setValue(0.0)
            self.rx_box.setValue(0.0)
            self.ry_box.setValue(0.0)
            self.rz_box.setValue(0.0)
        
        # Connect signals
        self.a_box.valueChanged.connect(self.on_a_changed)
        self.e_box.valueChanged.connect(self.on_e_changed)
        self.confirm_button.clicked.connect(self.confirm_slot)

    def browse_texture(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Satellite Texture", 
            "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.texture_field.setText(path)
            self.update_preview(path)
    
    def update_preview(self, path):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            self.preview_label.setPixmap(pixmap.scaled(
                100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
    def on_parent_type_changed(self, text):
        """Enable/disable satellite combo based on parent type selection"""
        is_satellite = (self.parent_type_combo.currentData() == "satellite")
        self.parent_sat_combo.setEnabled(is_satellite)
        
        # If no satellites available but satellite type selected, show warning
        if is_satellite and self.parent_sat_combo.count() == 0:
            QMessageBox.warning(self, "No Satellites", 
                              "No satellites available to select as parent.")
    @pyqtSlot(float)
    def on_a_changed(self, a):
        """
        Handle changes to the semi-major axis value
        
        Args:
            a (float): New semi-major axis value
        """
        # Update e maximum
        self.e_box.setMaximum(1.0 - self.m_planet.get_radius() / a)
        self.e_box.setToolTip(f"[{self.e_box.minimum()}, {self.e_box.maximum()}]")
        
        # Update tp range
        period = 1.0 / Constants.twopi * math.sqrt(pow(self.a_box.value(), 3.0) / self.m_planet.get_mu())
        self.tp_box.setRange(-period, period)
        self.tp_box.setToolTip(f"[{self.tp_box.minimum()}, {self.tp_box.maximum()}]")
    
    @pyqtSlot(float)
    def on_e_changed(self, e):
        """
        Handle changes to the eccentricity value
        
        Args:
            e (float): New eccentricity value
        """
        # Update a minimum
        self.a_box.setMinimum(self.m_planet.get_radius() / (1.0 - e))
        self.a_box.setToolTip(f"[{self.a_box.minimum()}, {self.a_box.maximum()}]")
    
    @pyqtSlot()
    def confirm_slot(self):
        """Handle confirm button click"""
        if not self.sat_name_field.text():
            QMessageBox.warning(self, "Empty name", "Please enter a satellite name!")
            return
        
        # Update satellite with form values
        self.m_sat.set_name(self.sat_name_field.text())
        self.m_sat.get_orbit().set_a(self.a_box.value())
        self.m_sat.get_orbit().set_e(self.e_box.value())
        self.m_sat.get_orbit().set_i(self.i_box.value())
        self.m_sat.get_orbit().set_omega(self.om_box.value())
        self.m_sat.get_orbit().set_omega_small(self.om_small_box.value())
        self.m_sat.get_orbit().set_tp(self.tp_box.value())
        selected_axis = self.rotation_axis_combo.currentIndex()
        period = self.rotation_period_spin.value()
        self.m_sat.set_rx(0.0)
        self.m_sat.set_ry(0.0)
        self.m_sat.set_rz(0.0)
        if period > 0:
            angular_velocity = (2 * math.pi) / period
            if selected_axis == 0:  # X-axis
                self.m_sat.set_rx(angular_velocity)
            elif selected_axis == 1:  # Y-axis
                self.m_sat.set_ry(angular_velocity)
            else:  # Z-axis
                self.m_sat.set_rz(angular_velocity)
        self.m_sat.set_size(self.size_spin.value())
        self.m_sat.set_texture_path(self.texture_field.text())
        if self.texture_field.text():
            self.m_sat.set_rotation_speed(self.rotation_period_spin.value())
        
        self.m_sat.get_orbit().reset()
        if self.m_is_new and hasattr(self, 'parent_type_combo'):
            if self.parent_type_combo.currentData() == "satellite":
                parent = self.parent_sat_combo.currentData()
                if parent:
                    self.m_sat.set_parent(parent)
                    # Force parent position initialization
                    parent.get_orbit().reset()
        self.done(QDialog.Accepted)

    @pyqtSlot()
    def import_from_norad_slot(self):
        """Import satellite data from NORAD ID"""
        norad_id = self.norad_id_field.text()
        if not norad_id:
            QMessageBox.warning(self, "Invalid NORAD ID", "Please enter a valid NORAD ID.")
            return
            
        try:
            importer = TLEImporter()
            satellite = importer.fetch_satellite_by_norad_id(norad_id)
            
            if not satellite:
                QMessageBox.warning(self, "Satellite Not Found", 
                                f"Could not find satellite with NORAD ID {norad_id}.")
                return
                
            # Convert to orbit parameters and update the UI
            orbit = importer.convert_to_simulator_orbit(satellite, self.m_planet)
            
            # Update the satellite's orbit with the imported parameters
            self.m_sat.get_orbit().set_a(orbit.get_a())
            self.m_sat.get_orbit().set_e(orbit.get_e())
            self.m_sat.get_orbit().set_i(orbit.get_i())
            self.m_sat.get_orbit().set_omega(orbit.get_omega())
            self.m_sat.get_orbit().set_omega_small(orbit.get_omega_small())
            
            # Update form fields with the imported data
            self.a_box.setValue(orbit.get_a())
            self.e_box.setValue(orbit.get_e())
            self.i_box.setValue(orbit.get_i())
            self.om_box.setValue(orbit.get_omega())
            self.om_small_box.setValue(orbit.get_omega_small())
            
            # Set satellite name from TLE if available
            self.sat_name_field.setText(satellite.name)
            self.m_sat.set_name(satellite.name)
            
            QMessageBox.information(self, "Import Successful", 
                                f"Successfully imported data for satellite {satellite.name}.")
                                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", 
                            f"An error occurred while importing the satellite data: {str(e)}")
            
    def update_orbit_preview(self):
        """Update the orbit preview with current values"""
        a = self.a_box.value()
        e = self.e_box.value()
        self.orbit_preview.update_orbit(a, e)

    def on_preview_changed(self, a, e):
        """Handle changes from the preview widget"""
        # Block signals temporarily to prevent infinite loops
        self.a_box.blockSignals(True)
        self.e_box.blockSignals(True)
        
        self.a_box.setValue(a)
        self.e_box.setValue(e)
        
        # Restore signals
        self.a_box.blockSignals(False)
        self.e_box.blockSignals(False)
        
        # Update other dependent fields
        self.on_a_changed(a)
        self.on_e_changed(e)

    def update_attitude(self):
        """Update the satellite's attitude based on UI controls"""
        # Convert degrees to radians for internal storage
        self.m_sat.set_rx(math.radians(self.rx_box.value()))
        self.m_sat.set_ry(math.radians(self.ry_box.value()))
        self.m_sat.set_rz(math.radians(self.rz_box.value()))