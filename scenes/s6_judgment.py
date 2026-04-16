import threading

import pygame

from groq_client import ask_goddess
from scenes import BaseScene
from ui.phase1_ui import (
    GOLD,
    GOLD_DIM,
    PURPLE_LIGHT,
    TEXT_COLOR,
    VOID_BLACK,
    Typewriter,
    draw_dialogue_box,
    draw_gold_button,
    draw_text_wrapped_clipped,
)


class JudgmentScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.tag_font = fonts["small"]
        self.body_font = fonts["body"]
        self.ui_font = fonts["ui"]

        self.typewriter = Typewriter()
        self.elapsed = 0.0

        self.result = {"text": None, "done": False}
        self._request_judgment()

        self.class_cards = [
            {
                "name": "WARRIOR",
                "stats": {"HP": 5, "STR": 4, "AGI": 2, "MAG": 1},
            },
            {
                "name": "SHADOW MAGE",
                "stats": {"HP": 3, "STR": 2, "AGI": 3, "MAG": 5},
            },
            {
                "name": "DIVINE RANGER",
                "stats": {"HP": 3, "STR": 3, "AGI": 5, "MAG": 2},
            },
        ]
        self.selected_idx = None
        self.accept_rect = pygame.Rect(940, 650, 220, 36)

    def _request_judgment(self):
        name = self.game_state.get("player_name", "Unknown")
        story = self.game_state.get("player_story", "Unknown")
        personality = self.game_state.get("player_personality", "Unknown")
        prompt = (
            f'Judge the soul of "{name}" who lived as: "{story}". '\
            f'Their instinct under danger is: "{personality}". '\
            "Give a dramatic divine judgment of their soul's nature (2-3 sentences). "
            "Recommend ONE class: Warrior (strength/combat), Shadow Mage (dark magic/stealth), "
            "or Divine Ranger (agility/archery). Explain why. End by saying: choose your path."
        )

        def worker():
            self.result["text"] = ask_goddess(prompt, max_tokens=220, max_sentences=3, max_words=46)
            self.result["done"] = True

        threading.Thread(target=worker, daemon=True).start()

    def handle_events(self, events):
        if not self.result["done"] or not self.typewriter.done:
            return

        mouse = pygame.mouse.get_pos()
        card_rects = self._card_rects()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(card_rects):
                    if rect.collidepoint(mouse):
                        self.selected_idx = idx
                        self.game_state["player_class"] = self.class_cards[idx]["name"]
                        return

                if self.selected_idx is not None and self.accept_rect.collidepoint(mouse):
                    self.next_scene = "portal"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.selected_idx is not None:
                self.next_scene = "portal"

    def update(self, dt):
        self.elapsed += dt
        self.particles.update(dt)

        if self.result["done"] and not self.typewriter.full_text:
            self.typewriter.set_text(self.result["text"])

        self.typewriter.update(dt)

    def _card_rects(self):
        width = 1280
        card_w, card_h = 200, 260
        gap = 28
        total = card_w * 3 + gap * 2
        start_x = width // 2 - total // 2
        y = 360
        return [pygame.Rect(start_x + i * (card_w + gap), y, card_w, card_h) for i in range(3)]

    def _draw_icon(self, screen, rect, idx):
        cx, cy = rect.centerx, rect.top + 64
        if idx == 0:
            pygame.draw.line(screen, GOLD, (cx - 3, cy - 28), (cx + 3, cy + 24), 4)
            pygame.draw.polygon(screen, GOLD, [(cx - 7, cy - 22), (cx + 7, cy - 22), (cx, cy - 36)])
            pygame.draw.rect(screen, GOLD, (cx - 11, cy + 20, 22, 4))
        elif idx == 1:
            pygame.draw.circle(screen, PURPLE_LIGHT, (cx, cy), 22)
            pygame.draw.circle(screen, VOID_BLACK, (cx + 9, cy - 3), 18)
        else:
            pygame.draw.arc(screen, GOLD, (cx - 24, cy - 28, 48, 56), 1.8, 4.5, 3)
            pygame.draw.line(screen, GOLD, (cx + 12, cy - 18), (cx + 22, cy + 20), 2)

    def _draw_stats(self, screen, rect, stats):
        y = rect.top + 114
        for label in ("HP", "STR", "AGI", "MAG"):
            filled = stats[label]
            empty = 5 - filled
            stars = "★" * filled + "✩" * empty
            txt = self.tag_font.render(f"{label}  {stars}", True, GOLD if filled > 0 else GOLD_DIM)
            screen.blit(txt, (rect.left + 14, y))
            y += 30

    def draw(self, screen):
        width, height = screen.get_size()

        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            beam_x = width // 2 - 120 + i * 120
            beam_alpha = int(20 + 25 * (0.5 + 0.5 * (1 if i % 2 == 0 else -1) * __import__("math").sin(t * 1.6 + i)))
            beam = pygame.Surface((18, height), pygame.SRCALPHA)
            beam.fill((255, 255, 255, max(8, min(55, beam_alpha))))
            screen.blit(beam, (beam_x, 0))

        label = self.tag_font.render("SOUL EVALUATION", True, GOLD_DIM)
        screen.blit(label, (width // 2 - label.get_width() // 2, 38))

        bar_outer = pygame.Rect(width // 2 - 100, 60, 200, 10)
        pygame.draw.rect(screen, GOLD_DIM, bar_outer, width=1)
        fill_ratio = min(1.0, self.elapsed / 2.5)
        if fill_ratio > 0:
            fill = pygame.Rect(bar_outer.left + 1, bar_outer.top + 1, int((bar_outer.width - 2) * fill_ratio), bar_outer.height - 2)
            pygame.draw.rect(screen, GOLD, fill)

        panel = draw_dialogue_box(screen, 180, 120, 920, 200)
        tag = self.tag_font.render("✦  DIVINE JUDGMENT", True, GOLD)
        screen.blit(tag, (panel.left + 22, panel.top + 14))
        pygame.draw.line(screen, GOLD, (panel.left + 22, panel.top + 38), (panel.right - 22, panel.top + 38), 1)

        if self.result["done"]:
            draw_text_wrapped_clipped(
                screen,
                self.typewriter.visible_text,
                self.body_font,
                TEXT_COLOR,
                panel.left + 22,
                panel.top + 54,
                panel.width - 44,
                panel.height - 70,
            )
        else:
            dots = 1 + (pygame.time.get_ticks() // 220) % 3
            wait_txt = self.body_font.render("." * dots, True, TEXT_COLOR)
            screen.blit(wait_txt, (panel.left + 22, panel.top + 56))

        if self.result["done"] and self.typewriter.done:
            mouse = pygame.mouse.get_pos()
            for idx, rect in enumerate(self._card_rects()):
                hovered = rect.collidepoint(mouse)
                selected = self.selected_idx == idx
                draw_rect = rect.move(0, -4 if hovered else 0)

                bg = (20, 16, 8) if hovered else VOID_BLACK
                pygame.draw.rect(screen, bg, draw_rect)
                pygame.draw.rect(screen, GOLD if selected else GOLD_DIM, draw_rect, width=2 if selected else 1)

                if selected:
                    glow = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                    glow.fill((201, 168, 76, 24))
                    screen.blit(glow, draw_rect.topleft)

                # Corner accents
                accent = 12
                pygame.draw.line(screen, GOLD, draw_rect.topleft, (draw_rect.left + accent, draw_rect.top), 2)
                pygame.draw.line(screen, GOLD, draw_rect.topleft, (draw_rect.left, draw_rect.top + accent), 2)
                pygame.draw.line(screen, GOLD, draw_rect.bottomright, (draw_rect.right - accent, draw_rect.bottom), 2)
                pygame.draw.line(screen, GOLD, draw_rect.bottomright, (draw_rect.right, draw_rect.bottom - accent), 2)

                name = self.ui_font.render(self.class_cards[idx]["name"], True, TEXT_COLOR)
                screen.blit(name, (draw_rect.centerx - name.get_width() // 2, draw_rect.top + 16))
                self._draw_icon(screen, draw_rect, idx)
                self._draw_stats(screen, draw_rect, self.class_cards[idx]["stats"])

            if self.selected_idx is not None:
                hovered = self.accept_rect.collidepoint(mouse)
                draw_gold_button(screen, "Accept My Destiny →", self.accept_rect, self.ui_font, hovered)
