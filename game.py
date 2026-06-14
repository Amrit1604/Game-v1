import pygame
import os
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
TILE = 64
PLAYER_SIZE = 96
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ANIME RPG - Red Girl Chronicles")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("arial", 18)
font = pygame.font.SysFont("arial", 24, bold=True)
font_big = pygame.font.SysFont("arial", 48, bold=True)
font_title = pygame.font.SysFont("arial", 64, bold=True)

# ---------------- CONFIG: sprite paths ----------------
# BASE = r"D:\exampleGame\The Red girl tileset\Player"
BASE = r"E:\Projects\Game-v2\The Red girl tileset\Player"
IDLE_PATH = os.path.join(BASE, "Red_Girl_Idle.png")
WALK_PATH = os.path.join(BASE, "Red_Girl_Walk.png")

FRAME = 48
IDLE_FRAMES = 3
WALK_FRAMES = 6

ROW_DOWN, ROW_LEFT, ROW_RIGHT, ROW_UP = 0, 1, 2, 3
# --------------------------------------------------------


def load_frames(sheet_path, row, count, frame_size, scale):
    sheet = pygame.image.load(sheet_path).convert_alpha()
    frames = []
    for i in range(count):
        rect = pygame.Rect(i * frame_size, row * frame_size, frame_size, frame_size)
        img = sheet.subsurface(rect).copy()
        img = pygame.transform.scale(img, (scale, scale))
        frames.append(img)
    return frames


def vertical_gradient(surface, top_color, bottom_color):
    h = surface.get_height()
    w = surface.get_width()
    for y in range(h):
        ratio = y / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))


# ================= PARTICLES =================
class Particle:
    def __init__(self, x, y, color, vel=None, life=30, size=4, gravity=0.0):
        self.x, self.y = x, y
        if vel:
            self.vx, self.vy = vel
        else:
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1, 4)
            self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    def draw(self, surface, offset=(0, 0)):
        if self.life <= 0:
            return
        alpha = max(0, int(255 * (self.life / self.max_life)))
        s = max(1, int(self.size * (self.life / self.max_life)))
        surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (s, s), s)
        surface.blit(surf, (self.x - s - offset[0], self.y - s - offset[1]))

    @property
    def dead(self):
        return self.life <= 0


class FloatingText:
    """Damage numbers / popups."""
    def __init__(self, x, y, text, color, life=45):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.y -= 1
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = max(0, int(255 * (self.life / self.max_life)))
        surf = font_big.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        surface.blit(surf, (self.x - surf.get_width() // 2, self.y))

    @property
    def dead(self):
        return self.life <= 0


# ================= PLAYER =================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.idle = {
            "down":  load_frames(IDLE_PATH, ROW_DOWN,  IDLE_FRAMES, FRAME, PLAYER_SIZE),
            "left":  load_frames(IDLE_PATH, ROW_LEFT,  IDLE_FRAMES, FRAME, PLAYER_SIZE),
            "right": load_frames(IDLE_PATH, ROW_RIGHT, IDLE_FRAMES, FRAME, PLAYER_SIZE),
            "up":    load_frames(IDLE_PATH, ROW_UP,    IDLE_FRAMES, FRAME, PLAYER_SIZE),
        }
        self.walk = {
            "down":  load_frames(WALK_PATH, ROW_DOWN,  WALK_FRAMES, FRAME, PLAYER_SIZE),
            "left":  load_frames(WALK_PATH, ROW_LEFT,  WALK_FRAMES, FRAME, PLAYER_SIZE),
            "right": load_frames(WALK_PATH, ROW_RIGHT, WALK_FRAMES, FRAME, PLAYER_SIZE),
            "up":    load_frames(WALK_PATH, ROW_UP,    WALK_FRAMES, FRAME, PLAYER_SIZE),
        }

        self.direction = "down"
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 6

        self.image = self.idle[self.direction][0]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        self.speed = 4

        self.max_hp = 100
        self.hp = 100
        self.attack = 15
        self.level = 1
        self.xp = 0
        self.xp_to_level = 50

    def update(self, keys, obstacles, particles):
        dx = dy = 0
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
            self.direction = "left"
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.direction = "right"
            moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
            self.direction = "up"
            moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
            self.direction = "down"
            moving = True

        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, obstacles):
            self.rect.x -= dx

        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, obstacles):
            self.rect.y -= dy

        anim_set = self.walk if moving else self.idle
        frames = anim_set[self.direction]

        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)

            # dust trail particles while walking
            if moving:
                particles.append(Particle(
                    self.rect.centerx, self.rect.bottom - 5,
                    (200, 200, 150), vel=(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0)),
                    life=20, size=3
                ))

        if self.frame_index >= len(frames):
            self.frame_index = 0

        self.image = frames[self.frame_index]
        return moving

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_level:
            self.xp -= self.xp_to_level
            self.level += 1
            self.xp_to_level = int(self.xp_to_level * 1.5)
            self.max_hp += 20
            self.hp = self.max_hp
            self.attack += 5
            leveled = True
        return leveled


