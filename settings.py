class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's static settings."""
        # settings
        self.screen_width = 1200
        self.screen_heigth = 800
        self.bg_color = (0, 2, 13)

        # Ship settings
        self.ship_limit = 3

        # Bullet settings
        self.bullet_color = (0, 255, 221)
        self.bullets_allowed = 5

        # Alien settings.
        self.fleet_drop_speed = 10

        # Here we set how quickly the game speeds up.
        self.speedup_scale = 1.3
        self.ship_speedup_scale = 1.1
        self.bullet_speedup_scale = 1.2
        self.score_scale = 1.5
        self.initialize_dynamic_settings()

        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

    def initialize_dynamic_settings(self):
        """Initialize settings that change throuought the game."""
        self.ship_speed = 1.2
        self.bullet_speed = 3.0
        self.bullet_width = 50
        self.bullet_height = 5
        self.alien_speed = 1.0

        # fleet_direction of 1 represents right; fleet_direction of -1 represents left.
        self.fleet_direction = 1

        # Scoring.
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings."""
        self.ship_speed *= self.ship_speedup_scale
        self.bullet_width *= self.bullet_speedup_scale
        self.bullet_height *= self.bullet_speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        
        # Here we scale up the point per alien hit.
        self.alien_points = int(self.alien_points * self.score_scale)
