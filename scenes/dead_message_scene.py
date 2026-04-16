import pygame
from scene_manager import Scene
from scenes.glitch_scene import GlitchScene

class DeadMessageScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0
        self.open_duration = 0.5
        self.hold_duration = 2.0
        self.close_duration = 1.0
        self.duration = self.open_duration + self.hold_duration + self.close_duration
        self.width, self.height = pygame.display.get_surface().get_size()
        
        # Using the font from GoddessScreen's "second" YOU DIED that the user liked
        self.font = pygame.font.SysFont("gabriola, georgia", 140, bold=True)

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.manager.change_scene(GlitchScene(self.manager))

    def draw(self, screen):
        screen.fill((0, 0, 0))

        if self.timer < self.open_duration:
            alpha = int((self.timer / self.open_duration) * 255)
        elif self.timer < self.open_duration + self.hold_duration:
            alpha = 255
        else:
            close_t = (self.timer - self.open_duration - self.hold_duration) / self.close_duration
            alpha = int((1.0 - close_t) * 255)

        alpha = max(0, min(255, alpha))

        # Render the large red "YOU DIED" directly at the center
        text = self.font.render("YOU DIED", True, (180, 20, 30))
        text.set_alpha(alpha)
        
        screen.blit(
            text,
            (
                self.width // 2 - text.get_width() // 2,
                self.height // 2 - text.get_height() // 2,
            ),
        )
