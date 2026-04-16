import math
import pygame

from scenes import BaseScene
from ui.phase1_ui import GOLD, GOLD_DIM, GOLD_LIGHT, VOID_BLACK, draw_letter_spaced


class TitleScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.title_font = fonts["title"]
        self.subtitle_font = fonts["subtitle"]
        self.prompt_font = fonts["body"]
        self.time_s = 0.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.next_scene = "death"

    def update(self, dt):
        self.time_s += dt
        self.particles.update(dt)

    def draw(self, screen):
        width, height = screen.get_size()

        title_text = "REBORN INTO DARKNESS"
        glow = self.title_font.render(title_text, True, GOLD)
        glow.set_alpha(60)
        txt = self.title_font.render(title_text, True, GOLD_LIGHT)
        tx = width // 2 - txt.get_width() // 2
        ty = height // 2 - 170
        screen.blit(glow, (tx, ty + 2))
        screen.blit(txt, (tx, ty))

        line_w = 300
        line_y = ty + txt.get_height() + 24
        pygame.draw.line(
            screen,
            GOLD,
            (width // 2 - line_w // 2, line_y),
            (width // 2 + line_w // 2, line_y),
            1,
        )

        subtitle = "A Soul Reincarnation RPG"
        draw_letter_spaced(
            screen,
            subtitle,
            self.subtitle_font,
            GOLD_DIM,
            width // 2,
            line_y + 28,
            spacing=1,
        )

        pulse = 0.5 + 0.5 * math.sin(self.time_s * 2.1)
        alpha = int(80 + pulse * 175)
        prompt = self.prompt_font.render("✦  Press ENTER to Begin Your Fate  ✦", True, GOLD_LIGHT)
        prompt.set_alpha(alpha)
        screen.blit(prompt, (width // 2 - prompt.get_width() // 2, height - 92))
