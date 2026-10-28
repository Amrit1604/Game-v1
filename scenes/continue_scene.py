"""
ContinueScene — shown on startup when a save.json exists.
Displays the saved character's info with a cinematic loading bar,
then fades into the MapScene.
"""

import math
import pygame
from scenes import BaseScene
from ui.phase1_ui import (
    GOLD,
    GOLD_LIGHT,
    GOLD_DIM,
    TEXT_COLOR,
    TEXT_DIM,
    VOID_BLACK,
    wrap_text,
)


# Loading messages that scroll through during the bar animation
_LOAD_LINES = [
    "Awakening soul record...",
    "Restoring memories of past life...",
    "Locating Kingdom of Ariana...",
    "Calibrating reincarnation anchor...",
    "Syncing with the Goddess's blessing...",
    "Preparing your destiny...",
]


class ContinueScene(BaseScene):
    """
    Shown instead of TitleScene when a valid save is detected.
    Reads the save data from game_state (pre-populated by main.py),
    shows a dramatic "Continuing your journey" loader, then transitions to 'map'.
    """

    LOAD_DURATION = 3.2   # total seconds for the loader bar to fill
    FADE_IN_SPD   = 1.8   # alpha units per second (0→1)

    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.elapsed    = 0.0
        self.fade_in    = 0.0
        self.done       = False          # has the bar finished?
        self.exit_timer = 0.0            # short pause after bar completes
        self.line_idx   = 0             # current loading message index

        self.body_font  = fonts["body"]
        self.ui_font    = fonts["ui"]
        self.small_font = fonts["small"]
        self.title_font = fonts["title"]

        # Particle drift
        self.particles  = particles

        # Pull display info from save (stored in game_state by main.py)
        self.save_name  = game_state.get("player_name",  "Unknown Hero")
        self.save_class = game_state.get("player_class", "???")
        self.save_world = game_state.get("world_name",   "???")

    # ──────────────────────────────────────────────────────────────────────────
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # ESC always bails to title
                self.next_scene = "title"
            # Allow skipping the loader with SPACE / ENTER
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_SPACE, pygame.K_RETURN
            ):
                self.elapsed = self.LOAD_DURATION
                self.done = True

    def update(self, dt):
        self.elapsed += dt
        self.particles.update(dt)

        # Fade in
        if self.fade_in < 1.0:
            self.fade_in = min(1.0, self.fade_in + self.FADE_IN_SPD * dt)

        # Advance loading message
        progress = min(1.0, self.elapsed / self.LOAD_DURATION)
        target_line = int(progress * len(_LOAD_LINES))
        self.line_idx = min(target_line, len(_LOAD_LINES) - 1)

        # Loader complete
        if self.elapsed >= self.LOAD_DURATION and not self.done:
            self.done = True

        if self.done:
            self.exit_timer += dt
            if self.exit_timer >= 0.7:
                self.next_scene = "map"

    # ──────────────────────────────────────────────────────────────────────────
    def draw(self, screen):
        w, h = screen.get_size()
        screen.fill(VOID_BLACK)

        # Ambient particles
        self.particles.draw(screen)

        alpha = int(self.fade_in * 255)
        if alpha <= 0:
            return

        # ── "CONTINUING YOUR JOURNEY" headline ───────────────────────────────
        headline = self.title_font.render("CONTINUING", True, GOLD_LIGHT)
        headline.set_alpha(alpha)
        screen.blit(headline, (w // 2 - headline.get_width() // 2, 80))

        sub = self.body_font.render("your journey continues in the Kingdom of Ariana", True, GOLD_DIM)
        sub.set_alpha(alpha)
        screen.blit(sub, (w // 2 - sub.get_width() // 2, 158))

        # ── Decorative line ───────────────────────────────────────────────────
        pygame.draw.line(screen, (*GOLD_DIM, alpha), (w // 2 - 300, 200), (w // 2 + 300, 200), 1)

        # ── Character card ────────────────────────────────────────────────────
        card_w, card_h = 560, 180
        card_x = w // 2 - card_w // 2
        card_y = 225

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((6, 4, 8, int(0.85 * alpha)))
        screen.blit(card_surf, (card_x, card_y))

        # Gold border + corner accents
        border_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, (*GOLD, alpha), (0, 0, card_w, card_h), 1)
        acc = 14
        for pts in [
            ((0,0),(acc,0),(0,acc)),
            ((card_w,0),(card_w-acc,0),(card_w,acc)),
            ((0,card_h),(acc,card_h),(0,card_h-acc)),
            ((card_w,card_h),(card_w-acc,card_h),(card_w,card_h-acc)),
        ]:
            pygame.draw.line(border_surf, (*GOLD, alpha), pts[0], pts[1], 2)
            pygame.draw.line(border_surf, (*GOLD, alpha), pts[0], pts[2], 2)
        screen.blit(border_surf, (card_x, card_y))

        # Soul icon (small glow circle)
        cx_icon = card_x + 48
        cy_icon = card_y + card_h // 2
        glow_r = 18
        glow_surf = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
        pulse = 0.5 + 0.5 * math.sin(self.elapsed * 2.8)
        glow_a = int((100 + pulse * 60) * (alpha / 255))
        pygame.draw.circle(glow_surf, (255, 230, 140, glow_a), (glow_r * 2, glow_r * 2), glow_r * 2)
        pygame.draw.circle(glow_surf, (255, 255, 255, alpha), (glow_r * 2, glow_r * 2), glow_r // 2)
        screen.blit(glow_surf, (cx_icon - glow_r * 2, cy_icon - glow_r * 2))

        # Name / class / world rows
        tx = card_x + 90
        ty = card_y + 30
        row_gap = 38

        label_col = (*GOLD_DIM, alpha)
        val_col   = (*GOLD_LIGHT, alpha)

        def _blitA(surf, x, y):
            surf.set_alpha(alpha)
            screen.blit(surf, (x, y))

        _blitA(self.small_font.render("SOUL RECORD", True, GOLD_DIM), tx, ty - 12)
        pygame.draw.line(screen, (*GOLD_DIM, int(alpha * 0.6)), (tx, ty + 6), (tx + card_w - 100, ty + 6), 1)

        rows = [
            ("Name",  self.save_name),
            ("Class", self.save_class),
            ("World", self.save_world),
        ]
        for i, (label, val) in enumerate(rows):
            lbl_s = self.ui_font.render(f"{label}:", True, GOLD_DIM)
            val_s = self.body_font.render(val, True, GOLD_LIGHT)
            _blitA(lbl_s, tx, ty + 18 + i * row_gap)
            _blitA(val_s, tx + 80, ty + 14 + i * row_gap)

        # ── Loading bar ───────────────────────────────────────────────────────
        bar_y   = 448
        bar_w   = 700
        bar_h   = 8
        bar_x   = w // 2 - bar_w // 2

        progress = min(1.0, self.elapsed / self.LOAD_DURATION)

        # Track
        track_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        track_surf.fill((*GOLD_DIM, int(60 * (alpha / 255))))
        screen.blit(track_surf, (bar_x, bar_y))

        # Fill
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            fill_surf = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
            # Gradient: left dim, right bright
            for px in range(fill_w):
                ratio = px / max(fill_w - 1, 1)
                r = int(130 + ratio * 110)
                g = int(100 + ratio * 78)
                b = int(30 + ratio * 10)
                pygame.draw.line(fill_surf, (r, g, b, alpha), (px, 0), (px, bar_h - 1))
            screen.blit(fill_surf, (bar_x, bar_y))

        # Leading glow
        if 0 < fill_w < bar_w:
            tip_x = bar_x + fill_w
            tip_surf = pygame.Surface((30, bar_h + 10), pygame.SRCALPHA)
            pygame.draw.ellipse(tip_surf, (*GOLD_LIGHT, int(180 * (alpha / 255))), (0, 0, 30, bar_h + 10))
            screen.blit(tip_surf, (tip_x - 15, bar_y - 5))

        # Border around track
        pygame.draw.rect(screen, (*GOLD_DIM, int(100 * (alpha / 255))), (bar_x, bar_y, bar_w, bar_h), 1)

        # ── Loading message ───────────────────────────────────────────────────
        msg = _LOAD_LINES[self.line_idx]
        if self.done:
            msg = "Journey restored. Welcome back."
        msg_color = GOLD if self.done else TEXT_DIM
        msg_surf = self.ui_font.render(msg, True, msg_color)
        msg_surf.set_alpha(alpha)
        screen.blit(msg_surf, (w // 2 - msg_surf.get_width() // 2, bar_y + 18))

        # Progress %
        pct_surf = self.small_font.render(f"{int(progress * 100)}%", True, GOLD_DIM)
        pct_surf.set_alpha(alpha)
        screen.blit(pct_surf, (bar_x + bar_w + 10, bar_y - 2))

        # ── Skip hint ─────────────────────────────────────────────────────────
        if not self.done:
            hint_a = int((100 + 80 * (0.5 + 0.5 * math.sin(self.elapsed * 2.0))) * (alpha / 255))
            hint = self.small_font.render(
                "[ SPACE / ENTER ] Skip  ·  [ ESC ] Return to Title",
                True, GOLD_DIM
            )
            hint.set_alpha(hint_a)
            screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 32))
