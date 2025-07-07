import math
from src.Point import Point
from src.PointCart import PointCart

class PointPol(Point):
    """
    Represents a point in polar coordinates (r, theta, phi)
    """
    
    def __init__(self, r=0.0, theta=0.0, phi=0.0):
        super(PointPol, self).__init__()
        self.m_r = float(r) if r is not None else 0.0
        self.m_theta = float(theta) if theta is not None else 0.0
        self.m_phi = float(phi) if phi is not None else 0.0
    
    def __init_from_point(self, p):
        self.m_r = p.get_r()
        self.m_theta = p.get_theta()
        self.m_phi = p.get_phi()
        self.m_r = float(self.m_r) if self.m_r is not None else 0.0
        self.m_theta = float(self.m_theta) if self.m_theta is not None else 0.0
        self.m_phi = float(self.m_phi) if self.m_phi is not None else 0.0
    
    def valid_params(self):
        self.m_r = float(self.m_r) if self.m_r is not None else 0.0
        self.m_theta = float(self.m_theta) if self.m_theta is not None else 0.0
        self.m_phi = float(self.m_phi) if self.m_phi is not None else 0.0
    
    # Python's special methods for operator overloading
    def __eq__(self, p):
        return (self.m_r == p.get_r() and 
                self.m_theta == p.get_theta() and 
                self.m_phi == p.get_phi())
    
    def __iadd__(self, p):
        # Create cartesian copy of point to use adding operator
        tmp = PointCart(self)
        tmp += p
        # Reconvert to polar point
        copy = PointPol(0)
        copy.__init_from_point(tmp)
        self.m_r = copy.m_r
        self.m_theta = copy.m_theta
        self.m_phi = copy.m_phi
        self.valid_params()
        return self
    
    def __isub__(self, p):
        # Create cartesian copy of point to use subtraction operator
        tmp = PointCart(self)
        tmp -= p
        # Reconvert to polar point
        copy = PointPol(0)
        copy.__init_from_point(tmp)
        self.m_r = copy.m_r
        self.m_theta = copy.m_theta
        self.m_phi = copy.m_phi
        self.valid_params()
        return self
    
    def __add__(self, p):
        copy = PointPol(0)
        copy.__init_from_point(self)
        copy += p
        self.valid_params()
        return copy
    
    def __sub__(self, p):
        if p is None:
            return PointPol(self.m_r, self.m_theta, self.m_phi)
            
        # Convert to Cartesian
        self_cart = PointCart(self)
        p_cart = PointCart(p)
        
        # Calculate difference
        diff = PointCart(
            self_cart.get_x() - p_cart.get_x(),
            self_cart.get_y() - p_cart.get_y(),
            self_cart.get_z() - p_cart.get_z()
        )
        return PointPol(diff)
    # Getter and setter methods
    def get_r(self):
        """Get radius"""
        return self.m_r
    
    def set_r(self, val):
        """Set radius"""
        self.m_r = val
    
    def get_theta(self):
        """Get azimuthal angle"""
        return self.m_theta
    
    def set_theta(self, val):
        """Set azimuthal angle"""
        self.m_theta = val
    
    def get_phi(self):
        """Get polar angle"""
        return self.m_phi
    
    def set_phi(self, val):
        """Set polar angle"""
        self.m_phi = val
    
    # Cartesian coordinate conversions
    def get_x(self):
        """Get x cartesian coordinate"""
        return self.m_r * math.cos(self.m_theta) * math.cos(self.m_phi)
    
    def get_y(self):
        """Get y cartesian coordinate"""
        return self.m_r * math.sin(self.m_theta) * math.cos(self.m_phi)
    
    def get_z(self):
        """Get z cartesian coordinate"""
        return self.m_r * math.sin(self.m_phi)
    
    def print(self):
        """Print the point coordinates"""
        print(f"Polar Point: r={self.m_r}, theta={self.m_theta}, phi={self.m_phi}")
        print(f"Cartesian: x={self.get_x()}, y={self.get_y()}, z={self.get_z()}")