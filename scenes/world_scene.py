import math
import random
import pygame
from scenes import BaseScene


def draw_vector_rune(surface, color, size, x, y, rune_type):
    """
    Draws a custom glowing vector-art rune on the given surface.
    Ensures a consistent ancient look regardless of system fonts.
    """
    # Grid markers
    mx = x + size // 2
    rx = x + size
    my = y + size // 2
    by = y + size
    
    if rune_type == 0:  # Fehu (F)
        pygame.draw.line(surface, color, (mx, y), (mx, by), 2)
        pygame.draw.line(surface, color, (mx, y + 2), (rx - 2, y - 2), 2)
        pygame.draw.line(surface, color, (mx, my), (rx - 2, my - 2), 2)
    elif rune_type == 1:  # Uruz (U)
        pygame.draw.line(surface, color, (x + 2, y), (x + 2, by), 2)
        pygame.draw.line(surface, color, (rx - 2, y + 5), (rx - 2, by), 2)
        pygame.draw.line(surface, color, (x + 2, y), (rx - 2, y + 5), 2)
    elif rune_type == 2:  # Thurisaz (Th)
        pygame.draw.line(surface, color, (mx, y), (mx, by), 2)
        pygame.draw.polygon(surface, color, [(mx, y + 4), (rx, my), (mx, by - 4)], 2)
    elif rune_type == 3:  # Ansuz (A)
        pygame.draw.line(surface, color, (mx, y), (mx, by), 2)
        pygame.draw.line(surface, color, (mx, y), (rx - 2, y + 5), 2)
        pygame.draw.line(surface, color, (mx, my), (rx - 2, my + 5), 2)
    elif rune_type == 4:  # Raido (R)
        pygame.draw.line(surface, color, (mx, y), (mx, by), 2)
        pygame.draw.polygon(surface, color, [(mx, y), (rx - 2, y + 4), (rx - 2, my), (mx, my)], 2)
        pygame.draw.line(surface, color, (mx, my), (rx - 2, by), 2)
    elif rune_type == 5:  # Kenaz (K)
        pygame.draw.line(surface, color, (x + 2, y), (rx - 2, my), 2)
        pygame.draw.line(surface, color, (rx - 2, my), (x + 2, by), 2)
    elif rune_type == 6:  # Gebo (G)
        pygame.draw.line(surface, color, (x + 2, y + 2), (rx - 2, by - 2), 2)
        pygame.draw.line(surface, color, (rx - 2, y + 2), (x + 2, by - 2), 2)
    elif rune_type == 7:  # Wunjo (W)
        pygame.draw.line(surface, color, (mx, y), (mx, by), 2)
        pygame.draw.polygon(surface, color, [(mx, y), (rx - 2, y + 4), (rx - 2, my), (mx, my)], 2)
    elif rune_type == 8:  # Hagalaz (H)
        pygame.draw.line(surface, color, (x + 2, y), (x + 2, by), 2)
        pygame.draw.line(surface, color, (rx - 2, y), (rx - 2, by), 2)
        pygame.draw.line(surface, color, (x + 2, my), (rx - 2, my), 2)
    elif rune_type == 9:  # Isa (I)
        pygame.draw.line(surface, color, (mx, y), (mx, by), 2)
    elif rune_type == 10:  # Jera (J)
        pygame.draw.line(surface, color, (x + 2, y), (mx, y), 2)
        pygame.draw.line(surface, color, (mx, y), (mx, my), 2)
        pygame.draw.line(surface, color, (rx - 2, by), (mx, by), 2)
        pygame.draw.line(surface, color, (mx, by), (mx, my), 2)
    elif rune_type == 11:  # Algiz (Z)
        pygame.draw.line(surface, color, (mx, y), (mx, by), 2)
        pygame.draw.line(surface, color, (x + 2, y), (mx, my), 2)
        pygame.draw.line(surface, color, (rx - 2, y), (mx, my), 2)
    else:  # Sowilo (S)
        pygame.draw.line(surface, color, (rx - 2, y), (x + 2, my), 2)
        pygame.draw.line(surface, color, (x + 2, my), (rx - 2, my), 2)
        pygame.draw.line(surface, color, (rx - 2, my), (x + 2, by), 2)


