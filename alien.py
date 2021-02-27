import pygame as pg
from pygame.sprite import Sprite
import random

from settings import scale


def build_alien_fleet(game):
    """
    Find the best spacing between each alien in the fleet based on a given
    usable width and a given usable height. The fleet will be positioned
    in a grid that roughly fills the given usable area.
    """
    usable_w = game.rect.width
    usable_h = .55 * game.rect.height
    columns: int = game.vars.fleet_columns
    rows: int = game.vars.fleet_rows

    hoz_spacing = usable_w / columns
    vert_spacing = usable_h / rows

    for row in range(rows):
        # create a row of aliens
        row_of_aliens = [Alien(game) for _ in range(columns)]

        # move each alien in the row to it's correct x,y position
        for column, alien in enumerate(row_of_aliens, start=0):
            alien.x += column * hoz_spacing
            alien.y += row * vert_spacing

        game.aliens.add(*row_of_aliens)


class Alien(Sprite):
    def __init__(self, game):
        super().__init__()
        """
        Represents an enemy ship that is part of a larger group (fleet) of aliens.
        """
        # get access to attributes of the main game class
        self.game = game

        # Load a random alien image and get the surface and rect
        image = pg.image.load(
            random.choice(['images/alien1.bmp', 'images/alien2.bmp'])
        ).convert_alpha()
        self.image, self.rect = scale(image, self.game.screen,
                                      self.game.vars.alien_scale)

        # Used to keep accurate count of current location
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # velocity
        self.vel_x = self.game.vars.alien_vel_x
        self.drop_height = self.game.vars.fleet_drop_height

    def update(self, dt):
        """
        -Move self left / right. If colliding with wall, reverse direction and
        move down one level.
        -Aliens that hit the player or the floor both have different behaviors.
        """
        # left / right
        self.x += self.vel_x * dt
        # reverse and move down on wall collision
        if (self.rect.left < 0 and self.vel_x < 0) or \
                (self.rect.right > self.game.rect.right and self.vel_x > 0):
            self.vel_x *= -1
            self.y += self.drop_height

        # move the rect
        self.rect.x = self.x
        self.rect.y = self.y

        # check if has alien has hit the floor
        if self.rect.bottom >= self.game.rect.bottom:
            self._hit_bottom()
        # check if alien has hit the player
        elif self.rect.colliderect(self.game.ship.rect):
            self._hit_player_ship()

    def _hit_bottom(self):
        """ Do a series of actions when the alien reaches the bottom"""
        self.blow_up()

    def _hit_player_ship(self):
        """ Do a series of actions when an alien hits the player"""
        self.blow_up()

    def blow_up(self):
        """Creates an effect before removing self from group"""
        print('ALIEN SHIP EXPLOSION!')
        self.remove(self.game.aliens)

    def blitme(self):
        self.game.screen.blit(self.image, self.rect)
