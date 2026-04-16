import math
import os
import pygame


VOID_BLACK = (6, 4, 8)
GOLD = (201, 168, 76)
GOLD_LIGHT = (240, 208, 120)
GOLD_DIM = (100, 80, 35)
PURPLE = (123, 79, 160)
PURPLE_LIGHT = (176, 127, 208)
TEXT_COLOR = (232, 223, 200)
TEXT_DIM = (138, 122, 96)
BLOOD_RED = (180, 40, 40)
WHITE = (255, 255, 255)


def load_font(size, bold=False, italic=False):
    font_dir = os.path.join("assets", "fonts")
    if os.path.isdir(font_dir):
        for file_name in sorted(os.listdir(font_dir)):
            if file_name.lower().endswith((".ttf", ".otf")):
                try:
                    return pygame.font.Font(os.path.join(font_dir, file_name), size)
                except Exception:
                    pass
    return pygame.font.SysFont("georgia", size, bold=bold, italic=italic)


def draw_dialogue_box(screen, x, y, w, h):
    box = pygame.Rect(x, y, w, h)
    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((6, 4, 8, 220))
    screen.blit(bg, (x, y))
    pygame.draw.rect(screen, GOLD, box, width=1)

    accent = 12
    thickness = 2
    pygame.draw.line(screen, GOLD, (box.left, box.top), (box.left + accent, box.top), thickness)
    pygame.draw.line(screen, GOLD, (box.left, box.top), (box.left, box.top + accent), thickness)

    pygame.draw.line(screen, GOLD, (box.right, box.top), (box.right - accent, box.top), thickness)
    pygame.draw.line(screen, GOLD, (box.right, box.top), (box.right, box.top + accent), thickness)

    pygame.draw.line(screen, GOLD, (box.left, box.bottom), (box.left + accent, box.bottom), thickness)
    pygame.draw.line(screen, GOLD, (box.left, box.bottom), (box.left, box.bottom - accent), thickness)

    pygame.draw.line(screen, GOLD, (box.right, box.bottom), (box.right - accent, box.bottom), thickness)
    pygame.draw.line(screen, GOLD, (box.right, box.bottom), (box.right, box.bottom - accent), thickness)

    return box


def wrap_text(text, font, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_text_wrapped(screen, text, font, color, x, y, max_width):
    lines = wrap_text(text, font, max_width)
    line_h = font.get_linesize() + 4
    for idx, line in enumerate(lines):
        txt = font.render(line, True, color)
        screen.blit(txt, (x, y + idx * line_h))
    return len(lines) * line_h


def draw_text_wrapped_clipped(screen, text, font, color, x, y, max_width, max_height, line_gap=4):
    lines = wrap_text(text, font, max_width)
    line_h = font.get_linesize() + line_gap
    max_lines = max(1, max_height // line_h)

    clipped = lines[:max_lines]
    was_clipped = len(lines) > max_lines

    for idx, line in enumerate(clipped):
        txt = font.render(line, True, color)
        screen.blit(txt, (x, y + idx * line_h))

    return {
        "line_height": line_h,
        "max_lines": max_lines,
        "used_lines": len(clipped),
        "used_height": len(clipped) * line_h,
        "clipped": was_clipped,
    }


class Typewriter:
    def __init__(self):
        self.full_text = ""
        self.chars_revealed = 0
        self._carry = 0.0

    def set_text(self, text):
        self.full_text = text or ""
        self.chars_revealed = 0
        self._carry = 0.0

    def update(self, dt):
        # 1 char every 2 frames at 60 FPS => 30 chars/sec
        self._carry += dt * 30.0
        while self._carry >= 1.0 and self.chars_revealed < len(self.full_text):
            self.chars_revealed += 1
            self._carry -= 1.0

    @property
    def visible_text(self):
        return self.full_text[: self.chars_revealed]

    @property
    def done(self):
        return self.chars_revealed >= len(self.full_text)


def draw_gold_button(screen, text, rect, font, hovered):
    bg_color = (20, 16, 8) if hovered else VOID_BLACK
    pygame.draw.rect(screen, bg_color, rect)
    pygame.draw.rect(screen, GOLD, rect, width=1)

    txt = font.render(text, True, GOLD)
    screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
    return rect.collidepoint(pygame.mouse.get_pos())


def draw_letter_spaced(screen, text, font, color, center_x, y, spacing=1):
    chars = []
    total_w = 0
    for ch in text:
        surf = font.render(ch, True, color)
        chars.append(surf)
        total_w += surf.get_width() + spacing
    total_w = max(0, total_w - spacing)

    x = center_x - total_w // 2
    for surf in chars:
        screen.blit(surf, (x, y))
        x += surf.get_width() + spacing


def draw_goddess_silhouette(screen, time_s, pos=(640, 90), scale=1.0):
    x0, y0 = pos

    aura_w = int((280 + math.sin(time_s * 2.2) * 18) * scale)
    aura_h = int((190 + math.sin(time_s * 2.2) * 12) * scale)
    aura = pygame.Surface((aura_w, aura_h), pygame.SRCALPHA)
    pygame.draw.ellipse(aura, (*PURPLE, 30), aura.get_rect())
    screen.blit(aura, (x0 - aura_w // 2, y0 + int(20 * scale)))

    head = pygame.Surface((int(40 * scale), int(50 * scale)), pygame.SRCALPHA)
    pygame.draw.ellipse(head, (*GOLD, 180), head.get_rect())
    screen.blit(head, (x0 - head.get_width() // 2, y0))

    crown_points = []
    crown_w = int(48 * scale)
    crown_h = int(18 * scale)
    crown_x = x0 - crown_w // 2
    crown_y = y0 - int(12 * scale)
    for i in range(5):
        px = crown_x + i * (crown_w // 4)
        crown_points.append((px, crown_y + crown_h))
        crown_points.append((px + crown_w // 8, crown_y))
    pygame.draw.polygon(screen, GOLD, crown_points)

    body = pygame.Surface((int(120 * scale), int(220 * scale)), pygame.SRCALPHA)
    body_points = [
        (body.get_width() // 2, int(28 * scale)),
        (int(10 * scale), body.get_height() - int(10 * scale)),
        (body.get_width() - int(10 * scale), body.get_height() - int(10 * scale)),
    ]
    pygame.draw.polygon(body, (*GOLD, 60), body_points)
    screen.blit(body, (x0 - body.get_width() // 2, y0 + int(38 * scale)))

    orb_r = max(4, int(7 * scale))
    for ox in (-int(56 * scale), int(56 * scale)):
        orb = pygame.Surface((orb_r * 6, orb_r * 6), pygame.SRCALPHA)
        pygame.draw.circle(orb, (*GOLD_LIGHT, 170), (orb_r * 3, orb_r * 3), orb_r)
        pygame.draw.circle(orb, (*GOLD, 70), (orb_r * 3, orb_r * 3), orb_r * 2)
        screen.blit(orb, (x0 + ox - orb.get_width() // 2, y0 + int(130 * scale)))