# ================= WORLD OBJECTS =================
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w=TILE, h=TILE, color=(70, 50, 40)):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        # add a subtle border for definition
        pygame.draw.rect(self.image, tuple(min(255, c + 30) for c in color), self.image.get_rect(), 3)
        self.rect = self.image.get_rect(topleft=(x, y))


class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.base_image = self._build_image(enemy_type)
        self.image = self.base_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dir = random.choice([-1, 1])
        self.range_min = x - 60
        self.range_max = x + 60
        self.speed = 1
        self.bob_timer = random.uniform(0, math.tau)

    def _build_image(self, enemy_type):
        size = TILE
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = enemy_type["color"]
        glow_color = tuple(min(255, c + 60) for c in color)
        # glow aura
        pygame.draw.circle(surf, (*glow_color, 60), (size // 2, size // 2), size // 2)
        # body
        pygame.draw.rect(surf, color, (size * 0.15, size * 0.15, size * 0.7, size * 0.7), border_radius=10)
        # eyes
        eye_color = (255, 255, 255)
        pygame.draw.circle(surf, eye_color, (int(size * 0.35), int(size * 0.4)), 5)
        pygame.draw.circle(surf, eye_color, (int(size * 0.65), int(size * 0.4)), 5)
        pygame.draw.circle(surf, (0, 0, 0), (int(size * 0.35), int(size * 0.4)), 2)
        pygame.draw.circle(surf, (0, 0, 0), (int(size * 0.65), int(size * 0.4)), 2)
        return surf

    def update(self):
        self.rect.x += self.dir * self.speed
        if self.rect.x < self.range_min or self.rect.x > self.range_max:
            self.dir *= -1
        self.bob_timer += 0.08

    def draw(self, surface, offset=(0, 0)):
        bob = math.sin(self.bob_timer) * 4
        surface.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1] + bob))


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y, target_map, target_pos, color=(80, 200, 255)):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.target_map = target_map
        self.target_pos = target_pos
        self.timer = random.uniform(0, math.tau)

    def update(self):
        self.timer += 0.1

    def draw(self, surface, offset=(0, 0)):
        cx = self.rect.centerx - offset[0]
        cy = self.rect.centery - offset[1]
        for i in range(3):
            radius = (TILE // 2 - 4) - i * 6
            phase = self.timer + i * 1.2
            alpha = int(120 + 100 * math.sin(phase))
            alpha = max(40, min(255, alpha))
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (radius, radius), radius, width=3)
            surface.blit(surf, (cx - radius, cy - radius))
        # core
        pygame.draw.circle(surface, (*self.color,), (cx, cy), 6)


# ================= ENEMY TYPES =================
ENEMY_TYPES = {
    "slime":  {"name": "Slime",  "color": (60, 200, 90),  "hp": 30, "attack": 8,  "xp": 15},
    "wolf":   {"name": "Wolf",   "color": (150, 80, 200), "hp": 50, "attack": 12, "xp": 25},
    "bandit": {"name": "Bandit", "color": (220, 60, 60),  "hp": 70, "attack": 18, "xp": 40},
}


