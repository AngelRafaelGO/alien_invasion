# General note 1: 'ai' stands for 'alien invasion'.
# Here we import the necesary modules for our game to work.
import sys
from time import sleep
import pygame

# Here we import our custom modules.
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    
    def __init__(self):
        """Initialize the alien_invasion game and create game resources."""
        # py.init() is a function that initializes the background settings that
        # pygame need to work.
        pygame.init()

        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # Create all the necesary instances for ai.
        # Create an instance to store game statistics and create a 
        # scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # Here we create the Play button for the game.
        self.play_button = Button(self, "Play")
        # Here we create the Game Over button.
        self.game_over_button = Button(self, "Game Over")
        
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            
    def _check_events(self):
        """Responde to keypresses and mouse events."""
        # Watch for keyboard and mouse events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.main_theme()
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()
            # Reset the game statistics.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_lvl()
            self.sb.prep_ships()

            # Get rid on any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Here we hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        # Here we add a short cut to exit the game.
        elif event.key == pygame.K_q:
            sys.exit()
        # Here we add the firing key.
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            simple_shot = pygame.mixer.Sound('sound_effects/simple_shot.wav')
            simple_shot.play()
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

            # Getting rid of the bullets that are out of the game window.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # We remove the print call for game effitency.
        # print(len(self.bullets))
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any aliens and bullets that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                alien_explosion = pygame.mixer.Sound('sound_effects/alien_explosion.wav')
                alien_explosion.play()
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existingn bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Here we increase the lvl each time the alien fleet is defeated.
            self.stats.lvl += 1
            self.sb.prep_lvl()

    def _ship_hit(self):
        """Set behavior when the ship gets hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships left and update scorboard (ships left).
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Get rid of any remaining aliens or bullets.
            self.aliens.empty()
            self.bullets.empty()
            # Create a new fleet and recenter the ship.
            self._create_fleet()
            self.ship.center_ship()
            # Pause the game after the ship is hit.
            sleep(0.5)
        if self.stats.ships_left == 0:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check for aliens that reach the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # We want the same behavior as when the ship gets hit,
                # so we call the same method.
                self._ship_hit()
                break    

    def _update_aliens(self):
        """
        Check if the alien fleet is at the edge,
            then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between aliens is equal to the width of one alien.
        alien = Alien(self)
        alien_width, alien_hieght = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit to the screen.
        ship_height = self.ship.rect.height
        # Here we can reduce the amount of rows.
        available_space_y = (self.settings.screen_heigth -
                                (3 * alien_hieght) - ship_height)
        number_rows = available_space_y //(2 * alien_hieght)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
    
    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien_width = alien.rect.width
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Set behavior when aliens touch the screen edges."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the alien fleet's positions and change to opposite direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        # This line changes the fleet's direction.
        # It's outside the loop because we only want this to occur once.
        self.settings.fleet_direction *= -1

    def main_theme(self):
        """Initialize background music loop."""
        # Here we load and play the main theme.
        pygame.mixer.music.load('sound_effects/main_theme.wav')
        pygame.mixer.music.play(-1)

    def _update_screen(self):
        """Update images on the screen and then filp to the new screen."""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        # Here we call our ship, after filling our screen so that it will
        # be on top of our background.
        self.ship.blitme()
        # Here we update de screen with all our fired bullets.
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Draw the scoreboard to the screen.
        self.sb.show_score()

        # Draw the play button to the screen if the game is inactive.
        if not self.stats.game_active and self.stats.ships_left > 0:
            self.play_button.draw_button()

        # Here we draw the Game Over button to the screen.
        if self.stats.ships_left == 0:
            self.game_over_button.draw_button()
        
        # Make the most recently drawn screen visible.
        pygame.display.flip()

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()