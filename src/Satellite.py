from src.Orbit import Orbit
from src.Planet import Planet
from src.Propulsion import Propulsion
from src.PointPol import PointPol
from src.Constants import Constants
import os
class Satellite:
    """
    Represents a satellite object in the simulation
    """
    
    def __init__(self, orb, planet, prop, name="",parent=None):
        """
        Initialize a satellite
        
        Args:
            orb (Orbit): The orbit of the satellite
            planet (Planet): The planet the satellite orbits
            prop (Propulsion): The propulsion system
            name (str, optional): The name of the satellite. Defaults to "".
        """
        self.m_orbit = Orbit(planet, orb.get_a(), orb.get_e(), orb.get_i(), 
                            orb.get_omega(), orb.get_omega_small(), orb.get_tp())
        self.m_planet = planet
        self.m_prop = prop
        self.m_name = name
        self.m_orbit.reset()
        self.m_parent = parent
        if parent is not None and parent.get_current_position() is None:
            parent.get_orbit().reset()
        if parent is not None:
            # Configure as relative orbit
            self.m_orbit.set_relative_to_parent(parent.get_orbit())
            # Initialize relative position
            self.update(0)
        self.m_rx = 0.0
        self.m_ry = 0.0
        self.m_rz = 0.0
        self.m_texture_path = ""
        self.m_size = 1.0
        self.m_rotation = 0.0  # Current rotation angle in radians
        self.m_rotation_speed = 0.5  # Rotation speed in radians/second
    
    def update(self, dt):
        """
        Update the satellite state for a time step
        
        Args:
            dt (float): Time step in seconds
        """
        if self.m_parent is not None:
            # Update relative to parent's current position
            parent_pos = self.m_parent.get_current_position()
            if parent_pos:
                self.m_orbit.update(dt)
                # Maintain relative position
                rel_pos = self.m_orbit.get_position_point()
                self.current_position = parent_pos + rel_pos
            else:
                self.m_orbit.update(dt)
        else:
            # Standard absolute orbit
            self.m_orbit.update(dt)
        
        # Only rotate if we have a texture (spherical)
        if self.has_texture():
            if self.m_rx != 0:
                self.m_rotation += self.m_rx * dt
            elif self.m_ry != 0:
                self.m_rotation += self.m_ry * dt
            else:  # Default to Z-axis rotation
                self.m_rotation += self.m_rz * dt
            self.m_rotation %= (2 * Constants.pi)  # Keep within 0-2π
    
    def reset(self):
        """Reset the satellite to its initial state"""
        # Reset position to 0
        self.m_orbit.reset()
        # Reset other parameters if needed
        # self.m_prop.reset()
    
    def to_string(self):
        """
        Convert satellite to string representation
        
        Returns:
            str: String representation of the satellite
        """
        output = "----------\n"
        output += f"Name: {self.m_name}\n"
        # output += f"Propulsion: {self.m_prop.to_string()}\n"
        output += self.m_orbit.to_string()
        return output
    
    def get_orbit(self):
        """
        Get the satellite's orbit
        
        Returns:
            Orbit: The satellite's orbit
        """
        return self.m_orbit
    
    def get_planet(self):
        """
        Get the planet the satellite orbits
        
        Returns:
            Planet: The planet
        """
        return self.m_planet
    
    def get_propu(self):
        """
        Get the satellite's propulsion system
        
        Returns:
            Propulsion: The propulsion system
        """
        return self.m_prop
    
    def get_name(self):

        return self.m_name
    
    def get_rx(self):
        return self.m_rx
    
    def get_ry(self):
        return self.m_ry
    
    def get_rz(self):
        return self.m_rz
    
    def set_name(self, name):
        self.m_name = name
    
    def set_rx(self, rx):
        self.m_rx = rx
    
    def set_ry(self, ry):
        self.m_ry = ry
    
    def set_rz(self, rz):
        self.m_rz = rz
    
    def get_current_position(self):
        
        """Get position relative to parent (planet or satellite)"""
        try:
            # Get position relative to parent
            pos = self.m_orbit.get_position_point()
            if pos is None:
                print(f"Null orbit position for {self.m_name}")
                return PointPol(0, 0, 0)
                
            # If we have a parent satellite, add its position
            if self.m_parent is not None:
                parent_pos = self.m_parent.get_current_position()
                if parent_pos is None:
                    print(f"Null parent position for {self.m_name}")
                    return pos
                return pos + parent_pos
            return pos
        except Exception as e:
            print(f"Error in get_current_position for {self.m_name}: {str(e)}")
            return PointPol(0, 0, 0)
        
    def set_texture_path(self, path):
        self.m_texture_path = os.path.abspath(path) if path else ""
        
    def get_texture_path(self):
        return self.m_texture_path
        
    def set_size(self, size):
        self.m_size = max(0.1, min(1000.0, float(size)))
        
    def get_size(self):
        return self.m_size
        
    def has_texture(self):
        return bool(self.m_texture_path)
    def get_rotation(self):
        return self.m_rotation
        
    def set_rotation_speed(self, speed):
        self.m_rotation_speed = speed
        
    def get_rotation_speed(self):
        return self.m_rotation_speed

    def get_parent(self):      
        return self.m_parent
    
    def set_parent(self, parent_sat):
        self.m_parent = parent_sat