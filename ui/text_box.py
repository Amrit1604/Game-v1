import pygame

class TextBox:
    def __init__(self, rect, font_size=20):
        self.rect = pygame.Rect(rect)
        # Use a cleaner font for inputs
        self.font = pygame.font.SysFont("palatinolinotype, georgia", font_size, italic=True)
        self.text = ""
        self.active = True
        
        # Phase 1 Reborn Theme colors
        self.color_active = (201, 168, 76)      # Gold
        self.color_inactive = (122, 96, 48)     # Gold Dim
        self.text_color = (232, 223, 200)       # Light text
        self.bg_color = (201, 168, 76, 12)      # Barely visible gold tint
        
        self.color = self.color_inactive
        
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 100:
                        self.text += event.unicode
                        
    def update(self, dt):
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= 0.5:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible
        else:
            self.cursor_visible = False

    def draw(self, screen):
        # Slightly tinted background
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        screen.blit(bg_surface, (self.rect.x, self.rect.y))
        
        # Draw text
        txt_surface = self.font.render(self.text, True, self.text_color)
        
        # Cap text width so it scrolls to cursor
        margin = 15
        max_w = self.rect.width - margin * 2
        text_y = self.rect.y + (self.rect.height - txt_surface.get_height()) // 2
        
        if txt_surface.get_width() > max_w:
            # Scroll left to show end of text
            offset_x = txt_surface.get_width() - max_w
            text_x = self.rect.x + margin
            area = pygame.Rect(offset_x, 0, max_w, txt_surface.get_height())
            screen.blit(txt_surface, (text_x, text_y), area)
            cursor_x = self.rect.x + margin + max_w + 4
        else:
            text_x = self.rect.x + max(margin, (self.rect.width - txt_surface.get_width()) // 2)
            screen.blit(txt_surface, (text_x, text_y))
            cursor_x = text_x + txt_surface.get_width() + 4

        # Bottom Border only
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.line(screen, color, (self.rect.left, self.rect.bottom), (self.rect.right, self.rect.bottom), 2)

        # Draw cursor
        if self.cursor_visible and self.active:
            pygame.draw.rect(screen, self.color_active, (cursor_x, text_y + 4, 3, txt_surface.get_height() - 8))
