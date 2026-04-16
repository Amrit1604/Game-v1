import datetime
import json
import math
import re
import threading

import pygame

from groq_client import ask_goddess
from scenes import BaseScene
from ui.phase1_ui import (
    GOLD,
    GOLD_DIM,
    GOLD_LIGHT,
    PURPLE,
    TEXT_COLOR,
    TEXT_DIM,
    VOID_BLACK,
    WHITE,
    Typewriter,
    draw_dialogue_box,
    draw_gold_button,
    draw_text_wrapped_clipped,
    wrap_text,
)


COMMON_WORDS = {
    "The",
    "And",
    "With",
    "Your",
    "Soul",
    "Portal",
    "World",
    "Into",
    "Darkness",
    "Elyria",
    "Choose",
}


class PortalScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.tag_font = fonts["small"]
        self.body_font = fonts["body"]
        self.ui_font = fonts["ui"]
        self.world_font = fonts["world"]

        self.typewriter = Typewriter()
        self.elapsed = 0.0

        self.result = {"text": None, "done": False}
        self._request_blessing()

        self.state = "dialogue"
        self.flash_alpha = 0.0
        self.black_alpha = 0.0
        self.saved = False

        self.enter_rect = pygame.Rect(500, 650, 280, 40)
        self.play_again_rect = pygame.Rect(540, 470, 200, 38)

    def _request_blessing(self):
        name = self.game_state.get("player_name", "Unknown")
        chosen_class = self.game_state.get("player_class", "WARRIOR")
        prompt = (
            f"{name} has chosen the path of the {chosen_class}. "
            "Give a dramatic emotional farewell blessing (3-4 sentences). "
            "Invent a dark fantasy world name (like Valdremor or Aethenveil) "
            "and give 1 sentence of atmospheric flavor about it. "
            "Wish them luck with divine gravitas. Include the world name in your speech."
        )

        def worker():
            self.result["text"] = ask_goddess(prompt, max_tokens=260, max_sentences=4, max_words=58)
            self.result["done"] = True

        threading.Thread(target=worker, daemon=True).start()

    def _parse_world_name(self, text):
        candidates = re.findall(r"\b[A-Z][a-z]{5,}\b", text or "")
        for cand in candidates:
            if cand not in COMMON_WORDS:
                return cand
        return "Valdremor"

    def _save_record(self):
        if self.saved:
            return

        payload = {
            "name": self.game_state.get("player_name", ""),
            "backstory": self.game_state.get("player_story", ""),
            "class": self.game_state.get("player_class", ""),
            "world": self.game_state.get("world_name", ""),
            "personality": self.game_state.get("player_personality", ""),
            "phase": 1,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        with open("save.json", "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

        self.saved = True

    def handle_events(self, events):
        mouse = pygame.mouse.get_pos()
        for event in events:
            if self.state == "dialogue":
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.enter_rect.collidepoint(mouse)
                    and self.typewriter.done
                ):
                    self.state = "flash_white"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.typewriter.done:
                    self.state = "flash_white"

            elif self.state == "complete":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.play_again_rect.collidepoint(mouse):
                    self.game_state.update(
                        {
                            "player_name": "",
                            "player_story": "",
                            "player_personality": "",
                            "player_class": "",
                            "world_name": "",
                        }
                    )
                    self.next_scene = "title"

    def update(self, dt):
        self.elapsed += dt
        self.particles.update(dt, attract_to=(640, 360), attract_strength=0.08)

        if self.result["done"] and not self.typewriter.full_text:
            text = self.result["text"] or "[The portal hums in silence.]"
            self.typewriter.set_text(text)
            self.game_state["world_name"] = self._parse_world_name(text)

        self.typewriter.update(dt)

        if self.state == "flash_white":
            self.flash_alpha += 620 * dt
            if self.flash_alpha >= 255:
                self.flash_alpha = 255
                self.state = "flash_black"

        elif self.state == "flash_black":
            self.black_alpha += 460 * dt
            if self.black_alpha >= 255:
                self.black_alpha = 255
                self._save_record()
                self.state = "complete"

    def _draw_portal(self, screen):
        center = (640, 360)
        radii = [30, 58, 86, 114, 142, 170, 198, 226]
        time_s = pygame.time.get_ticks() / 1000.0

        for idx, r in enumerate(radii):
            w = r * 2 + 20
            h = int(r * 0.7) + 20
            alpha = max(40, 190 - idx * 18)
            color = GOLD if idx < 4 else PURPLE

            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (*color, alpha), (10, 10, w - 20, h - 20), 2)

            direction = 1 if idx % 2 == 0 else -1
            angle = direction * time_s * 30
            rs = pygame.transform.rotate(surf, angle)
            screen.blit(rs, (center[0] - rs.get_width() // 2, center[1] - rs.get_height() // 2))

        pulse = int(50 + 8 * math.sin(time_s * 3.0))
        glow = pygame.Surface((pulse * 2 + 20, pulse * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*WHITE, 80), (glow.get_width() // 2, glow.get_height() // 2), pulse)
        screen.blit(glow, (center[0] - glow.get_width() // 2, center[1] - glow.get_height() // 2))

    def draw(self, screen):
        self._draw_portal(screen)

        if self.game_state.get("world_name") and self.elapsed > 1.0:
            alpha = min(255, int((self.elapsed - 1.0) / 1.2 * 255))
            world = f"— {self.game_state['world_name'].upper()} —"
            txt = self.world_font.render(world, True, GOLD_LIGHT)
            glow = self.world_font.render(world, True, GOLD)
            glow.set_alpha(90)
            txt.set_alpha(alpha)
            screen.blit(glow, (640 - glow.get_width() // 2, 86 + 2))
            screen.blit(txt, (640 - txt.get_width() // 2, 86))

        if self.state in ("dialogue", "flash_white", "flash_black"):
            panel_w = 920
            panel_x = 180
            panel_bottom = 620
            panel_h = 150

            if self.result["done"]:
                preview_lines = wrap_text(self.typewriter.visible_text, self.ui_font, panel_w - 44)
                line_h = self.ui_font.get_linesize() + 4
                needed_h = 48 + len(preview_lines) * line_h + 16
                panel_h = max(150, min(230, needed_h))

            panel_y = panel_bottom - panel_h
            panel = draw_dialogue_box(screen, panel_x, panel_y, panel_w, panel_h)
            self.enter_rect = pygame.Rect(panel.right - 280, panel.bottom + 14, 280, 40)

            tag = self.tag_font.render("✦  GODDESS ELYRIA", True, GOLD)
            screen.blit(tag, (panel.left + 22, panel.top + 12))
            pygame.draw.line(screen, GOLD, (panel.left + 22, panel.top + 34), (panel.right - 22, panel.top + 34), 1)

            if self.result["done"]:
                draw_text_wrapped_clipped(
                    screen,
                    self.typewriter.visible_text,
                    self.ui_font,
                    TEXT_COLOR,
                    panel.left + 22,
                    panel.top + 44,
                    panel.width - 44,
                    panel.height - 56,
                )
            else:
                dots = 1 + (pygame.time.get_ticks() // 220) % 3
                wait_txt = self.ui_font.render("." * dots, True, TEXT_COLOR)
                screen.blit(wait_txt, (panel.left + 22, panel.top + 44))

            if self.typewriter.done and self.state == "dialogue":
                hovered = self.enter_rect.collidepoint(pygame.mouse.get_pos())
                draw_gold_button(screen, "Enter the Portal ✦", self.enter_rect, self.ui_font, hovered)

        if self.state == "flash_white":
            white = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            white.fill((255, 255, 255, int(self.flash_alpha)))
            screen.blit(white, (0, 0))

        if self.state == "flash_black":
            black = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            black.fill((0, 0, 0, int(self.black_alpha)))
            screen.blit(black, (0, 0))

        if self.state == "complete":
            panel = draw_dialogue_box(screen, 350, 200, 580, 320)
            title = self.tag_font.render("✦  SOUL RECORD SAVED  ✦", True, GOLD)
            screen.blit(title, (panel.centerx - title.get_width() // 2, panel.top + 24))

            rows = [
                f"Name: {self.game_state.get('player_name', '')}",
                f"Class: {self.game_state.get('player_class', '')}",
                f"World: {self.game_state.get('world_name', '')}",
                f"Phase 2 begins in {self.game_state.get('world_name', '')}...",
            ]
            y = panel.top + 86
            for row in rows:
                color = TEXT_COLOR if not row.startswith("Phase 2") else TEXT_DIM
                txt = self.body_font.render(row, True, color)
                screen.blit(txt, (panel.left + 38, y))
                y += 46

            hovered = self.play_again_rect.collidepoint(pygame.mouse.get_pos())
            draw_gold_button(screen, "Play Again", self.play_again_rect, self.ui_font, hovered)
