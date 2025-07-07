import math
from src.Point import Point
from src.Constants import Constants

class PointCart(Point):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        super(PointCart, self).__init__()
        
        # If the first argument is a Point object, initialize from it
        if isinstance(x, Point):
            self.m_x = x.get_x()
            self.m_y = x.get_y()
            self.m_z = x.get_z()
        else:
            self.m_x = x
            self.m_y = y
            self.m_z = z
    
    def __eq__(self, p):
        return (self.m_x == p.get_x() and 
                self.m_y == p.get_y() and 
                self.m_z == p.get_z())
    
    def __iadd__(self, p):
        self.m_x += p.get_x()
        self.m_y += p.get_y()
        self.m_z += p.get_z()
        return self
    
    def __isub__(self, p):
        self.m_x -= p.get_x()
        self.m_y -= p.get_y()
        self.m_z -= p.get_z()
        return self
    
    def __add__(self, p):
        copy = PointCart(self.m_x, self.m_y, self.m_z)
        copy += p
        return copy
    
    def __sub__(self, p):
        copy = PointCart(self.m_x, self.m_y, self.m_z)
        copy -= p
        return copy
    
    # Getter and setter methods
    def get_x(self):
        """Get x coordinate"""
        return self.m_x
    
    def set_x(self, val):
        """Set x coordinate"""
        self.m_x = val
    
    def get_y(self):
        """Get y coordinate"""
        return self.m_y
    
    def set_y(self, val):
        """Set y coordinate"""
        self.m_y = val
    
    def get_z(self):
        """Get z coordinate"""
        return self.m_z
    
    def set_z(self, val):
        """Set z coordinate"""
        self.m_z = val
    
    # Polar coordinate conversions
    def get_r(self):
        """Get radius (polar coordinate)"""
        return math.sqrt(self.m_x * self.m_x + self.m_y * self.m_y + self.m_z * self.m_z)
    
    def get_theta(self):
        """Get azimuthal angle (polar coordinate)"""
        if self.m_x > 0.0 and self.m_y >= 0.0:
            return math.atan(self.m_y / self.m_x)
        if self.m_x == 0.0 and self.m_y > 0.0:
            return Constants.pi / 2.0
        if self.m_x < 0.0:
            return Constants.pi + math.atan(self.m_y / self.m_x)
        if self.m_x == 0.0 and self.m_y < 0.0:
            return 3.0 * Constants.pi / 2.0
        if self.m_x > 0.0 and self.m_y < 0.0:
            return Constants.twopi + math.atan(self.m_y / self.m_x)
        return 0.0
    def get_phi(self):
        return super().get_phi()
    def print(self):
        """Print the point coordinates"""
        print(f"Cartesian Point: x={self.m_x}, y={self.m_y}, z={self.m_z}")
        print(f"Polar: r={self.get_r()}, theta={self.get_theta()}, phi={self.get_phi()}")