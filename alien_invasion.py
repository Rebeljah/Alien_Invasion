import sys
import pygame as pg
# import random as r

import settings
from ship import Ship
from alien import AlienFleet
from visual_fx import AsteroidGroup, FpsDisplay


class AlienInvasion:
    """overall class to manage game assets and behavior"""

    def __init__(self):
        """initialize the game, and create game resources"""
        pg.init()
        self.vars = settings.Vars()
        self.clock = pg.time.Clock()
        self.is_running = True

        # create the screen and get its rect
        self.screen = pg.display.set_mode(
            (self.vars.window_w, self.vars.window_h)
        )
        self.rect = self.screen.get_rect()

        pg.display.set_caption("Space Knockoffs!")
        pg.display.set_icon(pg.image.load('images/asteroid.bmp'))

        # set the background
        bg_surface = pg.image.load('images/bg.bmp').convert()
        self.bg = pg.transform.scale(bg_surface, self.rect.size)

        self.fps_display = FpsDisplay(self)
        self.ship = Ship(self)
        self.alien_fleet = AlienFleet(self)
        self.asteroids = AsteroidGroup(self, self.vars.num_asteroids)

    def run_game(self):
        """Main loop for checking events and updating objects.
        once everything is updated, the _update_screen method is called."""
        is_first_frame = True
        while True:
            # tick game clock, set max frame rate, get delta time in seconds
            dt = self.clock.tick(self.vars.max_fps) / 1000.0
            # limit dt to prevent items from teleporting on loss of frames
            if dt > 0.2:
                dt = 0.2

            if self.vars.show_fps:
                self.fps_display.update()

            self._check_events()
            if self.is_running or is_first_frame:
                is_first_frame = False
                self.asteroids.update(dt)
                self.alien_fleet.update(dt)
                self.ship.update(dt)
                self.ship.bullets.update(dt)
                self._bullet_alien_collide()

            self._update_screen()

    def _check_events(self):
        """Listen for events from the event queue"""

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.KEYDOWN:
                self._check_keydown_event(event)
            elif event.type == pg.KEYUP:
                self._check_keyup_event(event)

    def _check_keydown_event(self, event):
        """respond to key presses"""
        if event.key == self.vars.key_quit:
            sys.exit()

        if self.is_running:
            if event.key == self.vars.key_r:
                self.ship.moving_right = True
            elif event.key == self.vars.key_l:
                self.ship.moving_left = True
            elif event.key == self.vars.key_shoot:
                self.ship.fire_bullet()

    def _check_keyup_event(self, event):
        """respond to key releases"""
        if self.is_running:
            if event.key == self.vars.key_r:
                self.ship.moving_right = False
            elif event.key == self.vars.key_l:
                self.ship.moving_left = False

    def _bullet_alien_collide(self):
        """
        Collide all the bullet sprites will all the alien sprites, remove the
        bullet and then blow up the alien
        """
        collisions = pg.sprite.groupcollide(self.ship.bullets, self.alien_fleet,
                                            False, False)
        for alien_list in collisions.values():
            for alien in alien_list:
                alien.blow_up()

        if not self.vars.bullets_persist:
            for bullet in collisions.keys():
                bullet.remove_self()

    def _update_screen(self):
        """redraw the screen after each loop"""

        self.screen.blit(self.bg, (0, 0))

        self.asteroids.draw(self.screen)

        for bullet in self.ship.bullets:
            bullet.draw_bullet()
        self.ship.blit_self()

        self.alien_fleet.draw(self.screen)

        if self.vars.show_fps:
            self.fps_display.blit_self()

        pg.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
