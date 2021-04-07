
import pygame as pg
from pygame.sprite import Sprite

from settings import scale
from bullet import Bullet


class Ship(Sprite):
    """A class to manage the player's ship. This class relies heavily on the
    great code found in Python Crash Course"""

    def __init__(self, game):
        super().__init__()

        self.vars = game.vars
        self.game = game

        # create a sprite group for bullet sprites
        self.bullets = pg.sprite.Group()

        # load and scale the ship image then get its rectangle
        ship_surface = pg.image.load('images/ship1.bmp').convert_alpha()
        self.image, self.rect = scale(
            ship_surface, self.game.screen, self.vars.ship_scale
        )

        # start the new ship at the bottom center of the screen
        self.rect.midbottom = self.game.rect.midbottom

        self.x = float(self.rect.x)
        # movement flags
        self.velocity = self.vars.ship_speed
        self.moving_right = False
        self.moving_left = False

    def update(self, dt):
        """
        Update the ship's position based on the movement flag. Since
        the ship's speed is in pixels per second, multiply the speed by the
        amount of seconds passed since last update
        """

        # pixels per second * delta time in seconds
        move_distance = self.velocity * dt

        if self.moving_right and self.rect.right < self.game.rect.right:
            self.x += move_distance
        elif self.moving_left and self.rect.left > 0:
            self.x -= move_distance

        self.rect.x = self.x

    def fire_bullet(self):
        """Initialize a new bullet and add it to the bullet group"""
        if len(self.bullets) < self.vars.max_bullets:
            self.bullets.add(Bullet(self.game))

    def draw_self(self):
        """blit the ship to the screen at its current position"""
        self.game.screen.blit(self.image, self.rect)
