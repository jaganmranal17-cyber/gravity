import pygame
import numpy as np
import random
from math import cos, sin, pi, log10

# ---------- Colors ----------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 204, 0)
SPACE_BLUE = (10, 12, 20)

# ---------- Rendering Constants ----------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

class Starfield:
    def __init__(self, count=200):
        self.stars = []
        for _ in range(count):
            # x, y, size, layer (for parallax)
            self.stars.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.uniform(0.5, 1.8),
                random.uniform(0.1, 0.5)
            ])

    def draw(self, surface, cam_theta, cam_phi):
        surface.fill(SPACE_BLUE)
        for star in self.stars:
            # Simple parallax effect based on camera rotation
            offsetX = (cam_theta * 100 * star[3]) % SCREEN_WIDTH
            offsetY = (cam_phi * 100 * star[3]) % SCREEN_HEIGHT
            
            x = (star[0] + offsetX) % SCREEN_WIDTH
            y = (star[1] + offsetY) % SCREEN_HEIGHT
            
            brightness = int(255 * (star[3] / 0.5))
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (int(x), int(y)), int(star[2]))

def draw_tapered_trail(surface, proj_trail, color):
    """Draws a trail that tapers in thickness and fades in alpha."""
    if len(proj_trail) < 2: return
    
    for i in range(len(proj_trail) - 1):
        x0, y0, _ = proj_trail[i]
        x1, y1, _ = proj_trail[i+1]
        
        # Fading and Tapering
        progress = i / len(proj_trail)
        alpha = int(100 * progress**1.5)
        width = max(1, int(3 * progress))
        
        pygame.draw.line(surface, list(color) + [alpha], (x0, y0), (x1, y1), width)

def get_projection_func(cam_r, cam_phi, cam_theta):
    """Returns a projection function for the current camera state."""
    
    def project_3d(x, y, z):
        # Camera position (spherical → cartesian)
        cx = cam_r * cos(cam_phi) * cos(cam_theta)
        cy = cam_r * sin(cam_phi)
        cz = cam_r * cos(cam_phi) * sin(cam_theta)

        # Translate point into camera space
        px = x - cx
        py = y - cy
        pz = z - cz

        # Camera basis (look-at origin)
        forward = np.array([-cx, -cy, -cz])
        norm = np.linalg.norm(forward)
        if norm == 0: forward = np.array([0, 0, -1])
        else: forward /= norm

        right = np.cross([0, 1, 0], forward)
        norm_r = np.linalg.norm(right)
        if norm_r == 0: right = np.array([1, 0, 0])
        else: right /= norm_r

        up = np.cross(forward, right)

        # Coordinates in camera space
        x_cam = np.dot([px, py, pz], right)
        y_cam = np.dot([px, py, pz], up)
        z_cam = np.dot([px, py, pz], forward)

        if z_cam <= 0:
            return None  # behind camera

        # Perspective projection
        f = 600 # Slightly increased FOV effect
        sx = int(SCREEN_WIDTH / 2 + f * x_cam / z_cam)
        sy = int(SCREEN_HEIGHT / 2 - f * y_cam / z_cam)

        return sx, sy, z_cam
        
    return project_3d
