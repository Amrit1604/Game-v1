import math
import pygame

from scenes import BaseScene
from ui.phase1_ui import BLOOD_RED, VOID_BLACK


class DeathScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.font = fonts["italic"]
        self.elapsed = 0.0
        self.lines = [
            (1.5, "Your heart... stopped."),
            (3.5, "The world faded to silence."),
            (5.5, "Everything you knew... is gone."),
        ]

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.elapsed += dt
        self.particles.update(dt * 0.55)
        if self.elapsed >= 8.5:
            self.next_scene = "void"

    def _line_alpha(self, start):
        fade_in_time = 1.0
        t = (self.elapsed - start) / fade_in_time
        t = max(0.0, min(1.0, t))
        return int(t * 255)

    def draw(self, screen):
        width, height = screen.get_size()

        tint = pygame.Surface((width, height), pygame.SRCALPHA)
        tint.fill((50, 0, 0, 22))
        screen.blit(tint, (0, 0))

        t = self.elapsed
        radius = 60 + math.sin(t * 3.0) * 15
        if t > 7.0:
            p = min(1.0, (t - 7.0) / 1.5)
            radius *= (1.0 - p)

        if radius > 1:
            ring_alpha = int(180 * (0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * 3.0))))
            ring = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*BLOOD_RED, ring_alpha), (110, 110), int(radius), 3)
            screen.blit(ring, (width // 2 - 110, height // 2 - 140))

        for idx, (start, text) in enumerate(self.lines):
            alpha = self._line_alpha(start)
            if alpha <= 0:
                continue
            txt = self.font.render(text, True, BLOOD_RED)
            txt.set_alpha(alpha)
            y = height // 2 + 12 + idx * 46
            screen.blit(txt, (width // 2 - txt.get_width() // 2, y))
