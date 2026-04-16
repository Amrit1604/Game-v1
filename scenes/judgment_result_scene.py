import pygame
from scene_manager import Scene
from ui.fantasy_frame import FantasyFrame

class JudgmentResultScene(Scene):
    def __init__(self, manager, traits):
        super().__init__(manager)
        self.traits = traits
        self.width, self.height = pygame.display.get_surface().get_size()
        self.frame_rect = pygame.Rect(self.width//2 - 400, self.height//2 - 300, 800, 600)
        self.frame = FantasyFrame(self.frame_rect)
        
        self.title_font = pygame.font.SysFont("georgia", 36, bold=True)
        self.text_font = pygame.font.SysFont("georgia", 24)
        
        # Calculate alignment
        if self.traits["morality"] >= 5:
            self.alignment = "Heroic"
            self.message = "You lived with honor and kindness."
        elif self.traits["morality"] <= -5:
            self.alignment = "Villainous"
            self.message = "You sought power at the expense of others."
        else:
            self.alignment = "Neutral"
            self.message = "Your life was a balance of light and dark."
            
        # Top trait
        self.top_trait = max(self.traits, key=self.traits.get).capitalize()
        
    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((5, 8, 14))
        self.frame.draw(screen)
        
        title_text = self.title_font.render("FINAL JUDGMENT", True, (240, 240, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, self.frame_rect.top + 80))
        
        align_text = self.text_font.render(f"Alignment: {self.alignment}", True, (150, 200, 255))
        top_trait_text = self.text_font.render(f"Top Trait: {self.top_trait}", True, (150, 200, 255))
        msg_text = self.text_font.render(f"Message: {self.message}", True, (200, 200, 200))
        
        screen.blit(align_text, (self.width // 2 - align_text.get_width() // 2, self.frame_rect.top + 200))
        screen.blit(top_trait_text, (self.width // 2 - top_trait_text.get_width() // 2, self.frame_rect.top + 260))
        screen.blit(msg_text, (self.width // 2 - msg_text.get_width() // 2, self.frame_rect.top + 320))
        
        cont_text = self.text_font.render("Press ENTER to continue to next phase", True, (100, 100, 100))
        screen.blit(cont_text, (self.width // 2 - cont_text.get_width() // 2, self.frame_rect.bottom - 80))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            print("System Phase 1 Complete. Awaiting Phase 2+.")
