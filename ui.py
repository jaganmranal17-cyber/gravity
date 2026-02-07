import pygame
import numpy as np
from visualization import WHITE, BLACK, GOLD, SCREEN_WIDTH, SCREEN_HEIGHT

# Initialize fonts
_font = None
_title_font = None
_small_font = None

def init_fonts():
    global _font, _title_font, _small_font
    try:
        # Try to use a more modern system font if available
        available = pygame.font.get_fonts()
        pref = ["segoeui", "verdana", "arial"]
        chosen = "arial"
        for p in pref:
            if p in available:
                chosen = p
                break
        _font = pygame.font.SysFont(chosen, 16)
        _title_font = pygame.font.SysFont(chosen, 20, bold=True)
        _small_font = pygame.font.SysFont(chosen, 12, bold=True)
    except:
        _font = pygame.font.SysFont("Arial", 16)
        _title_font = pygame.font.SysFont("Arial", 20, bold=True)
        _small_font = pygame.font.SysFont("Arial", 12, bold=True)

class Button:
    def __init__(self, x, y, w, h, text, color=(40, 44, 52), hover_color=(56, 62, 73)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = np.array(color)
        self.hover_color = np.array(hover_color)
        self.current_color = np.array(color, dtype=float)
        self.is_hovered = False
        self.alpha = 180
        self.anim_speed = 0.15

    def draw(self, surface):
        # Interpolate color for smooth hover effect
        target = self.hover_color if self.is_hovered else self.base_color
        self.current_color += (target - self.current_color) * self.anim_speed
        
        # Draw glassmorphism background
        btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        color_with_alpha = list(self.current_color.astype(int)) + [self.alpha]
        pygame.draw.rect(btn_surf, color_with_alpha, btn_surf.get_rect(), border_radius=8)
        
        # Border glow
        border_color = (120, 150, 200, 100) if self.is_hovered else (80, 80, 80, 60)
        pygame.draw.rect(btn_surf, border_color, btn_surf.get_rect(), 2, border_radius=8)
        
        surface.blit(btn_surf, self.rect.topleft)
        
        # Text
        txt_color = WHITE if not self.is_hovered else GOLD
        txt_surf = _font.render(self.text, True, txt_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = min_val
        self.label = label
        self.handle_rect = pygame.Rect(x, y - 4, 14, h + 8)
        self.update_handle()
        self.dragging = False
        self.is_hovered = False

    def update_handle(self):
        pos = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * (self.rect.width - 14)
        self.handle_rect.x = pos

    def draw(self, surface):
        # Draw Label
        label_txt = _small_font.render(self.label.upper(), True, (150, 150, 150))
        val_txt = _font.render(f"{int(self.val)}x", True, WHITE)
        surface.blit(label_txt, (self.rect.x, self.rect.y - 25))
        surface.blit(val_txt, (self.rect.right - val_txt.get_width(), self.rect.y - 28))
        
        # Draw Track
        track_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(track_surf, (50, 50, 50, 150), track_surf.get_rect(), border_radius=4)
        
        # Draw Progress
        progress_w = int((self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        if progress_w > 0:
            progress_rect = pygame.Rect(0, 0, progress_w, self.rect.height)
            pygame.draw.rect(track_surf, (80, 120, 255, 180), progress_rect, border_radius=4)
        
        surface.blit(track_surf, self.rect.topleft)
        
        # Draw Handle
        handle_color = (255, 255, 255) if self.dragging or self.is_hovered else (200, 200, 200)
        pygame.draw.rect(surface, handle_color, self.handle_rect, border_radius=4)
        if self.dragging:
             pygame.draw.rect(surface, GOLD, self.handle_rect, 2, border_radius=4)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos) or self.handle_rect.collidepoint(event.pos)
            if self.dragging:
                rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width - 14))
                self.val = self.min_val + (rel_x / (self.rect.width - 14)) * (self.max_val - self.min_val)
                self.update_handle()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.dragging = True
                rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width - 14))
                self.val = self.min_val + (rel_x / (self.rect.width - 14)) * (self.max_val - self.min_val)
                self.update_handle()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

class SystemSelector:
    def __init__(self):
        self.systems = [
            "Solar System", "Extended Solar System", "Jovian System", 
            "Saturnian System", "Uranian System", "Neptunian System",
            "Earth-Moon", "Pluto System", "Mars System", "TRAPPIST-1"
        ]
        self.buttons = []
        for i, name in enumerate(self.systems):
            self.buttons.append(Button(25, 60 + i * 38, 170, 32, name))
        
        self.speed_slider = Slider(25, 60 + len(self.systems) * 38 + 50, 170, 8, 1, 200, "Simulation Speed")
        self.current_system = "Solar System"
        self.loading = False
        self.rect = pygame.Rect(10, 10, 200, 60 + len(self.systems) * 38 + 100)

    def draw(self, surface):
        # Draw Panel Background (Glassmorphism)
        panel_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 24, 30, 200), panel_surf.get_rect(), border_radius=15)
        # Border
        pygame.draw.rect(panel_surf, (100, 100, 100, 80), panel_surf.get_rect(), 2, border_radius=15)
        surface.blit(panel_surf, self.rect.topleft)

        # Draw Title
        title_surf = _title_font.render("SIMULATION CONTROL", True, GOLD)
        surface.blit(title_surf, (self.rect.x + 15, self.rect.y + 20))
        pygame.draw.line(surface, (80, 80, 80), (self.rect.x + 15, self.rect.y + 45), (self.rect.right - 15, self.rect.y + 45), 1)

        for btn in self.buttons:
            btn.draw(surface)
            
        self.speed_slider.draw(surface)

        if self.loading:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            loading_txt = _title_font.render("ESTABLISHING LINK...", True, GOLD)
            txt_rect = loading_txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(loading_txt, txt_rect)

    def handle_event(self, event):
        self.speed_slider.handle_event(event)
        
        if event.type == pygame.MOUSEMOTION:
            for btn in self.buttons:
                btn.check_hover(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.rect.collidepoint(event.pos):
                    if btn.text != self.current_system:
                        return btn.text
        return None
