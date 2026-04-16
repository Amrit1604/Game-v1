import pygame
import random
import math
from scene_manager import Scene
from scenes.goddess_scene import GoddessScene

class GlitchScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0
        self.duration = 1.0
        self.width, self.height = pygame.display.get_surface().get_size()
        self.alert_font = pygame.font.SysFont("consolas", 28, bold=True)
        self.noise_font = pygame.font.SysFont("consolas", 14)

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.manager.change_scene(GoddessScene(self.manager))

    def draw(self, screen):
        screen.fill((0, 0, 0))

        # Large RGB tearing bars.
        for _ in range(56):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            w = random.randint(50, 600)
            h = random.randint(2, 40)
            color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (50, 50, 50)])
            pygame.draw.rect(screen, color, (x, y, w, h))

        # Rapid horizontal tearing lines.
        for _ in range(40):
            y = random.randint(0, self.height - 1)
            shift = random.randint(-90, 90)
            color = random.choice([(30, 120, 255), (240, 240, 240), (255, 70, 70)])
            pygame.draw.line(screen, color, (max(0, shift), y), (self.width + min(0, shift), y), 1)

        # Subtle scan lines for CRT feel.
        for y in range(0, self.height, 3):
            pygame.draw.line(screen, (12, 12, 12), (0, y), (self.width, y), 1)

        # Floating hexadecimal noise.
        for _ in range(12):
            value = hex(random.randint(16, 4095)).upper()
            txt = self.noise_font.render(value, True, (100, 180, 255))
            txt.set_alpha(random.randint(40, 130))
            screen.blit(txt, (random.randint(0, self.width - 80), random.randint(0, self.height - 20)))

        # Alert text flicker with slight jitter.
        if int(self.timer * 24) % 2 == 0:
            pulse = 180 + int(60 * (0.5 + 0.5 * math.sin(self.timer * 40.0)))
            alert = self.alert_font.render("SYSTEM REWRITING FATE", True, (255, 255, 255))
            alert.set_alpha(max(120, min(255, pulse)))
            jitter_x = random.randint(-4, 4)
            jitter_y = random.randint(-2, 2)
            screen.blit(alert, (self.width // 2 - alert.get_width() // 2 + jitter_x, self.height // 2 - 14 + jitter_y))

        # Exit flash for punchier transition.
        if self.timer >= self.duration - 0.14:
            flash_alpha = int(((self.timer - (self.duration - 0.14)) / 0.14) * 255)
            flash = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash.fill((255, 255, 255, max(0, min(255, flash_alpha))))
            screen.blit(flash, (0, 0))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.manager.change_scene(GoddessScene(self.manager))
