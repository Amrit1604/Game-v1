import pygame
from scene_manager import Scene
from scenes.dead_message_scene import DeadMessageScene

class IntroScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.timer = 0
        self.duration = 1.0 # Wait 1 second

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.manager.change_scene(DeadMessageScene(self.manager))

    def draw(self, screen):
        screen.fill((0, 0, 0)) # Pure black screen

    def handle_event(self, event):
        pass
