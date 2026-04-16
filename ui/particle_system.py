import random
import pygame


class ParticleSystem:
    def __init__(self, count=150, width=1280, height=720):
        self.count = count
        self.width = width
        self.height = height
        self.particles = [self._new_particle() for _ in range(self.count)]

    def _pick_color(self):
        roll = random.random()
        if roll < 0.60:
            return (201, 168, 76)  # gold
        if roll < 0.85:
            return (180, 140, 220)  # purple
        return (255, 255, 255)  # white

    def _new_particle(self):
        return {
            "x": random.uniform(0, self.width),
            "y": random.uniform(0, self.height),
            "radius": random.uniform(0.5, 2.5),
            "dx": random.uniform(-0.3, 0.3),
            "dy": random.uniform(-0.6, -0.1),
            "alpha": random.randint(60, 200),
            "color": self._pick_color(),
        }

    def update(self, dt, rect=None, attract_to=None, attract_strength=0.0):
        if rect is not None:
            self.width = rect.width
            self.height = rect.height

        # Normalize speed to around 60 FPS movement units.
        step = dt * 60.0

        for p in self.particles:
            if attract_to is not None and attract_strength > 0.0:
                tx, ty = attract_to
                vx = tx - p["x"]
                vy = ty - p["y"]
                dist = max((vx * vx + vy * vy) ** 0.5, 1.0)
                p["x"] += (vx / dist) * attract_strength * step
                p["y"] += (vy / dist) * attract_strength * step

            p["x"] += p["dx"] * step
            p["y"] += p["dy"] * step

            # Wrap horizontally.
            if p["x"] < 0:
                p["x"] = self.width
            elif p["x"] > self.width:
                p["x"] = 0

            # Drift upward and reset to bottom when leaving top.
            if p["y"] < 0:
                p["y"] = self.height + random.uniform(0, 8)
                p["x"] = random.uniform(0, self.width)
            elif p["y"] > self.height:
                p["y"] = 0

    def draw(self, screen):
        for p in self.particles:
            radius = max(1, int(round(p["radius"])))
            size = radius * 2 + 2
            temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(
                temp_surf,
                (*p["color"], p["alpha"]),
                (size // 2, size // 2),
                radius,
            )
            screen.blit(temp_surf, (int(p["x"] - size // 2), int(p["y"] - size // 2)))
