import random
import pygame

from scenes import BaseScene
from ui.particle_system import ParticleSystem
from ui.phase1_ui import BLOOD_RED, GOLD, PURPLE_LIGHT, TEXT_COLOR, TEXT_DIM, VOID_BLACK, draw_dialogue_box


class VoidScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.font = fonts["body"]
        self.panel_title_font = fonts["small"]
        self.panel_font = fonts["ui"]
        self.elapsed = 0.0
        # Double density look for this scene while still reusing shared particles.
        self.extra_particles = ParticleSystem(count=150)
        for particle in self.extra_particles.particles:
            particle["color"] = random.choice(((201, 168, 76), (180, 140, 220)))

    def handle_events(self, events):
        pass

    def update(self, dt):
        self.elapsed += dt
        self.particles.update(dt)
        self.extra_particles.update(dt)
        if self.elapsed >= 8.0:
            self.next_scene = "goddess"

    def _fade_alpha(self, start, duration=0.9):
        t = (self.elapsed - start) / duration
        t = max(0.0, min(1.0, t))
        return int(t * 255)

    def draw(self, screen):
        width, height = screen.get_size()
        self.extra_particles.draw(screen)

        events = [
            (0.5, "Soul detected."),
            (2.3, "Consciousness... intact."),
            (4.1, "Initiating divine evaluation protocol..."),
        ]

        y0 = height // 2 - 170
        for idx, (start, text) in enumerate(events):
            alpha = self._fade_alpha(start)
            if alpha <= 0:
                continue
            txt = self.font.render(text, True, PURPLE_LIGHT)
            txt.set_alpha(alpha)
            screen.blit(txt, (width // 2 - txt.get_width() // 2, y0 + idx * 34))

        if self.elapsed >= 5.5:
            panel_alpha = self._fade_alpha(5.5)
            panel = draw_dialogue_box(screen, width // 2 - 210, height // 2 - 10, 420, 200)

            title = self.panel_title_font.render("✦  DIVINE SOUL REGISTRY  ✦", True, GOLD)
            title.set_alpha(panel_alpha)
            screen.blit(title, (panel.centerx - title.get_width() // 2, panel.top + 18))

            rows = [
                ("Status:", "DECEASED", BLOOD_RED),
                ("Soul Integrity:", "100%", TEXT_COLOR),
                ("Origin World:", "Mortal Realm", TEXT_COLOR),
            ]

            y = panel.top + 58
            for label, value, value_color in rows:
                l_s = self.panel_font.render(label, True, TEXT_DIM)
                v_s = self.panel_font.render(value, True, value_color)
                l_s.set_alpha(panel_alpha)
                v_s.set_alpha(panel_alpha)
                screen.blit(l_s, (panel.left + 28, y))
                screen.blit(v_s, (panel.left + 170, y))
                y += 34

            blink_on = (pygame.time.get_ticks() // 320) % 2 == 0
            tail = "▌" if blink_on else " "
            footer = self.panel_font.render(f"Awaiting evaluation...  {tail}", True, TEXT_DIM)
            footer.set_alpha(panel_alpha)
            screen.blit(footer, (panel.left + 28, panel.bottom - 42))
