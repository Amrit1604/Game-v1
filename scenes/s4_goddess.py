import math
import threading

import pygame

from groq_client import ask_goddess
from scenes import BaseScene
from ui.phase1_ui import (
    GOLD,
    TEXT_COLOR,
    VOID_BLACK,
    Typewriter,
    draw_dialogue_box,
    draw_gold_button,
    draw_goddess_silhouette,
    wrap_text,
)


class GoddessScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.tag_font = fonts["small"]
        self.body_font = fonts["ui"]
        self.button_font = fonts["ui"]
        self.typewriter = Typewriter()

        self.result = {"text": None, "done": False}
        self.loading_pulse = 0.0
        self._start_request()

        self.continue_rect = pygame.Rect(970, 576, 140, 30)

    def _start_request(self):
        prompt = (
            "A new soul has arrived in the void. Greet them, gently tell them they "
            "have died, explain that you will evaluate their soul for reincarnation "
            "into a new fantasy world. Be mystical and dramatic in 2 short sentences."
        )

        def worker():
            self.result["text"] = ask_goddess(prompt, max_tokens=120)
            self.result["done"] = True

        threading.Thread(target=worker, daemon=True).start()

    def handle_events(self, events):
        if not self.result["done"] or not self.typewriter.done:
            return

        hovered = self.continue_rect.collidepoint(pygame.mouse.get_pos())
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.next_scene = "identity"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hovered:
                self.next_scene = "identity"

    def update(self, dt):
        self.particles.update(dt)
        self.loading_pulse += dt

        if self.result["done"] and not self.typewriter.full_text:
            self.typewriter.set_text(self.result["text"])

        self.typewriter.update(dt)

    def draw(self, screen):
        width, _ = screen.get_size()

        draw_goddess_silhouette(screen, pygame.time.get_ticks() / 1000.0, pos=(width // 2, 80), scale=1.0)

        panel = draw_dialogue_box(screen, 160, 420, 960, 200)
        self.continue_rect = pygame.Rect(panel.right - 150, panel.bottom - 42, 130, 28)

        tag = self.tag_font.render("✦  GODDESS ELYRIA", True, GOLD)
        screen.blit(tag, (panel.left + 22, panel.top + 14))
        pygame.draw.line(screen, GOLD, (panel.left + 22, panel.top + 38), (panel.right - 22, panel.top + 38), 1)

        if self.result["done"]:
            visible = self.typewriter.visible_text
            reserve_button = self.typewriter.done
            max_w = panel.width - 46 - (self.continue_rect.width + 20 if reserve_button else 0)
            all_lines = wrap_text(visible, self.body_font, max_w)

            line_h = self.body_font.get_linesize() + 4
            y = panel.top + 54
            max_lines = max(1, (panel.bottom - 16 - y) // line_h)
            lines = all_lines[-max_lines:]

            for ln in lines:
                txt = self.body_font.render(ln, True, TEXT_COLOR)
                screen.blit(txt, (panel.left + 22, y))
                y += line_h
        else:
            dots = 1 + int((self.loading_pulse * 2.0) % 3)
            txt = self.body_font.render("." * dots, True, TEXT_COLOR)
            alpha = int(120 + 135 * (0.5 + 0.5 * math.sin(self.loading_pulse * 4.0)))
            txt.set_alpha(alpha)
            screen.blit(txt, (panel.left + 22, panel.top + 56))

        if self.result["done"] and self.typewriter.done:
            hovered = self.continue_rect.collidepoint(pygame.mouse.get_pos())
            draw_gold_button(screen, "Continue →", self.continue_rect, self.button_font, hovered)
