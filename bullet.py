
import pygame as pg
from pygame.sprite import Sprite


class Bullet(Sprite):
    """A class that represents a travelling bullet. This class uses code
    from Python Crash Course"""

    def __init__(self, game):
        """Create a bullet object at the ship's current position"""
        super().__init__()
        self.game = game
        self.ship = game.ship

        self.width = self.game.vars.bullet_w
        self.height = self.game.vars.bullet_h
        self.color = pg.Color(self.game.vars.bullet_color)

        # create the rectangle for the bullet and set its position
        self.rect = pg.Rect(0, 0, self.width, self.height)
        self.rect.midtop = self.ship.rect.midtop

        # store the bullet's y-value so it can move upward accurately
        self.y = float(self.rect.y)
        self.x = float(self.rect.x)

    def update(self, dt):
        """
        Update the bullet's position, move the bullet rectangle, and delete
        the bullet if it has moved off screen
        """
        # pixels per second * delta time in seconds
        move_distance = self.game.vars.bullet_speed * dt
        self.y -= move_distance  # move up
        self.rect.y = self.y

        # align the bullet with the ship's centerx until it clears the ship
        if self.rect.bottom >= self.ship.rect.top:
            self.rect.centerx = self.ship.rect.centerx

        # remove the bullet if it has left the screen
        if self.rect.bottom < self.game.rect.top:
            self.remove_self()

    def draw_bullet(self):
        """draw the bullet to the game screen"""
        pg.draw.ellipse(self.game.screen, self.color, self.rect)

    def remove_self(self):
        """Remove this bullet from the bullets group"""
        self.remove(self.ship.bullets)