# ================= MAP DEFINITIONS =================
def build_village():
    obstacles = pygame.sprite.Group(
        Obstacle(0, 0, WIDTH, 20, (50, 90, 50)),
        Obstacle(0, HEIGHT - 20, WIDTH, 20, (50, 90, 50)),
        Obstacle(150, 200, TILE, TILE, (110, 80, 60)),
        Obstacle(150, 264, TILE, TILE, (110, 80, 60)),
        Obstacle(450, 350, TILE, TILE * 2, (110, 80, 60)),
    )
    enemies = pygame.sprite.Group()
    portals = pygame.sprite.Group(
        Portal(WIDTH - TILE, HEIGHT // 2, "forest", (40, HEIGHT // 2)),
    )
    return {
        "obstacles": obstacles, "enemies": enemies, "portals": portals,
        "bg_top": (100, 180, 230), "bg_bottom": (60, 140, 70),
        "name": "Sunny Village", "ambient": "leaves"
    }


def build_forest():
    obstacles = pygame.sprite.Group(
        Obstacle(0, 0, WIDTH, 20, (20, 60, 30)),
        Obstacle(0, HEIGHT - 20, WIDTH, 20, (20, 60, 30)),
        Obstacle(150, 150, TILE, TILE, (40, 80, 40)),
        Obstacle(150, 214, TILE, TILE, (40, 80, 40)),
        Obstacle(500, 400, TILE * 2, TILE, (40, 80, 40)),
    )
    enemies = pygame.sprite.Group(
        EnemySprite(300, 200, ENEMY_TYPES["slime"]),
        EnemySprite(550, 150, ENEMY_TYPES["slime"]),
        EnemySprite(400, 450, ENEMY_TYPES["wolf"]),
    )
    portals = pygame.sprite.Group(
        Portal(0, HEIGHT // 2, "village", (WIDTH - TILE - 10, HEIGHT // 2)),
        Portal(WIDTH - TILE, HEIGHT - TILE - 20, "cave", (40, 40)),
    )
    return {
        "obstacles": obstacles, "enemies": enemies, "portals": portals,
        "bg_top": (30, 80, 50), "bg_bottom": (10, 30, 20),
        "name": "Whispering Forest", "ambient": "fireflies"
    }


def build_cave():
    obstacles = pygame.sprite.Group(
        Obstacle(0, 0, WIDTH, 20, (40, 35, 50)),
        Obstacle(0, HEIGHT - 20, WIDTH, 20, (40, 35, 50)),
        Obstacle(0, 0, 20, HEIGHT, (40, 35, 50)),
        Obstacle(WIDTH - 20, 0, 20, HEIGHT, (40, 35, 50)),
        Obstacle(350, 250, TILE * 2, TILE, (50, 40, 60)),
    )
    enemies = pygame.sprite.Group(
        EnemySprite(200, 300, ENEMY_TYPES["wolf"]),
        EnemySprite(600, 200, ENEMY_TYPES["bandit"]),
        EnemySprite(600, 450, ENEMY_TYPES["bandit"]),
    )
    portals = pygame.sprite.Group(
        Portal(30, 30, "forest", (WIDTH - TILE - 10, HEIGHT - TILE - 30)),
    )
    return {
        "obstacles": obstacles, "enemies": enemies, "portals": portals,
        "bg_top": (25, 15, 35), "bg_bottom": (5, 5, 15),
        "name": "Crystal Cave", "ambient": "embers"
    }


MAPS = {
    "village": build_village,
    "forest": build_forest,
    "cave": build_cave,
}


# ================= BATTLE SYSTEM =================
class Battle:
    def __init__(self, player, enemy_type):
        self.player = player
        self.enemy_type = enemy_type
        self.enemy_hp = enemy_type["hp"]
        self.enemy_max_hp = enemy_type["hp"]
        self.log = [f"A wild {enemy_type['name']} appears!"]
        self.player_turn = True
        self.over = False
        self.result = None
        self.shake = 0
        self.particles = []
        self.flash = 0  # screen flash effect timer

    def player_attack(self):
        if not self.player_turn or self.over:
            return
        dmg = random.randint(self.player.attack - 3, self.player.attack + 3)
        crit = random.random() < 0.15
        if crit:
            dmg = int(dmg * 1.8)
        self.enemy_hp -= dmg
        msg = f"You hit for {dmg}!" + (" CRITICAL!" if crit else "")
        self.log.append(msg)
        self.shake = 12 if crit else 6
        self.flash = 6
        self._spawn_hit_particles(WIDTH // 2, 140, self.enemy_type["color"])

        if self.enemy_hp <= 0:
            self.enemy_hp = 0
            self.log.append(f"{self.enemy_type['name']} defeated!")
            leveled = self.player.gain_xp(self.enemy_type["xp"])
            self.log.append(f"+{self.enemy_type['xp']} XP")
            if leveled:
                self.log.append(f"LEVEL UP! Now level {self.player.level}!")
            self.over = True
            self.result = "win"
            self._spawn_victory_particles()
            return
        self.player_turn = False

    def enemy_attack(self):
        if self.player_turn or self.over:
            return
        dmg = random.randint(self.enemy_type["attack"] - 2, self.enemy_type["attack"] + 2)
        self.player.hp -= dmg
        self.log.append(f"{self.enemy_type['name']} hits you for {dmg}!")
        self.shake = 8
        self._spawn_hit_particles(120, 400, (255, 80, 80))
        if self.player.hp <= 0:
            self.player.hp = 0
            self.log.append("You were defeated...")
            self.over = True
            self.result = "lose"
            return
        self.player_turn = True

    def flee(self):
        if self.over:
            return
        if random.random() < 0.5:
            self.log.append("You fled!")
            self.over = True
            self.result = "flee"
        else:
            self.log.append("Couldn't escape!")
            self.player_turn = False
            self.enemy_attack()

    def _spawn_hit_particles(self, x, y, color):
        for _ in range(15):
            self.particles.append(Particle(x, y, color, life=25, size=5))

    def _spawn_victory_particles(self):
        for _ in range(40):
            self.particles.append(Particle(
                WIDTH // 2, 140,
                random.choice([(255, 215, 0), (255, 255, 255), (255, 165, 0)]),
                vel=(random.uniform(-3, 3), random.uniform(-5, -1)),
                life=60, size=6, gravity=0.15
            ))

    def update(self):
        if self.shake > 0:
            self.shake -= 1
        if self.flash > 0:
            self.flash -= 1
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.dead]

    def trim_log(self):
        if len(self.log) > 5:
            self.log = self.log[-5:]


def draw_glow_rect(surface, color, rect, glow_size=20, alpha=80):
    glow_surf = pygame.Surface((rect.width + glow_size * 2, rect.height + glow_size * 2), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (*color, alpha), glow_surf.get_rect(), border_radius=20)
    surface.blit(glow_surf, (rect.x - glow_size, rect.y - glow_size))


def draw_battle(screen, battle, time_tick):
    shake_x = random.randint(-battle.shake, battle.shake) if battle.shake > 0 else 0
    shake_y = random.randint(-battle.shake, battle.shake) if battle.shake > 0 else 0

    bg = pygame.Surface((WIDTH, HEIGHT))
    vertical_gradient(bg, (60, 20, 80), (15, 5, 25))
    screen.blit(bg, (shake_x, shake_y))

    # pulsing arena circle behind enemy
    pulse = 60 + int(10 * math.sin(time_tick * 0.1))
    pygame.draw.circle(screen, (90, 30, 110), (WIDTH // 2 + shake_x, 150 + shake_y), pulse + 40)

    # Enemy
    enemy_rect = pygame.Rect(WIDTH // 2 - 60 + shake_x, 80 + shake_y, 120, 120)
    draw_glow_rect(screen, battle.enemy_type["color"], enemy_rect, glow_size=15, alpha=70)
    bob = math.sin(time_tick * 0.1) * 5
    body_rect = enemy_rect.move(0, bob)
    pygame.draw.rect(screen, battle.enemy_type["color"], body_rect, border_radius=16)
    # eyes
    pygame.draw.circle(screen, (255, 255, 255), (body_rect.centerx - 20, body_rect.centery - 10), 10)
    pygame.draw.circle(screen, (255, 255, 255), (body_rect.centerx + 20, body_rect.centery - 10), 10)
    pygame.draw.circle(screen, (0, 0, 0), (body_rect.centerx - 20, body_rect.centery - 10), 4)
    pygame.draw.circle(screen, (0, 0, 0), (body_rect.centerx + 20, body_rect.centery - 10), 4)

    name_text = font.render(battle.enemy_type["name"].upper(), True, (255, 255, 255))
    screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2 + shake_x, 50 + shake_y))

    # Enemy HP bar with glow
    bar_w = 220
    bar_rect = pygame.Rect(WIDTH // 2 - bar_w // 2, 220, bar_w, 18)
    pygame.draw.rect(screen, (40, 20, 50), bar_rect, border_radius=9)
    hp_ratio = max(0, battle.enemy_hp / battle.enemy_max_hp)
    fill_color = (220, 60, 60) if hp_ratio < 0.3 else (240, 180, 60) if hp_ratio < 0.6 else (80, 220, 100)
    fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(bar_w * hp_ratio), 18)
    pygame.draw.rect(screen, fill_color, fill_rect, border_radius=9)
    pygame.draw.rect(screen, (255, 255, 255), bar_rect, width=2, border_radius=9)
    hp_text = font_small.render(f"{battle.enemy_hp}/{battle.enemy_max_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (WIDTH // 2 - hp_text.get_width() // 2, 242))

    # Particles
    for p in battle.particles:
        p.draw(screen)

    # Player panel
    p = battle.player
    panel = pygame.Rect(20, 310, 320, 90)
    pygame.draw.rect(screen, (30, 20, 45), panel, border_radius=12)
    pygame.draw.rect(screen, (130, 90, 200), panel, width=2, border_radius=12)
    py_text = font.render(f"YOU - Lv.{p.level}", True, (255, 255, 255))
    screen.blit(py_text, (35, 320))
    bar_w2 = 280
    bar2 = pygame.Rect(35, 355, bar_w2, 16)
    pygame.draw.rect(screen, (40, 20, 30), bar2, border_radius=8)
    p_ratio = max(0, p.hp / p.max_hp)
    p_fill_color = (220, 60, 60) if p_ratio < 0.3 else (240, 180, 60) if p_ratio < 0.6 else (80, 220, 100)
    pygame.draw.rect(screen, p_fill_color, (bar2.x, bar2.y, int(bar_w2 * p_ratio), 16), border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), bar2, width=2, border_radius=8)
    hp_txt2 = font_small.render(f"HP {p.hp}/{p.max_hp}", True, (255, 255, 255))
    screen.blit(hp_txt2, (35, 374))

    # Log box
    log_rect = pygame.Rect(20, 410, WIDTH - 40, 110)
    pygame.draw.rect(screen, (20, 12, 30), log_rect, border_radius=12)
    pygame.draw.rect(screen, (90, 60, 130), log_rect, width=2, border_radius=12)
    for i, line in enumerate(battle.log[-4:]):
        t = font_small.render(line, True, (235, 230, 255))
        screen.blit(t, (35, 422 + i * 22))

    # Controls hint
    if not battle.over:
        hint = "[A] Attack    [F] Flee"
        hint_color = (255, 230, 100)
    else:
        if battle.result == "win":
            hint = "VICTORY! Press ENTER to continue"
            hint_color = (100, 255, 130)
        elif battle.result == "lose":
            hint = "DEFEATED... Press ENTER"
            hint_color = (255, 90, 90)
        else:
            hint = "Press ENTER to continue"
            hint_color = (200, 200, 255)
    hint_text = font.render(hint, True, hint_color)
    screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT - 35))

    # Flash overlay
    if battle.flash > 0:
        flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 255, battle.flash * 15))
        screen.blit(flash_surf, (0, 0))


