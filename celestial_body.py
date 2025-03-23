import numpy as np

class CelestialBody:
    """A class representing a celestial body (planet, star, etc.)."""
    
    def __init__(self, mass, position, velocity, radius, color):
        """
        Initialize a celestial body.
        
        Args:
            mass (float): Mass of the body in kg
            position (np.array): 2D position vector [x, y]
            velocity (np.array): 2D velocity vector [vx, vy]
            radius (float): Radius of the body for visualization
            color (tuple): RGB color tuple for visualization
        """
        self.mass = mass
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.zeros(2)
        self.radius = radius
        self.color = color
        self.trail = []  # Store previous positions for trail
        self.max_trail_length = 500  # Maximum number of positions to store
        self.initial_position = position.copy()  # Store initial position
        self.initial_velocity = velocity.copy()  # Store initial velocity
        
    def calculate_force(self, center_body, scale, use_constant_acceleration):
        """Calculate force between this body and the center body."""
        # Vector from this body to the center
        r = center_body.position - self.position
        
        # Distance between bodies in pixels
        distance = np.linalg.norm(r)
        
        # Avoid division by zero and too small distances
        distance = max(distance, 1e-10)
        
        # Normalize direction vector
        direction = r / distance
        
        # Use the same G value as in WorldSimulator
        G = 1.0
        
        # Calculate force using Newton's Law: F = GMm/r²
        force_magnitude = G * center_body.mass * self.mass / (distance ** 2)
        
        # Calculate force vector
        force = force_magnitude * direction
        
        return force
    
    def update_acceleration(self, bodies, scale, use_constant_acceleration=False):
        """Update acceleration based on force from the central body."""
        # Only consider force from the central body (first body in the list)
        center_body = bodies[0]
        if self is not center_body:  # Don't calculate for the central body
            force = self.calculate_force(center_body, scale, use_constant_acceleration)
            self.acceleration = force / self.mass  # a = F/m
        else:
            self.acceleration = np.zeros(2)  # Central body doesn't move
    
    def update_position(self, dt):
        """Update position and velocity using semi-implicit Euler method for better stability."""
        # Update velocity first (semi-implicit Euler)
        self.velocity += self.acceleration * dt
        
        # Then update position
        self.position += self.velocity * dt
        
        # Add current position to trail
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            
    def reset(self):
        """Reset the body to its initial state."""
        self.position = self.initial_position.copy()
        self.velocity = self.initial_velocity.copy()
        self.acceleration = np.zeros(2)
        self.trail = [] 