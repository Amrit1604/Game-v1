import pygame
from scene_manager import Scene
from ui.fantasy_frame import FantasyFrame
from ui.text_box import TextBox
from ui.particle_system import ParticleSystem
import math

class DeathInputScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.width, self.height = pygame.display.get_surface().get_size()
        
        self.frame_rect = pygame.Rect(self.width//2 - 400, self.height//2 - 300, 800, 600)
        self.frame = FantasyFrame(self.frame_rect)
        self.particles = ParticleSystem()
        
        # Better, cleaner fonts
        self.label_font = pygame.font.SysFont("georgia", 18, italic=True)
        self.title_font = pygame.font.SysFont("georgia", 28, bold=True)
        
        # Form dimensions focused tightly within the inner area of the frame
        box_width = 340
        box_height = 36
        start_x = self.width // 2 - box_width // 2
        start_y = self.height // 2 - 120
        spacing = 80
        
        # Setup form fields
        self.fields = [
            {"label": "How did you perish?", "box": TextBox((start_x, start_y, box_width, box_height))},
            {"label": "Given Name", "box": TextBox((start_x, start_y + spacing, box_width, box_height))},
            {"label": "Date of Birth", "box": TextBox((start_x, start_y + spacing * 2, box_width, box_height))},
            {"label": "Form/Gender", "box": TextBox((start_x, start_y + spacing * 3, box_width, box_height))}
        ]
        
    def update(self, dt):
        self.particles.update(dt, self.frame_rect)
        for field in self.fields:
            field["box"].update(dt)

    def draw(self, screen):
        # Darker, moodier background
        screen.fill((5, 8, 14))
        
        # Particles & Frame
        self.particles.draw(screen)
        self.frame.draw(screen)
        
        # Glowing Title
        time_ms = pygame.time.get_ticks()
        glow_val = 150 + int(math.sin(time_ms * 0.003) * 50)
        
        glow_text = self.title_font.render("PLAYER REGISTRATION", True, (100, 150, 255))
        glow_text.set_alpha(glow_val)
        title_text = self.title_font.render("PLAYER REGISTRATION", True, (240, 240, 255))
        
        title_x = self.width // 2 - title_text.get_width() // 2
        title_y = self.height // 2 - 220
        
        screen.blit(glow_text, (title_x + 2, title_y + 2))
        screen.blit(title_text, (title_x, title_y))
        
        # Draw fields
        for field in self.fields:
            label_text = self.label_font.render(field["label"], True, (180, 200, 220))
            # Left-align label with the input box, nicely offset vertically
            screen.blit(label_text, (field["box"].rect.x, field["box"].rect.y - 24))
            field["box"].draw(screen)

    def handle_event(self, event):
        for field in self.fields:
            field["box"].handle_event(event)
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                data = {f["label"]: f["box"].text for f in self.fields}
                print("Data gathered:", data)
                print("Transitioning to Goddess Scene...")
                from scenes.goddess_scene import GoddessScene
                self.manager.change_scene(GoddessScene(self.manager))
