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
    Course for the wonderful explanation of the main game loop and event
    handling"""

    def __init__(self):
        """initialize the game, and create game resources"""
        pg.init()
        self.vars = settings.Vars()
        self.clock = pg.time.Clock()
        self.dt = 0
        self.state = 'game'  # 'menu'
        self.first_frame = True

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
        # Initialize objects
        self.menu = MenuManager(self)
        self.scoreboard = Scoreboard(self)
        self.fps_display = FpsDisplay(self)
        self.ship = Ship(self)
        self.alien_fleet = AlienFleet(self)
        self.asteroids = AsteroidGroup(self)

    def run_game(self):
        """Main loop for checking events and updating objects.
        once everything is updated, the _update_screen method is called."""

        while True:
            # tick game clock, set max frame rate, get delta time in seconds
            self.dt = self.clock.tick(self.vars.max_fps) / 1000.0
            if self.dt > 0.10:
                self.dt = 0.10

            if self.state == 'game' or self.first_frame:
                self.first_frame = False
                self._check_game_events()
                self._update_game(self.dt)

            elif self.state == 'menu':
                self.menu.check_menu_events()
                self.menu.update_menu()

            # the game will always be drawn. This permits the use
            # of a transparent menu background
            self._draw_game()
            if self.state == 'menu':
                self.menu.draw_menu()

    def _check_game_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit_game()
            elif event.type == pg.KEYDOWN:
                if event.key == self.vars.key_quit:
                    self.quit_game()
                elif event.key == self.vars.key_move_l:
                    self.ship.moving_left = True
                elif event.key == self.vars.key_move_r:
                    self.ship.moving_right = True
                elif event.key == self.vars.key_shoot:
                    self.ship.fire_bullet()
            elif event.type == pg.KEYUP:
                if event.key == self.vars.key_move_l:
                    self.ship.moving_left = False
                elif event.key == self.vars.key_move_r:
                    self.ship.moving_right = False

    def _update_game(self, dt):
        # FX
        self.asteroids.update(dt)
        # Alien fleet
        self.alien_fleet.update(dt)
        # Player ship
        self.ship.update(dt)
        self.ship.bullets.update(dt)
        self._bullet_alien_collide()
        # Overlays
        self.scoreboard.update()
        if self.vars.show_fps:
            self.fps_display.update()

    def _draw_game(self):
        """Blit surfaces onto the game screen and then update the display"""

        self.screen.blit(self.bg, (0, 0))

        # FX
        self.asteroids.draw(self.screen)

        # Player ship
        for bullet in self.ship.bullets:
            bullet.draw_bullet()
        self.ship.blit_self()

        # Alien fleet
        self.alien_fleet.draw(self.screen)

        # Overlays
        self.scoreboard.blit_self()
        if self.vars.show_fps:
            self.fps_display.blit_self()

        pg.display.flip()

    def _bullet_alien_collide(self):
        """
        Collide all the bullet sprites will all the alien sprites, remove the
        bullet and then blow up the alien
        """
        collisions = pg.sprite.groupcollide(self.ship.bullets, self.alien_fleet,
                                            False, False)
        for alien_list in collisions.values():
            for alien in alien_list:
                self.scoreboard.player_score += alien.point_value
                alien.blow_up()

        if not self.vars.bullets_persist:
            for bullet in collisions.keys():
                bullet.remove_self()

    def quit_game(self):
        """save data as needed and close the game"""
        self.scoreboard.leaderboard.update_leaderboard()
        sys.exit()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
