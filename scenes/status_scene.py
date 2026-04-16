import pygame
import math
from scene_manager import Scene
from scenes.death_input_scene import DeathInputScene
from ui.fantasy_frame import FantasyFrame
from ui.particle_system import ParticleSystem

class StatusScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0
        self.duration = 4.0 # Switch after 4 seconds
        self.font = pygame.font.SysFont("timesnewroman", 36)
        
        # Load frame and center it
        width, height = pygame.display.get_surface().get_size()
        self.frame_rect = pygame.Rect(width//2 - 400, height//2 - 300, 800, 600)
        self.frame = FantasyFrame(self.frame_rect)
        self.particles = ParticleSystem()
        
    def update(self, dt):
        self.timer += dt
        
        # Particles only appear when frame opens
        self.particles.update(dt, self.frame.rect)
        
        if self.timer >= self.duration:
            self.manager.change_scene(DeathInputScene(self.manager))

    def draw(self, screen):
        screen.fill((8, 12, 20))
        
        # Particles
        self.particles.draw(screen)
        
        # Frame
        self.frame.draw(screen)
        
        # Title Text (Pulsing Glow Effect)
        time_ms = pygame.time.get_ticks()
        glow_intensity = 150 + int(math.sin(time_ms * 0.003) * 105)
        
        glow_text = self.font.render("SYSTEM MESSAGE", True, (120, 180, 255))
        glow_text.set_alpha(glow_intensity)
        text = self.font.render("SYSTEM MESSAGE", True, (255, 255, 255))

        title_pos = (self.frame.rect.centerx - text.get_width() // 2, self.frame.rect.top + 40)
        
        screen.blit(glow_text, (title_pos[0] + 2, title_pos[1] + 2))
        screen.blit(text, title_pos)

    def handle_event(self, event):
        pass