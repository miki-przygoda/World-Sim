import pygame
import numpy as np
from celestial_body import CelestialBody

class WorldSimulator:
    def __init__(self, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Gravitational Orbital Simulator")
        
        # Initialize fonts
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.large_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Constants
        self.G = 1.0  # Scaled gravitational constant
        self.central_mass = 1000.0  # Mass of central body
        self.dt = 1  # Fixed time step for physics
        
        self.clock = pygame.time.Clock()
        self.bodies = []
        self.paused = True  # Start paused
        self.use_constant_acceleration = False  # Using gravitational acceleration only now
        self.scale = 1e9  # 1 pixel = 1 billion meters
        self.simulation_time = 0  # Track total simulation time
        
        # Store initial parameters for reset
        self.initial_sun_pos = np.array([self.width/2, self.height/2])
        self.orbital_distance = 150  # pixels - reduced for better visibility
        
        # Calculate initial orbital period (constant throughout simulation)
        self.initial_period = 2 * np.pi * np.sqrt(self.orbital_distance**3 / (self.G * self.central_mass))
        
        # Initialize the solar system
        self.create_solar_system()
    
    def create_solar_system(self):
        # Central body (yellow)
        center = CelestialBody(
            mass=self.central_mass,
            position=self.initial_sun_pos.copy(),
            velocity=np.array([0, 0]),  # Central body stays stationary
            radius=30,
            color=(255, 255, 0)
        )
        
        # Create orbiting bodies
        bodies = []
        num_outer_bodies = 1
        for i in range(num_outer_bodies):
            # Calculate position on a circle
            angle = i * (2 * np.pi / num_outer_bodies)
            x = self.width/2 + self.orbital_distance * np.cos(angle)
            y = self.height/2 + self.orbital_distance * np.sin(angle)
            
            # Calculate velocity for circular orbit using v = sqrt(GM/r)
            vel_magnitude = np.sqrt(self.G * self.central_mass / self.orbital_distance)
            vel_x = -vel_magnitude * np.sin(angle)  # Perpendicular to position
            vel_y = vel_magnitude * np.cos(angle)   # Perpendicular to position
            
            # Create the body with unique color
            body = CelestialBody(
                mass=10,
                position=np.array([x, y]),
                velocity=np.array([vel_x, vel_y]),
                radius=10,
                color=(0, 128 + i * 30, 255)  # Different shades of blue
            )
            bodies.append(body)
        
        self.bodies = [center] + bodies
    
    def reset_simulation(self):
        """Reset the simulation to its initial state."""
        self.simulation_time = 0
        self.paused = True  # Reset to paused state
        self.create_solar_system()  # Recreate all bodies instead of resetting existing ones
    
    def update(self, dt):
        """Update the positions and velocities of all bodies."""
        if not self.paused:
            # Use fixed time step for physics calculations
            # First, update all accelerations
            for body in self.bodies:
                body.update_acceleration(self.bodies, self.scale, self.use_constant_acceleration)
            
            # Then, update all positions
            for body in self.bodies:
                body.update_position(self.dt)
            
            self.simulation_time += self.dt
    
    def draw(self):
        """Draw all bodies to the screen."""
        self.screen.fill((0, 0, 0))  # Black background
        
        # Draw trails
        for body in self.bodies:
            if len(body.trail) > 1:
                # Draw trail with fading opacity
                for i in range(len(body.trail) - 1):
                    alpha = int(255 * (i / len(body.trail)))
                    color = (*body.color[:3], alpha)
                    start_pos = body.trail[i].astype(int)
                    end_pos = body.trail[i + 1].astype(int)
                    pygame.draw.line(self.screen, color, start_pos, end_pos, 1)
        
        # Draw bodies and calculate orbital periods
        orbital_periods = []  # Store periods for later display
        for i, body in enumerate(self.bodies):
            # Draw the body
            pygame.draw.circle(
                self.screen,
                body.color,
                body.position.astype(int),
                body.radius
            )
            
            # Calculate orbital period for orbiting bodies (skip the central body)
            if i > 0:  # Skip the central body (index 0)
                # Use the initial orbital period instead of recalculating
                orbital_periods.append((body.color, self.initial_period))
        
        # Draw simulation information
        days = self.simulation_time
        info_text = f"Simulation Time: {days:.1f} days"
        if self.paused:
            info_text += " (PAUSED)"
        if self.use_constant_acceleration:
            info_text += " [Constant Acceleration]"
        else:
            info_text += " [Gravitational Acceleration]"
        
        text_surface = self.font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))
        
        # Draw FPS
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.font.render(fps_text, True, (255, 255, 255))
        self.screen.blit(fps_surface, (10, 30))
        
        # Draw orbital periods
        y_offset = 50  # Start below FPS
        for i, (color, period) in enumerate(orbital_periods):
            period_text = f"Orbital Period (Body {i+1}): {period:.1f} days"
            period_surface = self.font.render(period_text, True, color)
            self.screen.blit(period_surface, (10, y_offset))
            y_offset += 20  # Increment y position for next period text
        
        # Draw controls help
        controls_text = "Controls: Space = Pause/Unpause, C = Toggle Acceleration Type, R = Reset, Esc = Exit"
        controls_surface = self.font.render(controls_text, True, (255, 255, 255))
        self.screen.blit(controls_surface, (10, self.height - 30))
        
        # Draw start message when paused and time is 0
        if self.paused and self.simulation_time == 0:
            start_text = "Press SPACE to start the simulation"
            start_surface = self.large_font.render(start_text, True, (255, 255, 255))
            text_rect = start_surface.get_rect(center=(self.width/2, self.height/2 + 100))
            self.screen.blit(start_surface, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main simulation loop."""
        running = True
        dt = 100  # Smaller time step for smoother motion
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_c:
                        self.use_constant_acceleration = not self.use_constant_acceleration
                    elif event.key == pygame.K_r:
                        self.reset_simulation()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            self.update(dt)
            self.draw()
            self.clock.tick(120)
        
        pygame.quit()

if __name__ == "__main__":
    simulator = WorldSimulator()
    simulator.run() 