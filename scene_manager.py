import pygame

class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.pending_scene = None
        self.transition_phase = None
        self.transition_alpha = 0.0
        self.transition_speed = 900.0
        self.transition_overlay = None

    def change_scene(self, scene):
        if self.current_scene is None:
            self.current_scene = scene
            return

        if self.transition_phase is not None:
            return

        self.pending_scene = scene
        self.transition_phase = "out"
        self.transition_alpha = 0.0

    def _ensure_overlay(self, screen):
        if self.transition_overlay is None or self.transition_overlay.get_size() != screen.get_size():
            self.transition_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)

        if self.transition_phase == "out":
            self.transition_alpha += self.transition_speed * dt
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                if self.pending_scene is not None:
                    self.current_scene = self.pending_scene
                    self.pending_scene = None
                self.transition_phase = "in"
        elif self.transition_phase == "in":
            self.transition_alpha -= self.transition_speed * dt
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.transition_phase = None

    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)

        if self.transition_phase is not None:
            self._ensure_overlay(screen)
            self.transition_overlay.fill((0, 0, 0, int(self.transition_alpha)))
            screen.blit(self.transition_overlay, (0, 0))

    def handle_event(self, event):
        if self.transition_phase is not None:
            return

        if self.current_scene:
            self.current_scene.handle_event(event)

class Scene:
    def __init__(self, scene_manager):
        self.manager = scene_manager

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

    def handle_event(self, event):
        pass
