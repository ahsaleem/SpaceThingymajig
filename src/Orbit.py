import math
from src.Constants import Constants
from src.PointPol import PointPol
from src.Planet import Planet

class Orbit:
    def __init__(self, planet, a, e, i, omega=0.0, omega_small=0.0, tp=0.0):
        """
        Initialize an orbit with Keplerian elements
        
        Args:
            planet (Planet): The central planet
            a (float): Semi-major axis (km)
            e (float): Eccentricity
            i (float): Inclination (rad)
            omega (float, optional): Longitude of ascending node (rad). Defaults to 0.0.
            omega_small (float, optional): Argument of periapsis (rad). Defaults to 0.0.
            tp (float, optional): Epoch (s). Defaults to 0.0.
        """
        self.m_planet = planet
        self.m_mu = planet.get_mu()
        min_a = planet.get_radius() * 1.1 if hasattr(planet, 'get_radius') else Constants.r_earth * 1.1
        self.m_a = max(min_a, float(a))
        self.m_e = max(0.0, min(0.99, float(e)))
        
        # Normalize i to [0, 2π)
        self.m_i = math.fmod(i, Constants.twopi)
        if self.m_i < 0.0:
            self.m_i += Constants.twopi
        
        # Normalize Omega to [0, 2π)
        self.m_Omega = math.fmod(omega, Constants.twopi)
        if self.m_Omega < 0.0:
            self.m_Omega += Constants.twopi
        
        # Normalize omega to [0, 2π)
        self.m_omega = math.fmod(omega_small, Constants.twopi)
        if self.m_omega < 0.0:
            self.m_omega += Constants.twopi
        
        self.m_tp = tp
        
        # Initialize satellite motion variables
        self.m_v = 0.0  # True anomaly
        self.m_E = 0.0  # Eccentric anomaly
        self.m_M = 0.0  # Mean anomaly
        

        # Reset position to initial state
        self.is_relative = False
        self.relative_orientation = PointPol(0, 0, 0) 
        self.reset()
    
    def __init_from_orbit(self, orbit):
        self.m_planet = orbit.get_planet()
        self.m_mu = self.m_planet.get_mu()
        self.m_a = orbit.get_a()
        self.m_e = orbit.get_e()
        self.m_i = orbit.get_i()
        self.m_Omega = orbit.get_omega()
        self.m_omega = orbit.get_omega_small()
        self.m_tp = orbit.get_tp()
        self.m_v = orbit.get_v()
        self.m_E = orbit.get_e()
        self.m_M = orbit.get_m()
    
    def update_position(self, dt):
        # Update mean anomaly
        if not self.is_relative:
            new_M = math.fmod(self.m_M + self.get_n() * dt, Constants.twopi)
            if new_M < 0.0:
                new_M += Constants.twopi
            # Compute eccentric anomaly E with dichotomy since E - e*sin(E) is crescent
            eps = 1.0e-6
            min_val = 0.0
            max_val = Constants.twopi
            self.set_m(new_M)
            while (max_val - min_val) > eps:
                mid = 0.5 * (max_val + min_val)
                if self.m_M < mid - self.m_e * math.sin(mid):
                    max_val = mid
                else:
                    min_val = mid
            
            self.m_E = min_val
        
        # Compute true anomaly v
            if self.m_E <= Constants.pi:
                self.m_v = math.acos((math.cos(self.m_E) - self.m_e) / (1.0 - self.m_e * math.cos(self.m_E)))
            else:
                self.m_v = Constants.twopi - math.acos((math.cos(self.m_E) - self.m_e) / (1.0 - self.m_e * math.cos(self.m_E)))
        else:
            # For relative orbits, update position relative to parent
            self._update_relative_position(dt)
    def _update_relative_position(self, dt):
        """Maintain position relative to parent"""
        # Preserve the relative orientation
        self.m_v = self.relative_orientation.get_theta()
        self.m_phi = self.relative_orientation.get_phi()
        
        # Update anomalies while maintaining relative position
        self.m_M = math.fmod(self.m_M + self.get_n() * dt, Constants.twopi)
        self.m_E = self._solve_kepler_equation(self.m_M)
        
        # Calculate new position while preserving relative angles
        r = self.m_a * (1.0 - self.m_e * math.cos(self.m_E))
        self.relative_orientation.set_r(r)

    def set_relative_to_parent(self, parent_orbit):
        """Configure this as a relative orbit"""
        self.is_relative = True
        # Store initial relative orientation
        current_pos = self.get_position_point()
        parent_pos = parent_orbit.get_position_point()
        self.relative_orientation = current_pos - parent_pos
    def set_m(self, m):
        """
        Set the mean anomaly and update related angles
        
        Args:
            m (float): Mean anomaly (rad)
        """
        # Set M
        self.m_M = m
        self.m_M = math.fmod(self.m_M, Constants.twopi)
        if self.m_M < 0.0:
            self.m_M += Constants.twopi
        
        # Compute E with dichotomy since E - e*sin(E) is crescent
        eps = 1.0e-6
        min_val = 0.0
        max_val = Constants.twopi
        
        while (max_val - min_val) > eps:
            mid = 0.5 * (max_val + min_val)
            if self.m_M < mid - self.m_e * math.sin(mid):
                max_val = mid
            else:
                min_val = mid
        
        self.m_E = min_val
        
        # Compute v
        if self.m_E <= Constants.pi:
            self.m_v = math.acos((math.cos(self.m_E) - self.m_e) / (1.0 - self.m_e * math.cos(self.m_E)))
        else:
            self.m_v = Constants.twopi - math.acos((math.cos(self.m_E) - self.m_e) / (1.0 - self.m_e * math.cos(self.m_E)))
    
    def reset(self):
        """Reset orbital position to initial state"""
        # Set M to initial angle
        self.set_m(-self.get_n() * self.m_tp)
    
    def get_position_point(self):
        try:
            r = self.m_a * (1.0 - self.m_e * math.cos(self.m_E))
            if math.isnan(r) or not math.isfinite(r):
                r = self.m_a
        
            theta = math.fmod(
                self.m_Omega + math.atan2(
                    math.sin(self.m_omega + self.m_v) * math.cos(self.m_i) / 
                    math.sqrt(1.0 - math.pow(math.sin(self.m_omega + self.m_v) * math.sin(self.m_i), 2.0)),
                    math.cos(self.m_omega + self.m_v) / 
                    math.sqrt(1.0 - math.pow(math.sin(self.m_omega + self.m_v) * math.sin(self.m_i), 2.0))
                ),
                Constants.twopi
            )
            
            if theta < 0.0:
                theta += Constants.twopi
            
            phi = math.fmod(math.asin(math.sin(self.m_i) * math.sin(self.m_omega + self.m_v)), Constants.twopi)
            
            if phi < 0.0:
                phi += Constants.twopi
        
            return PointPol(r, theta, phi)
        except Exception as e:
            print("Error in orbit position calculation", str(e))
            return PointPol(self.m_a, 0, 0)
    
    def get_point_at(self, m):
        # Normalize M to [0, 2π)
        m = math.fmod(m, Constants.twopi)
        if m < 0.0:
            m += Constants.twopi
        
        # Compute E with dichotomy since E - e*sin(E) is crescent
        eps = 1.0e-6
        min_val = 0.0
        max_val = Constants.twopi
        
        while (max_val - min_val) > eps:
            mid = 0.5 * (max_val + min_val)
            if m < mid - self.m_e * math.sin(mid):
                max_val = mid
            else:
                min_val = mid
        
        e = min_val
        
        # Compute v
        v = 0.0
        if e <= Constants.pi:
            v = math.acos((math.cos(e) - self.m_e) / (1.0 - self.m_e * math.cos(e)))
        else:
            v = Constants.twopi - math.acos((math.cos(e) - self.m_e) / (1.0 - self.m_e * math.cos(e)))
        
        # Compute point
        r = self.m_a * (1.0 - self.m_e * math.cos(e))
        
        theta = math.fmod(
            self.m_Omega + math.atan2(
                math.sin(self.m_omega + v) * math.cos(self.m_i) / 
                math.sqrt(1.0 - math.pow(math.sin(self.m_omega + v) * math.sin(self.m_i), 2.0)),
                math.cos(self.m_omega + v) / 
                math.sqrt(1.0 - math.pow(math.sin(self.m_omega + v) * math.sin(self.m_i), 2.0))
            ),
            Constants.twopi
        )
        
        if theta < 0.0:
            theta += Constants.twopi
        
        phi = math.fmod(math.asin(math.sin(self.m_i) * math.sin(self.m_omega + v)), Constants.twopi)
        
        if phi < 0.0:
            phi += Constants.twopi
        
        return PointPol(r, theta, phi)
    def update(self, dt):
        if not self.is_relative:
            # Standard absolute orbit update
            self.m_M = math.fmod(self.m_M + self.get_n() * dt, Constants.twopi)
            if self.m_M < 0.0:
                self.m_M += Constants.twopi
        else:
            # Relative orbit maintains orientation to parent
            pass
            
        # Always update position
        self.update_position(dt)


    
    def to_string(self):
        output = f"a: {self.m_a}\n"
        output += f"e: {self.m_e}\n"
        output += f"i: {self.m_i}\n"
        output += f"Omega: {self.m_Omega}\n"
        output += f"omega: {self.m_omega}\n"
        output += f"tp: {self.m_tp}\n"
        output += f"M: {self.m_M}\n"
        
        return output
    
    def print(self):
        """Print detailed orbit information"""
        print("***Orbit members***")
        print(f"a  = {self.m_a} km")
        print(f"e  = {self.m_e}")
        print(f"i  = {self.m_i} rad")
        print(f"Om = {self.m_Omega} rad")
        print(f"om = {self.m_omega} rad")
        print(f"tp = {self.m_tp} s")
        print(f"n  = {self.get_n()} rad/s")
        
        print("***Other info***")
        print(f"rp = {self.m_a * (1.0 - self.m_e)} km")
        print(f"ra = {self.m_a * (1.0 + self.m_e)} km")
        print(f"T  = {Constants.twopi / self.get_n()} s")
        
        print("***Satellite motion***")
        print(f"v  = {self.m_v} rad")
        print(f"E  = {self.m_E} rad")
        print(f"M  = {self.m_M} rad")
    
    # Getter and setter methods
    def get_a(self):
        return self.m_a
    
    def set_a(self, a):
        self.m_a = a
    
    def get_e(self):
        return self.m_e
    
    def set_e(self, e):
        self.m_e = e
    
    def get_i(self):
        return self.m_i
    
    def set_i(self, i):
        self.m_i = i
    
    def get_omega(self):
        return self.m_Omega
    
    def set_omega(self, omega):
        self.m_Omega = omega
    
    def get_omega_small(self):
        return self.m_omega
    
    def set_omega_small(self, omega):
        self.m_omega = omega
    
    def get_n(self):
        return math.sqrt(self.m_mu / math.pow(self.m_a, 3.0))
    
    def get_v(self):
        return self.m_v
    
    def get_m(self):
        return self.m_M
    
    def get_tp(self):
        return self.m_tp
    
    def set_tp(self, tp):
        self.m_tp = tp
    
    def get_planet(self):
        return self.m_planet
    
    def get_ra(self):
        return self.m_a * (1.0 + self.m_e)
    
    def get_rp(self):
        return self.m_a * (1.0 - self.m_e)