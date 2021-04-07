import pygame as pg
import sys

import settings
from menu import MenuManager
from overlays import Scoreboard, FpsDisplay
from visual_fx import AsteroidGroup
from ship import Ship
from alien import AlienFleet


class AlienInvasion:
    """overall class to manage game assets and behavior, thanks to Python Crash
    Course for the wonderful explanation of the main game loop"""

    def __init__(self):
        """initialize the game, and create game resources"""
        pg.init()
        self.vars = settings.Vars()

        self.clock = pg.time.Clock()
        self.dt = 0

        self.debug = False
        self.state = 'menu'  # or 'game'

        # create the screen and get its rect
        self.screen = pg.display.set_mode(
            (self.vars.window_w, self.vars.window_h),
            flags=pg.HWSURFACE
        )
        self.rect = self.screen.get_rect()

        pg.display.set_caption("Space Knockoffs!")

        # set the background
        bg_surface = pg.image.load('images/bg.bmp').convert()
        self.bg = pg.transform.scale(bg_surface, self.rect.size)

        self.input_manager = InputManager(self)
        self.scoreboard = Scoreboard(self)
        self.fps_display = FpsDisplay(self)
        self.ship = Ship(self)
        self.alien_fleet = AlienFleet(self)
        self.asteroids = AsteroidGroup(self)
        self.menu = MenuManager(self)

        self._update_game(self.dt)

    def run_game(self):
        """Main loop for checking events and updating objects.
        once everything is updated, the _update_screen method is called."""

        while True:
            # tick game clock, set max frame rate, get delta time in seconds
            self.dt = self.clock.tick(self.vars.max_fps) / 1000.0
            if self.dt > 0.10: # limit dt in-case of freeze
                self.dt = 0.10

            self.input_manager.check_events()

            if self.state == 'game':
                self._update_game(self.dt)
            elif self.state == 'menu':
                self.menu.update_menu()

            self._draw_screen()

            pg.display.flip()

    def _update_game(self, dt):
        """
        Updates the objects that are active while the game is playing. These
        objects all stop updating when the menu is open
        """
        self.alien_fleet.update(dt)
        # Player ship
        self.ship.update(dt)
        self.ship.bullets.update(dt)
        self._bullet_alien_collide()

        self.scoreboard.update()
        self.asteroids.update(dt)

    def _draw_screen(self):
        """
        Handle drawing of all objects to the screen. The menu is only drawn
        if in menu mode
        """

        self._draw_game()

        if self.state == 'menu':
            self.menu.draw_menu()

        if self.vars.show_fps:
            self.fps_display.update()
            self.fps_display.draw_fps()

    def _draw_game(self):
        """
        blit game surfaces onto the screen. These are always blitted. If the
        menu is open, the game elements will be blitted underneath of the menu.
        """

        self.screen.blit(self.bg, (0, 0))

        # FX
        self.asteroids.draw(self.screen)

        # Player ship
        for bullet in self.ship.bullets:
            bullet.draw_bullet()
        self.ship.draw_self()

        # Alien fleet
        self.alien_fleet.draw(self.screen)

        # Overlays
        self.scoreboard.draw_self()

    def _bullet_alien_collide(self):
        """
        Collide all the bullet sprites will all the alien sprites, remove the
        bullet and then blow up the alien and add score.
        """
        collisions = pg.sprite.groupcollide(self.ship.bullets, self.alien_fleet,
                                            False, False)
        for alien_list in collisions.values():
            for alien in alien_list:
                alien.blow_up()
                self.scoreboard.player_score += alien.point_value

        if self.vars.kill_bullets:
            for bullet in collisions.keys():
                bullet.remove_self()

    def toggle_menu(self):
        """Switch state to 'menu' if in 'game' and visa versa"""
        self.state = 'game' if self.state == 'menu' else 'menu'

    def quit_game(self):
        """save data as needed and close the game"""
        self.scoreboard.leaderboard.update_high_scores()
        sys.exit()


class InputManager:
    def __init__(self, game):
        self.game = game
        self.vars = game.vars

        # these are updated while the game is in the menu state
        self.mouse_pos = 0, 0
        self.is_clicking = False

    def check_events(self):
        """
        First determine if the user has quit the game, then check events
        for the game or menu depending on the current game state
        """
        for event in pg.event.get():

            # check for user quit via the x button
            if event.type == pg.QUIT:
                self.game.quit_game()
            # check for user quit or menu toggle
            elif event.type == pg.KEYDOWN:
                if event.key == self.vars.key_quit:
                    self.game.quit_game()
                elif event.key == self.vars.key_menu:
                    self.game.toggle_menu()
                elif event.key == self.vars.key_toggle_debug:
                    self.game.debug = False if self.game.debug else True

            # update the mouse
            self.mouse_pos = pg.mouse.get_pos()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.is_clicking = True

            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_clicking = False

            # check game events if in game
            if self.game.state == 'game':
                self._check_game_events(event)

    def _check_game_events(self, event):
        """Handle events that occur while the game in playing"""
        if event.type == pg.KEYDOWN:
            # ship controls
            if event.key == self.vars.key_move_l:
                self.game.ship.moving_left = True
            elif event.key == self.vars.key_move_r:
                self.game.ship.moving_right = True
            elif event.key == self.vars.key_shoot:
                self.game.ship.fire_bullet()

        elif event.type == pg.KEYUP:
            # ship controls
            if event.key == self.vars.key_move_l:
                self.game.ship.moving_left = False
            elif event.key == self.vars.key_move_r:
                self.game.ship.moving_right = False


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
