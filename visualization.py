import pygame
import numpy as np
from math import cos, sin, pi

# ---------- Colors ----------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 204, 0)

# ---------- Rendering Constants ----------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

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
        f = 500
        sx = int(SCREEN_WIDTH / 2 + f * x_cam / z_cam)
        sy = int(SCREEN_HEIGHT / 2 - f * y_cam / z_cam)

        return sx, sy, z_cam
        
    return project_3d
