import pygame.font

class Button:
    """A general button."""

    def __init__(self, ai_game, msg):
        """Initialize button attributes."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Here we set the dimensions and properties of the button.
        self.width, self.height = 220, 75
        self.button_color = (21, 21, 21)
        self.text_color = (132, 132, 132)
        self.font = pygame.font.SysFont(None, 48)

        # Build the button's rect object and center it.
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # The button message need to be prepped only once.
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """Turnn msg into a rendered image and center text on the button."""
        self.msg_image = self.font.render(msg, True, self.text_color, 
                self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        """Draw blank button and then the message."""
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)