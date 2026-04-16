import pygame

class FantasyFrame:
    def __init__(self, rect, image_path="assets/ui/frame.png"):
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            # Scale the image to exactly match the requested rect, fixing any "distorted" rendering limits
            self.image = pygame.transform.smoothscale(self.original_image, rect.size)
            self.rect = self.image.get_rect(center=rect.center)
        except Exception:
            # Fallback if no image found
            self.image = pygame.Surface(rect.size, pygame.SRCALPHA)
            self.image.fill((20, 30, 50))
            pygame.draw.rect(self.image, (120, 180, 255), self.image.get_rect(), 4)
            self.rect = rect

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def draw_progress(self, screen, progress):
        # Animate from a vertical slit at center to full frame using real scaling.
        progress = max(0.0, min(1.0, progress))
        current_width = max(2, int(self.rect.width * progress))

        scaled_image = pygame.transform.smoothscale(self.image, (current_width, self.rect.height))
        dest_x = self.rect.centerx - current_width // 2
        screen.blit(scaled_image, (dest_x, self.rect.y))
