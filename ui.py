import pygame
from visualization import WHITE, BLACK, GOLD, SCREEN_WIDTH, SCREEN_HEIGHT

# Initialize fonts (must be called after pygame.init())
_font = None
_title_font = None

def init_fonts():
    global _font, _title_font
    _font = pygame.font.SysFont("Arial", 18)
    _title_font = pygame.font.SysFont("Arial", 22, bold=True)

class Button:
    def __init__(self, x, y, w, h, text, color=(50, 50, 50), hover_color=(80, 80, 80)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (150, 150, 150), self.rect, 1, border_radius=5)
        
        txt_surf = _font.render(self.text, True, WHITE)
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
        self.handle_rect = pygame.Rect(x, y, 10, h)
        self.update_handle()
        self.dragging = False

    def update_handle(self):
        pos = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * (self.rect.width - 10)
        self.handle_rect.x = pos

    def draw(self, surface):
        # Draw Label
        txt = _font.render(f"{self.label}: {int(self.val)}x", True, WHITE)
        surface.blit(txt, (self.rect.x, self.rect.y - 25))
        
        # Draw Bar
        pygame.draw.rect(surface, (100, 100, 100), self.rect, border_radius=5)
        # Draw Handle
        pygame.draw.rect(surface, (200, 200, 200), self.handle_rect, border_radius=3)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width - 10))
            self.val = self.min_val + (rel_x / (self.rect.width - 10)) * (self.max_val - self.min_val)
            self.update_handle()

class SystemSelector:
    def __init__(self):
        self.systems = [
            "Solar System", "Extended Solar System", "Jovian System", 
            "Saturnian System", "Uranian System", "Neptunian System",
            "Earth-Moon", "Pluto System", "Mars System", "TRAPPIST-1"
        ]
        self.buttons = []
        for i, name in enumerate(self.systems):
            self.buttons.append(Button(20, 50 + i * 40, 160, 30, name))
        
        # Add Speed Slider - Linear (1x to 200x)
        self.speed_slider = Slider(20, 50 + len(self.systems) * 40 + 40, 160, 15, 1, 200, "SPEED")
        self.current_system = "Solar System"
        self.loading = False

    def draw(self, surface):
        # Draw Menu Background
        menu_height = 80 + len(self.systems) * 40 + 40
        menu_rect = pygame.Rect(10, 10, 180, menu_height)
        s = pygame.Surface((menu_rect.width, menu_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 180), s.get_rect(), border_radius=10)
        surface.blit(s, menu_rect.topleft)
        pygame.draw.rect(surface, (100, 100, 100), menu_rect, 1, border_radius=10)

        # Draw Title
        title = _title_font.render("SELECT SYSTEM", True, GOLD)
        surface.blit(title, (25, 20))

        for btn in self.buttons:
            btn.draw(surface)
            
        self.speed_slider.draw(surface)

        if self.loading:
            loading_txt = _title_font.render("FETCHING DATA...", True, (255, 50, 50))
            surface.blit(loading_txt, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))

    def handle_event(self, event):
        # Handle Slider
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