# ================= AMBIENT EFFECTS =================
def spawn_ambient_particle(ambient_type, particles):
    if random.random() > 0.05:
        return
    if ambient_type == "leaves":
        particles.append(Particle(
            random.randint(0, WIDTH), -10,
            random.choice([(140, 200, 90), (180, 220, 100)]),
            vel=(random.uniform(-0.5, 0.5), random.uniform(0.5, 1.5)),
            life=300, size=4
        ))
    elif ambient_type == "fireflies":
        particles.append(Particle(
            random.randint(0, WIDTH), random.randint(0, HEIGHT),
            (255, 255, 150),
            vel=(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3)),
            life=120, size=3
        ))
    elif ambient_type == "embers":
        particles.append(Particle(
            random.randint(0, WIDTH), HEIGHT + 5,
            random.choice([(255, 120, 40), (255, 180, 60)]),
            vel=(random.uniform(-0.3, 0.3), random.uniform(-1.5, -0.5)),
            life=100, size=4
        ))


# ================= GAME STATE =================
class Game:
    def __init__(self):
        self.player = Player()
        self.current_map_name = "village"
        self.current_map = MAPS[self.current_map_name]()
        self.state = "title"  # title -> explore -> battle
        self.battle = None
        self.battle_enemy_sprite = None
        self.transition_cooldown = 0
        self.particles = []
        self.floating_texts = []
        self.screen_shake = 0
        self.time_tick = 0
        self.fade_alpha = 0
        self.fading_to = None

    def load_map(self, name, player_pos):
        self.current_map_name = name
        self.current_map = MAPS[name]()
        self.player.rect.center = player_pos
        self.transition_cooldown = 30

    def start_battle(self, enemy_sprite):
        self.battle_enemy_sprite = enemy_sprite
        self.battle = Battle(self.player, enemy_sprite.enemy_type)
        self.state = "battle"

    def end_battle(self):
        result = self.battle.result
        if result == "win" and self.battle_enemy_sprite:
            self.battle_enemy_sprite.kill()
        if result == "lose":
            self.player.hp = self.player.max_hp // 2
            self.load_map("village", (WIDTH // 2, HEIGHT // 2))
        self.battle = None
        self.battle_enemy_sprite = None
        self.state = "explore"
        self.transition_cooldown = 20

    def update_explore(self, keys):
        if self.transition_cooldown > 0:
            self.transition_cooldown -= 1

        moving = self.player.update(keys, self.current_map["obstacles"], self.particles)
        self.current_map["enemies"].update()
        self.current_map["portals"].update()

        spawn_ambient_particle(self.current_map.get("ambient", ""), self.particles)
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.dead]

        if self.transition_cooldown == 0:
            hit = pygame.sprite.spritecollideany(self.player, self.current_map["enemies"])
            if hit:
                self.start_battle(hit)
                return

            portal = pygame.sprite.spritecollideany(self.player, self.current_map["portals"])
            if portal:
                self.load_map(portal.target_map, portal.target_pos)

    def draw_explore(self, screen):
        m = self.current_map

        shake_x = random.randint(-2, 2) if self.screen_shake > 0 else 0
        shake_y = random.randint(-2, 2) if self.screen_shake > 0 else 0
        if self.screen_shake > 0:
            self.screen_shake -= 1

        bg = pygame.Surface((WIDTH, HEIGHT))
        vertical_gradient(bg, m["bg_top"], m["bg_bottom"])
        screen.blit(bg, (shake_x, shake_y))

        # ground texture: subtle grid
        for gx in range(0, WIDTH, TILE):
            pygame.draw.line(screen, (255, 255, 255, 10), (gx + shake_x, 0), (gx + shake_x, HEIGHT), 1)

        m["obstacles"].draw(screen)
        for portal in m["portals"]:
            portal.draw(screen, offset=(-shake_x, -shake_y))
        for enemy in m["enemies"]:
            enemy.draw(screen, offset=(-shake_x, -shake_y))

        # player glow
        glow_rect = self.player.rect.inflate(20, 20)
        draw_glow_rect(screen, (255, 220, 150), glow_rect, glow_size=10, alpha=40)
        screen.blit(self.player.image, (self.player.rect.x + shake_x, self.player.rect.y + shake_y))

        for p in self.particles:
            p.draw(screen)

        # HUD panel
        hud_rect = pygame.Rect(10, 10, 340, 70)
        hud_surf = pygame.Surface((hud_rect.width, hud_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(hud_surf, (20, 15, 35, 180), hud_surf.get_rect(), border_radius=12)
        screen.blit(hud_surf, hud_rect.topleft)

        p = self.player
        map_text = font.render(m["name"], True, (255, 255, 255))
        screen.blit(map_text, (22, 16))

        lvl_text = font_small.render(f"Lv.{p.level}   XP {p.xp}/{p.xp_to_level}", True, (220, 220, 255))
        screen.blit(lvl_text, (22, 44))

        # HP bar
        bar_rect = pygame.Rect(150, 46, 180, 14)
        pygame.draw.rect(screen, (40, 20, 30), bar_rect, border_radius=7)
        ratio = max(0, p.hp / p.max_hp)
        color = (220, 60, 60) if ratio < 0.3 else (240, 180, 60) if ratio < 0.6 else (80, 220, 100)
        pygame.draw.rect(screen, color, (bar_rect.x, bar_rect.y, int(bar_rect.width * ratio), 14), border_radius=7)
        pygame.draw.rect(screen, (255, 255, 255), bar_rect, width=1, border_radius=7)
        hp_txt = font_small.render(f"{p.hp}/{p.max_hp}", True, (255, 255, 255))
        screen.blit(hp_txt, (bar_rect.x + bar_rect.width // 2 - hp_txt.get_width() // 2, bar_rect.y - 1))

        # mini hint
        hint = font_small.render("WASD/Arrows to move - touch glowing portals to travel", True, (255, 255, 255, 180))
        hint_surf = pygame.Surface((hint.get_width() + 16, hint.get_height() + 8), pygame.SRCALPHA)
        pygame.draw.rect(hint_surf, (0, 0, 0, 120), hint_surf.get_rect(), border_radius=8)
        hint_surf.blit(hint, (8, 4))
        screen.blit(hint_surf, (10, HEIGHT - 36))


def draw_title_screen(screen, time_tick):
    bg = pygame.Surface((WIDTH, HEIGHT))
    top = (40 + int(20 * math.sin(time_tick * 0.01)), 20, 60)
    bottom = (10, 5, 25)
    vertical_gradient(bg, top, bottom)
    screen.blit(bg, (0, 0))

    # floating glowing orbs in background
    for i in range(6):
        x = (WIDTH // 6) * i + 60
        y = HEIGHT // 2 + int(40 * math.sin(time_tick * 0.03 + i))
        color = [(255, 100, 150), (100, 200, 255), (255, 220, 100)][i % 3]
        surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, 50), (30, 30), 30)
        screen.blit(surf, (x - 30, y - 30))

    title1 = font_title.render("RED GIRL", True, (255, 220, 120))
    title2 = font_title.render("CHRONICLES", True, (255, 255, 255))
    glow1 = font_title.render("RED GIRL", True, (255, 150, 50))

    pulse = 1 + 0.05 * math.sin(time_tick * 0.08)
    t1_scaled = pygame.transform.smoothscale(title1, (int(title1.get_width() * pulse), int(title1.get_height() * pulse)))
    glow_scaled = pygame.transform.smoothscale(glow1, (int(glow1.get_width() * pulse * 1.05), int(glow1.get_height() * pulse * 1.05)))
    glow_scaled.set_alpha(100)

    screen.blit(glow_scaled, (WIDTH // 2 - glow_scaled.get_width() // 2, 138))
    screen.blit(t1_scaled, (WIDTH // 2 - t1_scaled.get_width() // 2, 140))
    screen.blit(title2, (WIDTH // 2 - title2.get_width() // 2, 210))

    blink = abs(math.sin(time_tick * 0.05))
    start_text = font.render("Press ENTER to begin your journey", True, (255, 255, 255))
    start_text.set_alpha(int(150 + 105 * blink))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 420))

    sub = font_small.render("WASD/Arrows: Move    A: Attack    F: Flee    ENTER: Confirm", True, (180, 180, 220))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 480))


def main():
    game = Game()
    running = True

    while running:
        game.time_tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game.state == "title":
                    if event.key == pygame.K_RETURN:
                        game.state = "explore"

                elif game.state == "battle":
                    print("BATTLE KEY:", event.key, "state:", game.state)
                    b = game.battle
                    if not b.over:
                        if event.key == pygame.K_a:
                            b.player_attack()
                            b.trim_log()
                        elif event.key == pygame.K_f:
                            b.flee()
                            b.trim_log()
                        if not b.over and not b.player_turn:
                            b.enemy_attack()
                            b.trim_log()
                    else:
                        if event.key == pygame.K_RETURN:
                            game.end_battle()

        if game.state == "title":
            draw_title_screen(screen, game.time_tick)
        elif game.state == "explore":
            keys = pygame.key.get_pressed()
            game.update_explore(keys)
            game.draw_explore(screen)
        elif game.state == "battle":
            game.battle.update()
            draw_battle(screen, game.battle, game.time_tick)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()