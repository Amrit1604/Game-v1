import pygame
from scene_manager import Scene


class WorldScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.title_font = pygame.font.SysFont("georgia", 36, bold=True)
        self.body_font = pygame.font.SysFont("arial", 22)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((8, 11, 18))
        title = self.title_font.render("NEW WORLD AWAKENING", True, (220, 230, 255))
        subtitle = self.body_font.render("Phase 2 starts here.", True, (150, 170, 210))

        width, height = screen.get_size()
        screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 40))
        screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, height // 2 + 10))

    def handle_event(self, event):
        pass