class ScreenShake:
    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.elapsed = 0.0

    def start(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt):
        if self.elapsed < self.duration:
            self.elapsed += dt
            # Linear decay
            ratio = self.elapsed / self.duration
            curr_intensity = self.intensity * (1.0 - ratio)
            dx = random.uniform(-curr_intensity, curr_intensity)
            dy = random.uniform(-curr_intensity, curr_intensity)
            return int(dx), int(dy)
        return 0, 0


class ReincarnationParticle:
    def __init__(self, x, y, p_type):
        self.x = x
        self.y = y
        self.type = p_type  # 'dust', 'spark', 'fragment'
        
        if p_type == 'dust':
            self.color = (random.randint(220, 255), random.randint(180, 220), random.randint(80, 120))
            self.radius = random.uniform(1.0, 2.5)
            self.dx = random.uniform(-10.0, 10.0)
            self.dy = random.uniform(-35.0, -15.0)
            self.lifetime = random.uniform(1.8, 3.2)
        elif p_type == 'spark':
            self.color = (255, random.randint(235, 255), random.randint(190, 230))
            self.radius = random.uniform(0.8, 1.8)
            self.dx = random.uniform(-40.0, 40.0)
            self.dy = random.uniform(-75.0, -40.0)
            self.lifetime = random.uniform(0.8, 1.5)
        else:  # 'fragment'
            self.color = (random.randint(230, 255), random.randint(200, 230), random.randint(120, 160))
            self.radius = random.uniform(2.5, 4.2)
            self.dx = random.uniform(-20.0, 20.0)
            self.dy = random.uniform(-28.0, -12.0)
            self.lifetime = random.uniform(1.5, 2.8)
            self.sway_speed = random.uniform(2.0, 4.8)
            self.sway_amount = random.uniform(15.0, 30.0)
            self.sway_offset = random.uniform(0, 2.0 * math.pi)

        self.max_lifetime = self.lifetime
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        if self.type == 'fragment':
            sway = math.sin(self.age * self.sway_speed + self.sway_offset) * self.sway_amount * dt
            self.x += (self.dx * dt) + sway
        else:
            self.x += self.dx * dt
        self.y += self.dy * dt
        self.dx *= 0.98

    def is_dead(self):
        return self.age >= self.max_lifetime

    def get_alpha(self):
        ratio = self.age / self.max_lifetime
        if ratio > 0.7:
            return int(255 * (1.0 - ratio) / 0.3)
        return 255

    def draw(self, surface):
        alpha = self.get_alpha()
        if alpha <= 0:
            return
            
        color_with_alpha = (*self.color, alpha)
        
        if self.type == 'fragment':
            size = int(self.radius)
            poly_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.polygon(poly_surf, color_with_alpha, [
                (size, 0),
                (size * 2, size),
                (size, size * 2),
                (0, size)
            ])
            surface.blit(poly_surf, (int(self.x - size), int(self.y - size)))
        else:
            r = int(self.radius)
            rad_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(rad_surf, color_with_alpha, (r, r), r)
            surface.blit(rad_surf, (int(self.x - r), int(self.y - r)))


class ReincarnationParticleSystem:
    def __init__(self):
        self.particles = []
        self.target_count = 10

    def update(self, dt, soul_pos, magic_circle_pos, phase):
        for p in self.particles[:]:
            p.update(dt)
            if p.is_dead():
                self.particles.remove(p)
                
        if phase == 'A':
            self.target_count = 12
        elif phase == 'B':
            # Interpolate target count from 12 to 100
            self.target_count = 100
        elif phase == 'C':
            self.target_count = 200
        elif phase == 'D':
            self.target_count = 350
        else:
            self.target_count = 0  # Fade out during E and F
            
        if len(self.particles) < self.target_count:
            needed = self.target_count - len(self.particles)
            for _ in range(min(6, needed)):
                p_type = random.choice(['dust', 'dust', 'spark', 'fragment'])
                roll = random.random()
                
                if roll < 0.65 and magic_circle_pos:
                    # Spawn along circular area on the perspective ground plane
                    angle = random.uniform(0, 2.0 * math.pi)
                    dist = random.uniform(0, 180)
                    px = magic_circle_pos[0] + dist * math.cos(angle)
                    py = magic_circle_pos[1] + dist * 0.35 * math.sin(angle)
                    py -= random.uniform(0, 15)
                    self.particles.append(ReincarnationParticle(px, py, p_type))
                elif roll < 0.85 and soul_pos:
                    # Trailing soul particles
                    px = soul_pos[0] + random.uniform(-12, 12)
                    py = soul_pos[1] + random.uniform(-12, 12)
                    self.particles.append(ReincarnationParticle(px, py, 'spark'))
                else:
                    # Ambient drift
                    px = random.uniform(80, 1200)
                    py = random.uniform(380, 720)
                    self.particles.append(ReincarnationParticle(px, py, 'dust'))

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


