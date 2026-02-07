import pygame
import numpy as np
from math import log10, pi
import data
import physics
import ui
import visualization

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((visualization.SCREEN_WIDTH, visualization.SCREEN_HEIGHT))
pygame.display.set_caption("Orbital Mechanics Simulator (RK4)")
ui.init_fonts()

# --- Camera state (Target and Current for Lerping) ---
cam_r_target = 800
cam_theta_target = pi / 4
cam_phi_target = pi / 6

cam_r = cam_r_target
cam_theta = cam_theta_target
cam_phi = cam_phi_target

dragging = False
last_mouse = (0, 0)
cam_lerp_speed = 0.12

# Main game objects
running = True
frame_count = 0
selector = ui.SystemSelector()
starfield = visualization.Starfield(350)
clock = pygame.time.Clock()

def load_system(name):
    print(f"Loading system: {name}")
    data_package = data.get_system_data(name)
    return data_package["state"], data_package["G"]

state, G = load_system("Solar System")
dt = 0.01

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle UI events
        new_system = selector.handle_event(event)
        if new_system:
            selector.loading = True
            starfield.draw(screen, cam_theta, cam_phi)
            selector.draw(screen)
            pygame.display.flip()
            
            state, G = load_system(new_system)
            selector.current_system = new_system
            selector.loading = False
            frame_count = 0
            cam_r_target = 1500 if ("System" in new_system and new_system != "Solar System") else 800

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click was on UI
            ui_rect = selector.rect
            if not ui_rect.collidepoint(event.pos):
                if event.button == 1:
                    dragging = True
                    last_mouse = event.pos
                elif event.button == 4:  # scroll up
                    cam_r_target *= 0.85
                elif event.button == 5:  # scroll down
                    cam_r_target *= 1.15

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            mx, my = event.pos
            dx = mx - last_mouse[0]
            dy = my - last_mouse[1]
            last_mouse = (mx, my)

            cam_theta_target += dx * 0.003
            cam_phi_target -= dy * 0.003
            cam_phi_target = max(-pi / 2 + 0.1, min(pi / 2 - 0.1, cam_phi_target))

    # --- Camera Interpolation (Lerping) ---
    cam_r += (cam_r_target - cam_r) * cam_lerp_speed
    cam_theta += (cam_theta_target - cam_theta) * cam_lerp_speed
    cam_phi += (cam_phi_target - cam_phi) * cam_lerp_speed
    
    project_3d = visualization.get_projection_func(cam_r, cam_phi, cam_theta)

    # --- Calculation ---
    steps_per_frame = int(selector.speed_slider.val)
    for _ in range(steps_per_frame):
        state = physics.rk4_step(state, dt, G)
        
        # Add trail points with higher detail
        if frame_count % max(1, steps_per_frame // 6) == 0:
            for p in state:
                trail = p[4]
                pos = (p[1][0], p[2][0], p[3][0])
                trail.append(pos)
                if len(trail) > 350:
                    trail.pop(0)
    
    frame_count += 1

    # --- Rendering ---
    # 1. Background
    starfield.draw(screen, cam_theta, cam_phi)
    
    # 2. Trails (Tapered rendering)
    trail_surface = pygame.Surface((visualization.SCREEN_WIDTH, visualization.SCREEN_HEIGHT), pygame.SRCALPHA)
    for particle in state:
        trail = particle[4]
        if len(trail) < 2: continue

        proj_trail = []
        step = max(1, len(trail) // 60)
        for i in range(0, len(trail), step):
            p = project_3d(*trail[i])
            if p: proj_trail.append(p)
        
        # Always include the last point for precision
        p_last = project_3d(*trail[-1])
        if p_last: proj_trail.append(p_last)

        visualization.draw_tapered_trail(trail_surface, proj_trail, particle[6])

    screen.blit(trail_surface, (0, 0))
    
    # 3. Bodies
    drawables = []
    for particle in state:
        proj = project_3d(particle[1][0], particle[2][0], particle[3][0])
        if proj:
            sx, sy, depth = proj
            # Perspective-based size
            vis_size = max(0.5, log10(particle[0]) + 2) if particle[0] > 0 else 1
            radius = max(1, int(vis_size * 550 / depth))
            drawables.append((depth, sx, sy, radius, particle[6], particle[5]))

    drawables.sort(key=lambda x: x[0], reverse=True)
    for depth, sx, sy, r, c, name in drawables:
        # Core
        pygame.draw.circle(screen, c, (sx, sy), r)
        
        # Subtle Highlight
        hl_color = [min(255, channel + 100) for channel in c]
        pygame.draw.circle(screen, hl_color, (sx - r//3, sy - r//3), max(1, r//4))
        
        # Label (only for larger bodies or if hovered)
        if depth < 5500:
            label_surf = ui._font.render(name, True, (210, 210, 210))
            screen.blit(label_surf, (sx + r + 10, sy - 10))

    # 4. UI
    selector.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

    # 4. UI
    selector.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
