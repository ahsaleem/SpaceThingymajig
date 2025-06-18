import math
from src.Constants import Constants

class Planet:
    def __init__(self, mu=Constants.mu_earth, radius=Constants.r_earth, 
                 day=Constants.day_earth, name=Constants.defaultPlanetName,
                 img_path=Constants.defaultImgPath, night_img_path=None):
        """
        Initialize a planet with physical parameters
        
        Args:
            mu (float, optional): Gravitational parameter (km^3/s^2). Defaults to Earth's mu.
            radius (float, optional): Planet radius (km). Defaults to Earth's radius.
            day (float, optional): Sidereal day duration (s). Defaults to Earth's day.
            name (str, optional): Planet name. Defaults to "Earth".
            img_path (str, optional): Path to day texture image. Defaults to Earth texture.
            night_img_path (str, optional): Path to night texture image. Defaults to None.
        """
        self.m_mu = mu
        self.m_radius = radius
        self.m_name = name
        self.m_img_path = img_path
        self.m_night_img_path = night_img_path
        self.m_day = day
    
    def get_mu(self):
        return self.m_mu
    
    def get_radius(self):
        return self.m_radius
    
    def get_day(self):
        return self.m_day
    
    def get_name(self):
        return self.m_name
    
    def get_img_path(self):
        return self.m_img_path
    
    def get_night_img_path(self):
        return self.m_night_img_path
    
    def set_mu(self, mu):
        self.m_mu = mu
    
    def set_radius(self, radius):
        self.m_radius = radius
    
    def set_day(self, day):
        self.m_day = day
    
    def set_name(self, name):
        self.m_name = name
    
    def set_img_path(self, path):
        self.m_img_path = path
    
    def set_night_img_path(self, path):
        self.m_night_img_path = path
    
    def a_geo(self):
        return math.pow(self.m_mu * self.m_day * self.m_day / (4.0 * Constants.pi2), 1.0/3.0)
    
    def to_string(self):
        output = f"Name: {self.m_name}\n"
        output += f"Radius: {self.m_radius}\n"
        output += f"Mu: {self.m_mu}\n"
        output += f"Day: {self.m_day}\n"
        output += f"ImgPath: {self.m_img_path}\n"
        output += f"NightImgPath: {self.m_night_img_path}\n"
        return output