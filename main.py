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

# Camera state
cam_r = 800
cam_theta = pi / 4
cam_phi = pi / 6
dragging = False
last_mouse = (0, 0)

# Main game initialization
running = True
frame_count = 0
selector = ui.SystemSelector()
clock = pygame.time.Clock()

def load_system(name):
    print(f"Loading system: {name}")
    data_package = data.get_system_data(name)
    return data_package["state"], data_package["G"]

state, G = load_system("Solar System")
dt = 0.01

while running:
    # Update projection function based on current camera
    project_3d = visualization.get_projection_func(cam_r, cam_phi, cam_theta)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle UI events
        new_system = selector.handle_event(event)
        if new_system:
            selector.loading = True
            screen.fill(visualization.BLACK)
            selector.draw(screen)
            pygame.display.flip()
            
            state, G = load_system(new_system)
            selector.current_system = new_system
            selector.loading = False
            frame_count = 0
            if "System" in new_system and new_system != "Solar System":
                cam_r = 1500
            else:
                cam_r = 800

        elif event.type == pygame.MOUSEBUTTONDOWN:
            ui_clicked = any(btn.rect.collidepoint(event.pos) for btn in selector.buttons)
            ui_clicked = ui_clicked or selector.speed_slider.rect.collidepoint(event.pos)
            ui_clicked = ui_clicked or selector.speed_slider.handle_rect.collidepoint(event.pos)
            
            if not ui_clicked:
                if event.button == 1:
                    dragging = True
                    last_mouse = event.pos
                elif event.button == 4:  # scroll up
                    cam_r *= 0.75
                elif event.button == 5:  # scroll down
                    cam_r *= 1.25

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            mx, my = event.pos
            dx = mx - last_mouse[0]
            dy = my - last_mouse[1]
            last_mouse = (mx, my)

            cam_theta += dx * 0.002
            cam_phi -= dy * 0.002
            cam_phi = max(-pi / 2 + 0.01, min(pi / 2 - 0.01, cam_phi))

    # Physics and Rendering
    screen.fill(visualization.BLACK)
    trail_surface = pygame.Surface((visualization.SCREEN_WIDTH, visualization.SCREEN_HEIGHT), pygame.SRCALPHA)

    steps_per_frame = int(selector.speed_slider.val)
    for _ in range(steps_per_frame):
        state = physics.rk4_step(state, dt, G)
        
        # Add trail points
        if steps_per_frame < 50 or frame_count % (steps_per_frame // 10 + 1) == 0:
            for p in state:
                trail = p[4]
                pos = (p[1][0], p[2][0], p[3][0])
                trail.append(pos)
                if len(trail) > 600:
                    trail.pop(0)
    
    frame_count += 1

    # Draw Trails
    for particle in state:
        trail = particle[4]
        color = particle[6]
        if len(trail) < 2: continue

        step = max(1, steps_per_frame // 2)
        proj_trail = []
        for i in range(0, len(trail), step):
            p = project_3d(*trail[i])
            if p: proj_trail.append(p)
        
        p_last = project_3d(*trail[-1])
        if p_last: proj_trail.append(p_last)

        if len(proj_trail) < 2: continue
        for i in range(len(proj_trail) - 1):
            x0, y0, _ = proj_trail[i]
            x1, y1, _ = proj_trail[i+1]
            alpha = int(180 * (i / len(proj_trail))**2)
            pygame.draw.line(trail_surface, list(color) + [alpha], (x0, y0), (x1, y1), 2)

    screen.blit(trail_surface, (0, 0))
    
    # Draw Bodies
    drawables = []
    for particle in state:
        proj = project_3d(particle[1][0], particle[2][0], particle[3][0])
        if proj:
            sx, sy, depth = proj
            vis_size = max(0.5, log10(particle[0]) + 2) if particle[0] > 0 else 1
            radius = max(1, int(vis_size * 500 / depth))
            drawables.append((depth, sx, sy, radius, particle[6], particle[5]))

    drawables.sort(key=lambda x: x[0], reverse=True)
    for depth, sx, sy, r, c, name in drawables:
        pygame.draw.circle(screen, c, (sx, sy), r)
        # Draw Labels
        label_surf = ui._font.render(name, True, c)
        screen.blit(label_surf, (sx + r + 5, sy - 10))

    selector.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()