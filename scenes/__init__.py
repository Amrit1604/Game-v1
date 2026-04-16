class BaseScene:
    def __init__(self, game_state, particles, fonts):
        self.game_state = game_state
        self.particles = particles
        self.fonts = fonts
        self.next_scene = None

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
