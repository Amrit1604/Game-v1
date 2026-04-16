import threading

import pygame

from groq_client import ask_goddess
from scenes import BaseScene
from ui.phase1_ui import (
    GOLD,
    GOLD_DIM,
    TEXT_COLOR,
    VOID_BLACK,
    Typewriter,
    draw_dialogue_box,
    draw_gold_button,
    draw_goddess_silhouette,
    draw_text_wrapped,
    draw_text_wrapped_clipped,
)


class IdentityScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.tag_font = fonts["small"]
        self.body_font = fonts["body"]
        self.ui_font = fonts["ui"]

        self.step = 1
        self.typewriter = Typewriter()
        self.typewriter.set_text(
            "Before I can weave your new destiny, I must know who you truly were. "
            "Speak your name unto the void."
        )

        self.name_input = ""
        self.story_input = ""
        self.personality_choice = ""
        self.waiting = False
        self.pending_target = ""
        self.result = {"text": None, "done": False}

        self.choice_items = [
            ("Courage", "I act without hesitation"),
            ("Caution", "I assess before striking"),
            ("Cunning", "I seek the hidden advantage"),
            ("Compassion", "I protect those beside me"),
        ]
        self.choice_rects = []
        self._build_choice_rects()

        self.advance_timer = 0.0

    def _build_choice_rects(self):
        width = 1280
        left = width // 2 - (280 * 2 + 24) // 2
        top = 470
        self.choice_rects = [
            pygame.Rect(left, top, 280, 70),
            pygame.Rect(left + 304, top, 280, 70),
            pygame.Rect(left, top + 94, 280, 70),
            pygame.Rect(left + 304, top + 94, 280, 70),
        ]

    def _request(self, prompt, target):
        self.waiting = True
        self.pending_target = target
        self.result = {"text": None, "done": False}

        def worker():
            self.result["text"] = ask_goddess(prompt, max_tokens=160, max_sentences=2, max_words=42)
            self.result["done"] = True

        threading.Thread(target=worker, daemon=True).start()

    def _submit_name(self):
        name = self.name_input.strip()
        if not name:
            return
        self.game_state["player_name"] = name
        prompt = (
            f'The soul\'s name is "{name}". React to their name in 1-2 sentences '
            "divinely and poetically. Then ask them to tell you about their mortal life."
        )
        self._request(prompt, "step2")

    def _submit_story(self):
        story = self.story_input.strip()
        if not story:
            return
        self.game_state["player_story"] = story
        name = self.game_state.get("player_name", "Unknown")
        prompt = (
            f'The soul named "{name}" lived as: "{story}". React with divine wisdom '
            "in 2 sentences. Then ask: When faced with danger, what rises first - "
            "Courage, Caution, Cunning, or Compassion?"
        )
        self._request(prompt, "step3")

    def _submit_personality(self, choice):
        self.personality_choice = choice
        self.game_state["player_personality"] = choice
        prompt = (
            f'The soul chose "{choice}" as their instinct under danger. React in '
            "1-2 sentences divinely. Then say the judgment is about to begin."
        )
        self._request(prompt, "advance")

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN and event.type != pygame.MOUSEBUTTONDOWN:
                continue

            if self.waiting:
                continue

            if self.step == 1 and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self._submit_name()
                elif event.unicode.isprintable() and len(self.name_input) < 40:
                    self.name_input += event.unicode

            elif self.step == 2 and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.story_input = self.story_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self._submit_story()
                elif event.unicode.isprintable() and len(self.story_input) < 600:
                    self.story_input += event.unicode

            elif self.step == 3 and self.typewriter.done and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = event.pos
                for idx, rect in enumerate(self.choice_rects):
                    if rect.collidepoint(mouse):
                        self._submit_personality(self.choice_items[idx][0])
                        break

    def update(self, dt):
        self.particles.update(dt)
        self.typewriter.update(dt)

        if self.waiting and self.result["done"]:
            text = self.result["text"] or "[The goddess is silent.]"
            self.typewriter.set_text(text)
            self.waiting = False

            if self.pending_target == "step2":
                self.step = 2
            elif self.pending_target == "step3":
                self.step = 3
            elif self.pending_target == "advance":
                self.step = 4
                self.advance_timer = 0.0

            self.pending_target = ""

        if self.step == 4 and self.typewriter.done:
            self.advance_timer += dt
            if self.advance_timer >= 2.0:
                self.next_scene = "judgment"

    def _draw_input_box(self, screen, rect, text, label):
        pygame.draw.rect(screen, VOID_BLACK, rect)
        pygame.draw.rect(screen, GOLD, rect, width=1)

        label_s = self.tag_font.render(label, True, GOLD_DIM)
        screen.blit(label_s, (rect.left, rect.top - 20))

        visible_text = text
        if self.body_font.size(visible_text)[0] > rect.width - 20:
            while visible_text and self.body_font.size(visible_text)[0] > rect.width - 20:
                visible_text = visible_text[1:]

        t = self.body_font.render(visible_text, True, TEXT_COLOR)
        screen.blit(t, (rect.left + 10, rect.centery - t.get_height() // 2))

        blink = (pygame.time.get_ticks() // 350) % 2 == 0
        if blink:
            cx = rect.left + 10 + t.get_width() + 2
            pygame.draw.rect(screen, GOLD, (cx, rect.top + 10, 2, rect.height - 20))

    def draw(self, screen):
        width, _ = screen.get_size()

        draw_goddess_silhouette(screen, pygame.time.get_ticks() / 1000.0, pos=(220, 92), scale=0.72)

        panel = draw_dialogue_box(screen, 160, 220, 960, 220)
        tag = self.tag_font.render("✦  GODDESS ELYRIA", True, GOLD)
        screen.blit(tag, (panel.left + 22, panel.top + 14))
        pygame.draw.line(screen, GOLD, (panel.left + 22, panel.top + 38), (panel.right - 22, panel.top + 38), 1)

        if self.waiting and not self.result["done"]:
            dots = 1 + (pygame.time.get_ticks() // 220) % 3
            wait_txt = self.body_font.render("." * dots, True, TEXT_COLOR)
            screen.blit(wait_txt, (panel.left + 22, panel.top + 56))
        else:
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

        if self.step == 1:
            self._draw_input_box(
                screen,
                pygame.Rect(340, 480, 600, 50),
                self.name_input,
                "Your name in the mortal world",
            )

        elif self.step == 2:
            rect = pygame.Rect(340, 470, 600, 120)
            pygame.draw.rect(screen, VOID_BLACK, rect)
            pygame.draw.rect(screen, GOLD, rect, width=1)
            label = self.tag_font.render("Tell me of your mortal life", True, GOLD_DIM)
            screen.blit(label, (rect.left, rect.top - 20))

            # Multi-line wrapped preview in a taller field.
            draw_text_wrapped(screen, self.story_input, self.ui_font, TEXT_COLOR, rect.left + 10, rect.top + 10, rect.width - 20)
            blink = (pygame.time.get_ticks() // 350) % 2 == 0
            if blink:
                pygame.draw.rect(screen, GOLD, (rect.right - 10, rect.bottom - 24, 2, 16))

            submit_rect = pygame.Rect(960, 598, 160, 30)
            hovered = submit_rect.collidepoint(pygame.mouse.get_pos())
            draw_gold_button(screen, "Submit", submit_rect, self.ui_font, hovered)

        elif self.step == 3 and self.typewriter.done:
            mouse = pygame.mouse.get_pos()
            for idx, rect in enumerate(self.choice_rects):
                title, desc = self.choice_items[idx]
                hovered = rect.collidepoint(mouse)
                draw_gold_button(screen, "", rect, self.ui_font, hovered)
                t1 = self.ui_font.render(f"{chr(65 + idx)}) {title}", True, TEXT_COLOR)
                t2 = self.tag_font.render(desc, True, GOLD_DIM)
                screen.blit(t1, (rect.left + 12, rect.top + 12))
                screen.blit(t2, (rect.left + 12, rect.top + 40))
