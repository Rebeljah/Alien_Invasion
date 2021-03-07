import pygame as pg
import random
import os

from settings import scale


class AlienFleet(pg.sprite.Group):
    """Class used to control the fleet of aliens on screen, inherits from Group"""
    def __init__(self, game):
        super().__init__()
        """
        Find the best spacing between each alien in the fleet based on a given
        usable width and a given usable height. The fleet will be positioned
        in a grid that roughly fills the given usable area.
        """
        self.game = game

        # information used to space the fleet
        self.usable_w = game.rect.width
        self.usable_h = .55 * game.rect.height
        self.num_columns = game.vars.fleet_columns
        self.num_rows = game.vars.fleet_rows
        # space between each alien's starting x, y)
        self.hoz_spacing = self.usable_w / self.num_columns
        self.vert_spacing = self.usable_h / self.num_rows

        # load possible ship surfaces
        fp = os.path.join('images/', 'alien_ships/')
        self.ship_images = [pg.image.load(fp+fn) for fn in os.listdir(fp)]

        # use the preceding information to build an evenly spaced fleet
        self._build_new_fleet()

    def _build_new_fleet(self):
        """Create an evenly spaced 'fleet' of alien objects by multiplying
        the aliens row/column position by a pre-determiend vertical and
        horizontal spacing
        """
        def random_image(): return random.choice(self.ship_images)

        for row in range(self.num_rows):
            row_of_aliens = [
                self.Alien(self.game, random_image())
                for col in range(self.num_columns)
            ]
            # move each alien in the row to it's correct x,y position
            for column, alien in enumerate(row_of_aliens, start=0):
                alien.x += column * self.hoz_spacing
                alien.y += row * self.vert_spacing

            self.add(*row_of_aliens)

    def update(self, dt):
        """Perform actions to the group as a whole. Overrides super method"""
        # add a new fleet immediately after the old one in destroyed
        if len(self) == 0:
            self._build_new_fleet()

        for alien in self.sprites():
            alien.update(dt)

    class Alien(pg.sprite.Sprite):
        def __init__(self, game, image):
            super().__init__()
            """
            Represents an enemy ship that is part of a larger group (fleet) of
            aliens.
            """
            # get access to attributes of the main game class
            self.game = game

            # Load a random alien image and get the surface and rect
            self.image = image

            self.image, self.rect = scale(image, self.game.screen,
                                          self.game.vars.alien_scale)

            # Used to keep accurate count of current pixel location
            self.x = self.y = 0.0
            # velocity
            self.vel_x = self.game.vars.alien_vel_x
            self.drop_height = self.game.vars.fleet_drop_height

        def update(self, dt):
            """
            -Move self left / right. If colliding with wall, reverse direction and
            move down one level.
            -Aliens that hit the player or the floor both have different behaviors.
            """
            # move on the x-axis
            self.x += self.vel_x * dt

            # reverse and move down on wall collision
            def moving_left(): return self.vel_x < 0
            def moving_right(): return self.vel_x > 0
            def colliding_left(): return self.rect.left < 0
            def colliding_right(): return self.rect.right > self.game.rect.w

            if (colliding_left() and moving_left() or
                    colliding_right() and moving_right()):
                self.vel_x *= -1
                self.y += self.drop_height

            self.rect.topleft = (self.x, self.y)

            # check if has alien has hit the floor
            if self.rect.bottom >= self.game.rect.bottom:
                self._hit_bottom()
            # check if alien has hit the player
            elif self.rect.colliderect(self.game.ship.rect):
                self._hit_player_ship()

        def _hit_bottom(self):
            """ Do a series of actions when the alien reaches the bottom"""
            print('hit bottom', end=' ')
            self.blow_up()

        def _hit_player_ship(self):
            """ Do a series of actions when an alien hits the player"""
            print('hit player', end=' ')
            self.blow_up()

        def blow_up(self):
            """Creates an effect before removing self from group"""
            print('ALIEN SHIP EXPLOSION!')
            self.remove(self.game.alien_fleet)

        def blitme(self):
            self.game.screen.blit(self.image, self.rect)
