import pygame
import sys
import random
import math

pygame.init()

# -------------------------
# Screen
# -------------------------

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fantasy Frame UI")

clock = pygame.time.Clock()

# -------------------------
# Load Frame
# -------------------------

frame = pygame.image.load(
    "assets/ui/frame.png"
).convert_alpha()

frame_rect = frame.get_rect(
    center=(WIDTH // 2, HEIGHT // 2)
)

# -------------------------
# Colors
# -------------------------

WHITE = (255, 255, 255)
BLUE = (120, 180, 255)

# -------------------------
# Font
# -------------------------

font = pygame.font.SysFont("timesnewroman", 36)

# -------------------------
# Particle System
# -------------------------

particles = []

def spawn_particle():

    x = random.randint(
        frame_rect.left,
        frame_rect.right
    )

    y = random.randint(
        frame_rect.top,
        frame_rect.bottom
    )

    particle = {
        "x": x,
        "y": y,
        "speed": random.uniform(20, 60),
        "size": random.randint(2, 4),
        "life": random.uniform(1.0, 2.0)
    }

    particles.append(particle)

# -------------------------
# Main Loop
# -------------------------

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # -------------------------
    # Spawn particles
    # -------------------------

    if len(particles) < 80:
        spawn_particle()

    # -------------------------
    # Draw Background
    # -------------------------

    screen.fill((8, 12, 20))

    # -------------------------
    # Update and Draw particles
    # -------------------------

    for p in particles[:]:

        p["y"] -= p["speed"] * dt
        p["life"] -= dt
        
        # Calculate fade out based on life
        alpha = int((p["life"] / 2.0) * 255)
        alpha = max(0, min(255, alpha))

        if p["life"] <= 0:
            particles.remove(p)
            continue
            
        # Draw particle with alpha
        temp_surface = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            temp_surface,
            (*BLUE, alpha),
            (p["size"], p["size"]),
            p["size"]
        )
        screen.blit(temp_surface, (int(p["x"] - p["size"]), int(p["y"] - p["size"])))

    # -------------------------
    # Draw Frame
    # -------------------------

    screen.blit(frame, frame_rect)

    # -------------------------
    # Title Text (Pulsing Glow Effect)
    # -------------------------
    
    time_ms = pygame.time.get_ticks()
    glow_intensity = 150 + int(math.sin(time_ms * 0.003) * 105)
    
    # Shadow / Glow Text
    glow_text = font.render("SYSTEM MESSAGE", True, (*BLUE, glow_intensity))
    glow_text.set_alpha(glow_intensity)
    
    text = font.render("SYSTEM MESSAGE", True, WHITE)

    screen.blit(glow_text, (WIDTH // 2 - text.get_width() // 2 + 2, frame_rect.top + 42))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, frame_rect.top + 40))

    pygame.display.flip()

pygame.quit()
sys.exit()