class MagicCircle:
    def __init__(self, size=500):
        self.size = size
        self.circle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        self.runes_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        self._render_circle()
        self._render_runes()
        
    def _render_circle(self):
        center = self.size // 2
        # Draw outer concentric rings
        pygame.draw.circle(self.circle_surf, (201, 168, 76, 255), (center, center), center - 30, 2)
        pygame.draw.circle(self.circle_surf, (201, 168, 76, 255), (center, center), center - 60, 1)
        
        # Hexagram geometry lines
        points = []
        for i in range(6):
            a = math.radians(i * 60)
            x = center + (center - 60) * math.cos(a)
            y = center + (center - 60) * math.sin(a)
            points.append((x, y))
            
        for i in range(6):
            pygame.draw.line(self.circle_surf, (180, 140, 60, 150), points[i], points[(i + 2) % 6], 2)
            pygame.draw.line(self.circle_surf, (180, 140, 60, 150), points[i], points[(i + 4) % 6], 2)
            
        # Center inner ring
        pygame.draw.circle(self.circle_surf, (240, 208, 120, 200), (center, center), 80, 2)
        
    def _render_runes(self):
        center = self.size // 2
        rune_count = 12
        for idx in range(rune_count):
            angle = idx * (360.0 / rune_count)
            rad = math.radians(angle)
            dist = self.size // 2 - 45
            rx = center + dist * math.cos(rad) - 10
            ry = center + dist * math.sin(rad) - 10
            draw_vector_rune(self.runes_surf, (240, 208, 120, 240), 20, rx, ry, idx)

    def draw(self, screen, x, y, scale, opacity, angle1, angle2):
        if scale <= 0 or opacity <= 0:
            return
            
        # 1. Main summoning circle (Perspective Squash)
        rot_circle = pygame.transform.rotate(self.circle_surf, angle1)
        rot_circle.set_alpha(opacity)
        w = int(rot_circle.get_width() * scale)
        h = int(rot_circle.get_height() * scale * 0.35)
        if w > 0 and h > 0:
            squashed = pygame.transform.smoothscale(rot_circle, (w, h))
            screen.blit(squashed, (x - w // 2, y - h // 2))
            
        # 2. Runes (rotating independently)
        rot_runes = pygame.transform.rotate(self.runes_surf, angle2)
        rot_runes.set_alpha(opacity)
        w2 = int(rot_runes.get_width() * scale)
        h2 = int(rot_runes.get_height() * scale * 0.35)
        if w2 > 0 and h2 > 0:
            squashed2 = pygame.transform.smoothscale(rot_runes, (w2, h2))
            screen.blit(squashed2, (x - w2 // 2, y - h2 // 2))


class FloatingSoul:
    def __init__(self, radius=20):
        self.radius = radius
        self.size = 200
        self.surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self._render_soul()
        
    def _render_soul(self):
        center = self.size // 2
        # Soft outer exponential glow
        for r in range(self.size // 2, self.radius, -2):
            ratio = (r - self.radius) / (self.size // 2 - self.radius)
            alpha = int(45 * (1.0 - ratio) ** 2.2)
            if alpha > 0:
                pygame.draw.circle(self.surf, (255, 225, 140, alpha), (center, center), r)
                
        # Closer halo
        pygame.draw.circle(self.surf, (255, 245, 190, 120), (center, center), self.radius + 6)
        # White core
        pygame.draw.circle(self.surf, (255, 255, 255, 240), (center, center), self.radius)

    def draw(self, screen, x, y, time_s, glow_multiplier=1.0):
        float_y = 10.0 * math.sin(time_s * 1.8)
        pulse = 1.0 + 0.05 * math.sin(time_s * 2.5)
        
        scaled_size = int(self.size * pulse)
        if scaled_size > 0:
            scaled_surf = pygame.transform.scale(self.surf, (scaled_size, scaled_size))
            if glow_multiplier != 1.0:
                alpha_surf = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
                alpha_surf.blit(scaled_surf, (0, 0))
                # Clamp alpha
                alpha_val = max(0, min(255, int(255 * min(1.0, glow_multiplier / 3.0))))
                alpha_surf.set_alpha(alpha_val)
                screen.blit(alpha_surf, (int(x - scaled_size // 2), int(y + float_y) - scaled_size // 2))
            else:
                screen.blit(scaled_surf, (int(x - scaled_size // 2), int(y + float_y) - scaled_size // 2))


class LightRays:
    def __init__(self, num_rays=12):
        self.num_rays = num_rays
        
    def draw(self, screen, center, time_s, intensity):
        if intensity <= 0:
            return
            
        cx, cy = center
        max_len = 800.0 * intensity
        ray_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        for i in range(self.num_rays):
            dir_mult = 1 if i % 2 == 0 else -1
            angle = (i * (360.0 / self.num_rays)) + (time_s * 12.0 * dir_mult)
            
            width_angle = (1.8 + 1.2 * math.sin(time_s * 3.5 + i)) * intensity
            
            rad_l = math.radians(angle - width_angle)
            rad_r = math.radians(angle + width_angle)
            
            lx = cx + max_len * math.cos(rad_l)
            ly = cy + max_len * math.sin(rad_l)
            rx = cx + max_len * math.cos(rad_r)
            ry = cy + max_len * math.sin(rad_r)
            
            alpha = int(45 * intensity * (0.6 + 0.4 * math.sin(time_s * 2.2 + i)))
            color = (255, 230, 160, alpha)
            
            pygame.draw.polygon(ray_surf, color, [(cx, cy), (int(lx), int(ly)), (int(rx), int(ry))])
            
        screen.blit(ray_surf, (0, 0))


class EnergyWave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.max_radius = 650.0
        self.speed = 320.0
        self.opacity = 255.0
        
    def update(self, dt):
        self.radius += self.speed * dt
        ratio = min(1.0, self.radius / self.max_radius)
        self.opacity = 255.0 * (1.0 - ratio) ** 1.6
        
    def is_alive(self):
        return self.radius < self.max_radius and self.opacity > 0
        
    def draw(self, screen):
        if self.opacity <= 0:
            return
        w = int(self.radius * 2)
        h = int(self.radius * 2 * 0.35)
        if w > 0 and h > 0:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            color = (240, 208, 120, int(self.opacity))
            pygame.draw.ellipse(surf, color, (0, 0, w, h), 3)
            if w > 12 and h > 4:
                pygame.draw.ellipse(surf, (255, 255, 255, int(self.opacity * 0.5)), (3, 1, w - 6, h - 2), 1)
            screen.blit(surf, (int(self.x - w // 2), int(self.y - h // 2)))


class WhiteFlash:
    def __init__(self):
        self.alpha = 0.0
        
    def update(self, dt, target_alpha, speed):
        if self.alpha < target_alpha:
            self.alpha = min(target_alpha, self.alpha + speed * dt)
        elif self.alpha > target_alpha:
            self.alpha = max(target_alpha, self.alpha - speed * dt)
            
    def draw(self, screen):
        if self.alpha > 0:
            surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            surf.fill((255, 255, 255, int(self.alpha)))
            screen.blit(surf, (0, 0))


class DivineFog:
    def __init__(self):
        self.clouds = []
        colors = [(16, 10, 32), (8, 14, 38), (24, 10, 42), (28, 20, 10)]
        for _ in range(6):
            w = random.randint(350, 550)
            h = random.randint(300, 500)
            color = random.choice(colors)
            
            cloud_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            cx, cy = w // 2, h // 2
            max_r = min(w, h) // 2
            for r in range(max_r, 0, -6):
                ratio = r / max_r
                alpha = int(20 * (1.0 - ratio) ** 2)
                if alpha > 0:
                    pygame.draw.circle(cloud_surf, (*color, alpha), (cx, cy), r)
                    
            self.clouds.append({
                "surf": cloud_surf,
                "x": random.uniform(-100, 1100),
                "y": random.uniform(-100, 600),
                "dx": random.uniform(-6, 6),
                "dy": random.uniform(-3, 3),
            })
            
    def update(self, dt):
        for c in self.clouds:
            c["x"] += c["dx"] * dt
            c["y"] += c["dy"] * dt
            
            if c["x"] < -600:
                c["x"] = 1280
            elif c["x"] > 1280:
                c["x"] = -600
                
            if c["y"] < -600:
                c["y"] = 720
            elif c["y"] > 720:
                c["y"] = -600
                
    def draw(self, screen):
        for c in self.clouds:
            screen.blit(c["surf"], (int(c["x"]), int(c["y"])))


class ReincarnationScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.elapsed = 0.0
        self.phase = 'A'
        
        self.ui_font = fonts["ui"]
        
        # Initialize modules
        self.screen_shake = ScreenShake()
        self.custom_particles = ReincarnationParticleSystem()
        self.magic_circle = MagicCircle(550)
        self.soul = FloatingSoul(22)
        self.light_rays = LightRays(12)
        self.white_flash = WhiteFlash()
        self.fog = DivineFog()
        
        self.energy_waves = []
        self.wave_spawn_timer = 0.0
        self.camera_zoom = 1.0
        
        self.soul_x = 640.0
        self.soul_y = 360.0
        self.soul_target_y = 360.0
        
        self.shake_offset = (0, 0)
        self.music_climax_triggered = False
        self.music_quiet_triggered = False
        
        self.circle_scale = 0.0
        self.circle_opacity = 0.0
        self.circle_angle1 = 0.0
        self.circle_angle2 = 0.0
        
        self.ray_intensity = 0.0
        self.soul_glow = 1.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_scene = "world_intro"

    def update(self, dt):
        self.elapsed += dt
        self.fog.update(dt)
        
        # Timeline evaluation
        if self.elapsed < 2.0:
            self.phase = 'A'
        elif self.elapsed < 5.0:
            self.phase = 'B'
        elif self.elapsed < 8.0:
            self.phase = 'C'
        elif self.elapsed < 11.0:
            self.phase = 'D'
        elif self.elapsed < 13.0:
            self.phase = 'E'
        elif self.elapsed < 15.0:
            self.phase = 'F'
        else:
            self.next_scene = "world_intro"
            return
            
        # Update particles
        soul_pos = (self.soul_x, self.soul_y)
        mc_pos = (640, 550) if self.elapsed >= 2.0 else None
        self.custom_particles.update(dt, soul_pos, mc_pos, self.phase)
        
        # Update waves
        for w in self.energy_waves[:]:
            w.update(dt)
            if not w.is_alive():
                self.energy_waves.remove(w)
                
        # Screen shake offset logic
        shake_dx, shake_dy = self.screen_shake.update(dt)
        self.shake_offset = (shake_dx, shake_dy)
        
        # Phase Timeline drivers
        if self.phase == 'A':
            self.soul_target_y = 360.0
            self.circle_scale = 0.0
            self.circle_opacity = 0.0
            self.camera_zoom = 1.0
            self.ray_intensity = 0.0
            self.soul_glow = 1.0
            
            if not self.music_quiet_triggered:
                try:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.fadeout(1500)
                except Exception:
                    pass
                self.music_quiet_triggered = True
                
        elif self.phase == 'B':
            t = (self.elapsed - 2.0) / 3.0
            smooth_t = t * t * (3.0 - 2.0 * t)
            
            self.circle_scale = smooth_t
            self.circle_opacity = 255.0 * smooth_t
            
            self.circle_angle1 += 14.0 * dt
            self.circle_angle2 -= 10.0 * dt
            
            self.soul_target_y = 360.0
            self.camera_zoom = 1.0
            self.ray_intensity = 0.0
            self.soul_glow = 1.0 + 0.4 * smooth_t
            
        elif self.phase == 'C':
            t = (self.elapsed - 5.0) / 3.0
            smooth_t = t * t * (3.0 - 2.0 * t)
            
            # Soul ascends slow upward
            self.soul_target_y = 360.0 - 100.0 * smooth_t
            self.soul_glow = 1.4 + 1.2 * smooth_t
            
            self.circle_angle1 += 18.0 * dt
            self.circle_angle2 -= 12.0 * dt
            self.circle_scale = 1.0 + 0.04 * math.sin(self.elapsed * 4.0)
            self.circle_opacity = 255.0
            
            self.ray_intensity = 0.5 * smooth_t
            self.camera_zoom = 1.0 + 0.03 * smooth_t
            
            # Continuous minor screen shake
            if self.screen_shake.duration <= 0 or self.screen_shake.elapsed >= self.screen_shake.duration:
                self.screen_shake.start(1.5, 0.4)
                
        elif self.phase == 'D':
            t = (self.elapsed - 8.0) / 3.0
            smooth_t = t * t * (3.0 - 2.0 * t)
            
            self.soul_target_y = 260.0
            self.soul_glow = 2.6 + 3.0 * smooth_t
            
            # Circles spin faster
            self.circle_angle1 += (18.0 + 35.0 * smooth_t) * dt
            self.circle_angle2 -= (12.0 + 30.0 * smooth_t) * dt
            self.circle_scale = 1.0 + 0.12 * math.sin(self.elapsed * 8.0)
            
            self.ray_intensity = 0.5 + 0.5 * smooth_t
            self.camera_zoom = 1.03 + 0.07 * smooth_t
            
            # Medium shake
            if self.screen_shake.duration <= 0 or self.screen_shake.elapsed >= self.screen_shake.duration:
                self.screen_shake.start(4.5, 0.35)
                
            # Spawn energy waves
            self.wave_spawn_timer += dt
            if self.wave_spawn_timer >= 0.5 - 0.25 * smooth_t:
                self.energy_waves.append(EnergyWave(640, 550))
                self.wave_spawn_timer = 0.0
                
            if not self.music_climax_triggered:
                self.music_climax_triggered = True
                
        elif self.phase == 'E':
            # White pulse expands
            flash_target = min(1.0, (self.elapsed - 11.0) / 1.0)
            self.white_flash.update(dt, flash_target * 255.0, 255.0)
            
            # Intense screen shake
            if self.elapsed < 11.8:
                if self.screen_shake.duration <= 0 or self.screen_shake.elapsed >= self.screen_shake.duration:
                    self.screen_shake.start(9.0, 0.3)
            self.camera_zoom = 1.10
            
        elif self.phase == 'F':
            self.white_flash.alpha = 255.0
            self.camera_zoom = 1.0
            
        self.soul_y += (self.soul_target_y - self.soul_y) * 4.0 * dt

    def draw(self, screen):
        # 1. Render visuals to a temporary surface to implement Camera Zoom easily
        temp_surf = pygame.Surface((1280, 720))
        temp_surf.fill((6, 4, 8))  # VOID_BLACK
        
        # Layer 1 & 2: Void fog background
        self.fog.draw(temp_surf)
        
        # Layer 4 & 5: Magic circle and independent runes
        if self.phase in ('B', 'C', 'D'):
            self.magic_circle.draw(temp_surf, 640, 550, self.circle_scale, self.circle_opacity, self.circle_angle1, self.circle_angle2)
            
        # Ground energy waves
        for w in self.energy_waves:
            w.draw(temp_surf)
            
        # Layer 6: Rising particles
        self.custom_particles.draw(temp_surf)
        
        # Layer 7: Radial Light Rays centered at the soul
        if self.phase in ('C', 'D'):
            self.light_rays.draw(temp_surf, (int(self.soul_x), int(self.soul_y)), self.elapsed, self.ray_intensity)
            
        # Layer 3 & 8: Floating breathing Soul with soft bloom glow
        if self.phase in ('A', 'B', 'C', 'D'):
            self.soul.draw(temp_surf, self.soul_x, self.soul_y, self.elapsed, self.soul_glow)
            
        # 2. Get screen shake offset values
        shake_dx, shake_dy = self.shake_offset
        
        # 3. Apply Camera Zoom and blit to main window screen
        if self.camera_zoom > 1.0:
            zoom_w = int(1280 / self.camera_zoom)
            zoom_h = int(720 / self.camera_zoom)
            zoom_x = (1280 - zoom_w) // 2
            zoom_y = (720 - zoom_h) // 2
            
            crop_rect = pygame.Rect(zoom_x, zoom_y, zoom_w, zoom_h)
            cropped_surf = temp_surf.subsurface(crop_rect)
            scaled_surf = pygame.transform.smoothscale(cropped_surf, (1280, 720))
            screen.blit(scaled_surf, (shake_dx, shake_dy))
        else:
            screen.blit(temp_surf, (shake_dx, shake_dy))
            
        # Layer 9: White Flash Overlay (Full screen)
        if self.phase in ('E', 'F'):
            self.white_flash.draw(screen)
            
        # Layer 10: Skip UI Overlay
        if self.phase != 'F':
            self._draw_skip_prompt(screen)

    def _draw_skip_prompt(self, screen):
        pulse = 0.5 + 0.5 * math.sin(self.elapsed * 2.5)
        alpha = int(80 + pulse * 90)
        
        skip_text = "[ ESC ] Skip"
        txt_surf = self.ui_font.render(skip_text, True, (240, 208, 120))
        txt_surf.set_alpha(alpha)
        
        tx = 1280 - txt_surf.get_width() - 32
        ty = 720 - txt_surf.get_height() - 24
        screen.blit(txt_surf, (tx, ty))


class WorldIntroductionScene(BaseScene):
    def __init__(self, game_state, particles, fonts):
        super().__init__(game_state, particles, fonts)
        self.elapsed = 0.0
        
        self.world_font = fonts["world"]
        self.body_font = fonts["body"]
        self.ui_font = fonts["ui"]
        self.text_fade_alpha = 0.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.next_scene = "title"

    def update(self, dt):
        self.elapsed += dt
        self.particles.update(dt)
        
        if self.text_fade_alpha < 255.0:
            self.text_fade_alpha = min(255.0, self.text_fade_alpha + 140.0 * dt)

    def draw(self, screen):
        width, height = screen.get_size()
        screen.fill((6, 4, 8))  # VOID_BLACK
        
        # Drifting background particles
        self.particles.draw(screen)
        
        # Display new world name generated in Phase 1
        world_name = self.game_state.get("world_name", "VALDREMOR").upper()
        world_txt = f"— {world_name} —"
        
        pulse = 0.5 + 0.5 * math.sin(self.elapsed * 1.5)
        glow_alpha = int(40 + pulse * 60)
        
        # Title Group
        title_top = self.body_font.render("AWAKENING IN THE NEW WORLD", True, (201, 168, 76))
        title_top.set_alpha(int(self.text_fade_alpha))
        screen.blit(title_top, (width // 2 - title_top.get_width() // 2, height // 2 - 140))
        
        main_world = self.world_font.render(world_txt, True, (240, 208, 120))
        main_world.set_alpha(int(self.text_fade_alpha))
        
        glow_world = self.world_font.render(world_txt, True, (201, 168, 76))
        glow_world.set_alpha(glow_alpha)
        
        screen.blit(glow_world, (width // 2 - glow_world.get_width() // 2, height // 2 - 70 + 2))
        screen.blit(main_world, (width // 2 - main_world.get_width() // 2, height // 2 - 70))
        
        # Details Panel
        details_y = height // 2 + 10
        player_name = self.game_state.get("player_name", "Chosen One")
        player_class = self.game_state.get("player_class", "Hero")
        
        line1 = f"Name: {player_name}"
        line2 = f"Class: {player_class.upper()}"
        line3 = "Your physical form begins to materialize..."
        
        lines = [line1, line2, line3]
        line_h = 32
        for idx, line in enumerate(lines):
            color = (232, 223, 200) if idx < 2 else (138, 122, 96)
            txt = self.ui_font.render(line, True, color)
            txt.set_alpha(int(self.text_fade_alpha))
            screen.blit(txt, (width // 2 - txt.get_width() // 2, details_y + idx * line_h))
            
        # Continue Prompt
        prompt_pulse = int(100 + 120 * (0.5 + 0.5 * math.sin(self.elapsed * 2.2)))
        prompt = self.ui_font.render("✦  Press ENTER to Return to Title  ✦", True, (240, 208, 120))
        prompt.set_alpha(int(min(prompt_pulse, self.text_fade_alpha)))
        screen.blit(prompt, (width // 2 - prompt.get_width() // 2, height - 100))
