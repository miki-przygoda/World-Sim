import pygame
from pygame.locals import *
from OpenGL.GL import * # type: ignore
from OpenGL.GLU import * # type: ignore
import numpy as np
from celestial_body import CelestialBody

class WorldSimulator:
    def __init__(self, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        
        # Set up OpenGL display
        pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Gravitational Orbital Simulator")
        
        # Create a separate surface for UI rendering
        self.ui_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Initialize fonts
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.large_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Constants
        self.G = 1.0  # Scaled gravitational constant
        self.central_mass = 1000.0  # Mass of central body
        self.dt = 1  # Fixed time step for physics
        
        # Camera control parameters
        self.camera_distance = 500
        self.camera_rotation = [0, 0, 0]  # [x, y, z] rotation angles
        self.camera_position = [0, 0, self.camera_distance]
        self.rotation_speed = 0.5  # Reduced for smoother mouse control
        self.zoom_speed = 10.0
        self.min_zoom = 100
        self.max_zoom = 1000
        
        # Mouse control parameters
        self.mouse_control = False
        self.last_mouse_pos = None
        
        self.clock = pygame.time.Clock()
        self.bodies = []
        self.paused = True  # Start paused
        self.use_constant_acceleration = False  # Using gravitational acceleration only now
        self.scale = 1e9  # 1 pixel = 1 billion meters
        self.simulation_time = 0  # Track total simulation time
        
        # Store initial parameters for reset
        self.initial_sun_pos = np.array([0, 0, 0])
        self.orbital_distance = 150  # pixels - reduced for better visibility
        
        # Calculate initial orbital period (constant throughout simulation)
        self.initial_period = 2 * np.pi * np.sqrt(self.orbital_distance**3 / (self.G * self.central_mass))
        
        # Initialize OpenGL settings
        self.setup_gl()
        
        # Initialize the solar system
        self.create_solar_system()
    
    def setup_gl(self):
        """Initialize OpenGL settings."""
        # Set up the viewport
        glViewport(0, 0, self.width, self.height) # type: ignore
        
        # Set up the projection matrix
        glMatrixMode(GL_PROJECTION) # type: ignore
        glLoadIdentity() # type: ignore
        gluPerspective(45, (self.width/self.height), 0.1, 1000.0) # type: ignore
        glMatrixMode(GL_MODELVIEW) # type: ignore
        
        # Enable features
        glEnable(GL_DEPTH_TEST) # type: ignore
        glEnable(GL_LIGHTING) # type: ignore
        glEnable(GL_LIGHT0) # type: ignore
        glEnable(GL_COLOR_MATERIAL) # type: ignore
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE) # type: ignore
        
        # Set up light
        glLight(GL_LIGHT0, GL_POSITION, (0, 0, 1, 0)) # type: ignore
        glLight(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1)) # type: ignore
        glLight(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1)) # type: ignore
        
        # Set background color
        glClearColor(0.0, 0.0, 0.0, 1.0) # type: ignore
    
    def create_solar_system(self):
        """Create the solar system with 3D positions."""
        # Central body (yellow)
        center = CelestialBody(
            mass=self.central_mass,
            position=self.initial_sun_pos.copy(),
            velocity=np.array([0, 0, 0]),  # Central body stays stationary
            radius=30,
            color=(255, 255, 0)
        )
        
        # Create orbiting bodies
        bodies = []
        num_outer_bodies = 1
        for i in range(num_outer_bodies):
            # Calculate position on a circle in the x-y plane
            angle = i * (2 * np.pi / num_outer_bodies)
            x = self.orbital_distance * np.cos(angle)
            y = self.orbital_distance * np.sin(angle)
            z = 0  # Start in the x-y plane
            
            # Calculate velocity for circular orbit using v = sqrt(GM/r)
            vel_magnitude = np.sqrt(self.G * self.central_mass / self.orbital_distance)
            vel_x = -vel_magnitude * np.sin(angle)  # Perpendicular to position
            vel_y = vel_magnitude * np.cos(angle)   # Perpendicular to position
            vel_z = 0  # No initial z velocity
            
            # Create the body with unique color
            body = CelestialBody(
                mass=10,
                position=np.array([x, y, z]),
                velocity=np.array([vel_x, vel_y, vel_z]),
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
    
    def draw_sphere(self, radius, slices, stacks):
        """Draw a sphere using OpenGL."""
        for i in range(stacks):
            lat0 = np.pi * (-0.5 + float(i) / stacks)
            z0 = np.sin(lat0)
            zr0 = np.cos(lat0)
            lat1 = np.pi * (-0.5 + float(i + 1) / stacks)
            z1 = np.sin(lat1)
            zr1 = np.cos(lat1)
            
            glBegin(GL_QUAD_STRIP) # type: ignore
            for j in range(slices + 1):
                lng = 2 * np.pi * float(j) / slices
                x = np.cos(lng)
                y = np.sin(lng)
                
                glVertex3f(radius * x * zr0, radius * y * zr0, radius * z0) # type: ignore
                glVertex3f(radius * x * zr1, radius * y * zr1, radius * z1) # type: ignore
            glEnd() # type: ignore
    
    def draw_spherical_grid(self, radius, num_latitudes=16, num_longitudes=16):
        """Draw a spherical grid around the central object."""
        # Draw latitude circles
        for i in range(num_latitudes):
            lat = np.pi * (-0.5 + float(i) / num_latitudes)
            z = np.sin(lat)
            r = np.cos(lat)
            
            glBegin(GL_LINE_LOOP) # type: ignore
            glColor4f(1.0, 0.5, 0.0, 0.3) # type: ignore # Semi-transparent orange
            for j in range(num_longitudes):
                lng = 2 * np.pi * float(j) / num_longitudes
                x = r * np.cos(lng)
                y = r * np.sin(lng)
                glVertex3f(radius * x, radius * y, radius * z) # type: ignore
            glEnd() # type: ignore
        
        # Draw longitude lines
        for j in range(num_longitudes):
            lng = 2 * np.pi * float(j) / num_longitudes
            glBegin(GL_LINE_STRIP) # type: ignore
            glColor4f(1.0, 0.5, 0.0, 0.3) # type: ignore # Semi-transparent orange
            for i in range(num_latitudes + 1):
                lat = np.pi * (-0.5 + float(i) / num_latitudes)
                z = np.sin(lat)
                r = np.cos(lat)
                x = r * np.cos(lng)
                y = r * np.sin(lng)
                glVertex3f(radius * x, radius * y, radius * z) # type: ignore
            glEnd() # type: ignore
    
    def draw_trail(self, trail, color):
        """Draw the trail of a celestial body."""
        if len(trail) > 1:
            glBegin(GL_LINE_STRIP) # type: ignore
            for i, pos in enumerate(trail):
                alpha = i / len(trail)
                glColor4f(*color[:3], alpha) # type: ignore
                glVertex3f(*pos) # type: ignore
            glEnd() # type: ignore
    
    def draw(self):
        """Draw all bodies to the screen using OpenGL."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # type: ignore
        glLoadIdentity() # type: ignore
        
        # Set up camera
        gluLookAt( # type: ignore
            self.camera_position[0], self.camera_position[1], self.camera_position[2],
            0, 0, 0,
            0, 1, 0
        )
        
        # Draw coordinate axes for reference (optional)
        glBegin(GL_LINES) # type: ignore    
        # X axis (red)
        glColor3f(1, 0, 0) # type: ignore
        glVertex3f(0, 0, 0) # type: ignore
        glVertex3f(100, 0, 0) # type: ignore
        # Y axis (green)
        glColor3f(0, 1, 0) # type: ignore
        glVertex3f(0, 0, 0) # type: ignore
        glVertex3f(0, 100, 0) # type: ignore
        # Z axis (blue)
        glColor3f(0, 0, 1) # type: ignore
        glVertex3f(0, 0, 0) # type: ignore
        glVertex3f(0, 0, 100) # type: ignore
        glEnd() # type: ignore
        
        # Draw spherical grid around central object (radius = 1.5 * central body radius)
        self.draw_spherical_grid(30*1)  # 30 * 1.5 = 45
        
        # Draw trails
        for body in self.bodies:
            self.draw_trail(body.trail, body.color)
        
        # Draw bodies
        for body in self.bodies:
            glPushMatrix() # type: ignore
            glTranslatef(*body.position) # type: ignore
            glColor3f(*body.color[:3]) # type: ignore
            self.draw_sphere(body.radius, 32, 32) # type: ignore
            glPopMatrix() # type: ignore
        
        # Draw UI elements on top
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw UI elements using OpenGL."""
        # Save current matrix state
        glMatrixMode(GL_PROJECTION) # type: ignore
        glPushMatrix() # type: ignore
        glLoadIdentity() # type: ignore
        glOrtho(0, self.width, self.height, 0, -1, 1) # type: ignore
        glMatrixMode(GL_MODELVIEW) # type: ignore
        glPushMatrix() # type: ignore
        glLoadIdentity() # type: ignore
        
        # Disable depth testing and lighting for UI
        glDisable(GL_DEPTH_TEST) # type: ignore
        glDisable(GL_LIGHTING) # type: ignore
        
        # Enable blending for transparency
        glEnable(GL_BLEND) # type: ignore
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # type: ignore
        
        # Draw semi-transparent background for settings
        glBegin(GL_QUADS) # type: ignore
        glColor4f(0, 0, 0, 0.5) # type: ignore # Semi-transparent black
        glVertex2f(5, 15) # type: ignore
        glVertex2f(305, 15) # type: ignore
        glVertex2f(305, 215) # type: ignore
        glVertex2f(5, 215) # type: ignore
        glEnd() # type: ignore
        
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
        text_data = pygame.image.tostring(text_surface, "RGBA", True) # type: ignore
        glRasterPos2i(10, 20) # type: ignore
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data) # type: ignore
        
        # Draw FPS
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.font.render(fps_text, True, (255, 255, 255))
        fps_data = pygame.image.tostring(fps_surface, "RGBA", True) # type: ignore
        glRasterPos2i(10, 40) # type: ignore
        glDrawPixels(fps_surface.get_width(), fps_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, fps_data) # type: ignore
        
        # Draw orbital periods
        y_offset = 60
        for i, body in enumerate(self.bodies[1:], 1):
            period_text = f"Orbital Period (Body {i}): {self.initial_period:.1f} days"
            period_surface = self.font.render(period_text, True, body.color[:3])
            period_data = pygame.image.tostring(period_surface, "RGBA", True) # type: ignore
            glRasterPos2i(10, y_offset) # type: ignore
            glDrawPixels(period_surface.get_width(), period_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, period_data) # type: ignore
            y_offset += 20
        
        # Draw controls help
        controls_text = "Controls: Space = Pause/Unpause, C = Toggle Acceleration Type, R = Reset, Esc = Exit"
        controls_surface = self.font.render(controls_text, True, (255, 255, 255))
        controls_data = pygame.image.tostring(controls_surface, "RGBA", True) # type: ignore
        glRasterPos2i(10, self.height - 30) # type: ignore
        glDrawPixels(controls_surface.get_width(), controls_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, controls_data) # type: ignore
        
        # Draw camera controls
        camera_text = "Camera: Arrow keys = Rotate, +/- = Zoom"
        camera_surface = self.font.render(camera_text, True, (255, 255, 255))
        camera_data = pygame.image.tostring(camera_surface, "RGBA", True) # type: ignore
        glRasterPos2i(10, self.height - 50) # type: ignore
        glDrawPixels(camera_surface.get_width(), camera_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, camera_data) # type: ignore
        
        # Draw start message when paused and time is 0
        if self.paused and self.simulation_time == 0:
            start_text = "Press SPACE to start the simulation"
            start_surface = self.large_font.render(start_text, True, (255, 255, 255))
            start_data = pygame.image.tostring(start_surface, "RGBA", True)
            text_rect = start_surface.get_rect(center=(self.width/2, self.height/2 + 100))
            glRasterPos2i(text_rect.x, text_rect.y) # type: ignore
            glDrawPixels(start_surface.get_width(), start_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, start_data) # type: ignore
        
        # Restore matrix state
        glMatrixMode(GL_PROJECTION) # type: ignore
        glPopMatrix() # type: ignore
        glMatrixMode(GL_MODELVIEW) # type: ignore
        glPopMatrix() # type: ignore
        
        # Re-enable depth testing and lighting
        glEnable(GL_DEPTH_TEST) # type: ignore
        glEnable(GL_LIGHTING) # type: ignore
        glDisable(GL_BLEND) # type: ignore
    
    def handle_camera_controls(self, keys):
        """Handle camera rotation and zoom controls."""
        # Handle mouse movement for camera rotation
        if self.mouse_control:
            current_mouse_pos = pygame.mouse.get_pos()
            if self.last_mouse_pos is not None:
                dx = current_mouse_pos[0] - self.last_mouse_pos[0]
                dy = current_mouse_pos[1] - self.last_mouse_pos[1]
                
                # Update camera rotation based on mouse movement
                self.camera_rotation[1] += dx * self.rotation_speed
                self.camera_rotation[0] += dy * self.rotation_speed
                
                # Clamp vertical rotation to prevent camera flipping
                self.camera_rotation[0] = max(-89, min(89, self.camera_rotation[0]))
            
            self.last_mouse_pos = current_mouse_pos
        
        # Update camera position based on rotation and distance
        self.camera_position[0] = self.camera_distance * np.sin(np.radians(self.camera_rotation[1]))
        self.camera_position[1] = self.camera_distance * np.sin(np.radians(self.camera_rotation[0]))
        self.camera_position[2] = self.camera_distance * np.cos(np.radians(self.camera_rotation[0])) * np.cos(np.radians(self.camera_rotation[1]))
    
    def run(self):
        """Main simulation loop."""
        running = True
        dt = 100  # Smaller time step for smoother motion
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.mouse_control = True
                        pygame.mouse.set_visible(False)  # Hide cursor while controlling
                        self.last_mouse_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.mouse_control = False
                        pygame.mouse.set_visible(True)  # Show cursor when not controlling
                        self.last_mouse_pos = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_c:
                        self.use_constant_acceleration = not self.use_constant_acceleration
                    elif event.key == pygame.K_r:
                        self.reset_simulation()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                        self.camera_distance = max(self.min_zoom, self.camera_distance - self.zoom_speed)
                        # Update camera position immediately after zoom
                        self.handle_camera_controls(pygame.key.get_pressed())
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        self.camera_distance = min(self.max_zoom, self.camera_distance + self.zoom_speed)
                        # Update camera position immediately after zoom
                        self.handle_camera_controls(pygame.key.get_pressed())
            
            # Handle camera controls
            keys = pygame.key.get_pressed()
            self.handle_camera_controls(keys)
            
            self.update(dt)
            self.draw()
            self.clock.tick(120)
        
        pygame.quit()

if __name__ == "__main__":
    simulator = WorldSimulator()
    simulator.run() 