import pygame

from scenes.s1_title import TitleScene
from scenes.s2_death import DeathScene
from scenes.s3_void import VoidScene
from scenes.s4_goddess import GoddessScene
from scenes.s5_identity import IdentityScene
from scenes.s6_judgment import JudgmentScene
from scenes.s7_portal import PortalScene
from scenes.world_scene import ReincarnationScene, WorldIntroductionScene
from ui.particle_system import ParticleSystem
from ui.phase1_ui import VOID_BLACK, load_font


pygame.init()

WIDTH = 1280
HEIGHT = 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reborn Into Darkness")
clock = pygame.time.Clock()

game_state = {
    "player_name": "",
    "player_story": "",
    "player_personality": "",
    "player_class": "",
    "world_name": "",
}

fonts = {
    "title": load_font(72),
    "subtitle": load_font(20),
    "body": load_font(28),
    "ui": load_font(18),
    "small": load_font(12),
    "italic": load_font(28, italic=True),
    "world": load_font(36),
}

particles = ParticleSystem(count=150, width=WIDTH, height=HEIGHT)

scene_factories = {
    "title": TitleScene,
    "death": DeathScene,
    "void": VoidScene,
    "goddess": GoddessScene,
    "identity": IdentityScene,
    "judgment": JudgmentScene,
    "portal": PortalScene,
    "reincarnation": ReincarnationScene,
    "world_intro": WorldIntroductionScene,
}


def make_scene(name):
    scene_cls = scene_factories[name]
    return scene_cls(game_state, particles, fonts)


def fade_to_black(surface, elapsed, duration):
    ratio = max(0.0, min(1.0, elapsed / max(duration, 1e-6)))
    alpha = int(255 * ratio)
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    surface.blit(overlay, (0, 0))


def run_game():
    current_scene = make_scene("title")

    transition_state = None
    transition_elapsed = 0.0
    transition_duration = 0.4
    pending_scene_name = None

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if transition_state is None:
            current_scene.handle_events(events)
            current_scene.update(dt)

            if current_scene.next_scene:
                pending_scene_name = current_scene.next_scene
                current_scene.next_scene = None
                transition_state = "out"
                transition_elapsed = 0.0
        else:
            # Keep animations alive during fade, but lock inputs.
            current_scene.update(dt)
            transition_elapsed += dt

            if transition_state == "out" and transition_elapsed >= transition_duration:
                current_scene = make_scene(pending_scene_name)
                pending_scene_name = None
                transition_state = "in"
                transition_elapsed = 0.0
            elif transition_state == "in" and transition_elapsed >= transition_duration:
                transition_state = None
                transition_elapsed = 0.0

        screen.fill(VOID_BLACK)
        particles.draw(screen)
        current_scene.draw(screen)

        if transition_state == "out":
            fade_to_black(screen, transition_elapsed, transition_duration)
        elif transition_state == "in":
            # Reverse fade for fade-in.
            fade_to_black(screen, transition_duration - transition_elapsed, transition_duration)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()