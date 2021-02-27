import pygame as pg
from pygame.sprite import Sprite
import random

from settings import scale


class Asteroid(Sprite):
    """
    Simulate a big'ol asteroid that bounces all over the screen like one
    of those 90's DVD screensavers.
    """

    def __init__(self, game):
        super().__init__()

        # get game info
        self.game = game
        self.vars = game.vars

        # load and scale the asteroid image then get its rectangle
        ratio = self.vars.asteroid_scale
        image = pg.image.load('images/asteroid.bmp').convert_alpha()
        self.image, self.rect = scale(
            image, game.screen, ratio
        )
        self.rect.midtop = self.game.rect.midbottom

        # used for resetting between rotations
        self.original_image = self.image

        # rotation info
        self.base_rotation_vel = self.vars.asteroid_rps
        self.rotation_vel = self.base_rotation_vel
        self.degree = 0.0

        # Get base velocity, save original then set variables
        self.base_vel = self.vars.asteroid_velocity
        self.vel_x = self.base_vel
        self.vel_y = self.base_vel

        # track location by center since asteroid is spinning
        self.centerx = float(self.rect.x)
        self.centery = float(self.rect.y)

    def update(self, dt):
        """
        Handles the rotation and movement of the asteroid
        """
        self._check_screen_exit()

        self._spin(dt)
        # move the asteroid by its velocity in PPS
        self.centerx += self.vel_x * dt
        self.centery += self.vel_y * dt
        self.rect.centerx = self.centerx
        self.rect.centery = self.centery

    def _spin(self, dt):
        """
        Rotate the original asteroid image surface to the the current degree
        of the asteroid object. Assign the rotated image to self.image

        This method is need as images tend to get corrupted over multiple
        rotations. Rotozoom is used here solely for its increased quality
        """
        self.degree += self.rotation_vel * dt
        # reset the angle after 360 degrees to save memory
        if -360 < self.degree < 360:
            self.image = pg.transform.rotozoom(self.original_image, self.degree, 1)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.degree = 0

    def _check_screen_exit(self):
        """
        When the asteroid leaves the screen, randomly amplify it's velocities,
        randomly amplify it's size, move it to another part of the screen.
        """
        screen_w = self.game.rect.width
        screen_h = self.game.rect.height
        # check left / right exit
        if self.rect.right < 0 and self.vel_x < 0:
            self.vel_x *= -1
            self._randomize_asteroid()
        elif self.rect.left > screen_w and self.vel_x > 0:
            self.vel_x *= -1
            self._randomize_asteroid()

        # check top / bottom exit
        elif self.rect.bottom < 0 and self.vel_y < 0:
            self.vel_y *= -1
            self._randomize_asteroid()
        elif self.rect.top > screen_h and self.vel_y > 0:
            self.vel_y *= -1
            self._randomize_asteroid()

    def _randomize_asteroid(self):
        """Randomly change the asteroid's velocity and rotation"""
        random_x_vel = random_y_vel = self.base_vel * random.uniform(.5, 2)
        random_rotation_vel = self.base_rotation_vel * random.uniform(.5, 2)

        if self.vel_x < 0:
            random_x_vel *= -1
            self.vel_x = random_x_vel

        if self.vel_y < 0:
            random_y_vel *= -1
            self.vel_y = random_y_vel

        self.rotation_vel *= random.choice([-1, 1])
        if self.rotation_vel < 0:
            random_rotation_vel *= -1
            self.rotation_vel = random_rotation_vel

    def _teleport_asteroid(self):
        pass


class FpsDisplay:
    """Class to represent a dynamic FPS counter that can be blitted to the
    screen"""
    def __init__(self, game):
        self.game = game

        self.font = pg.font.Font(game.vars.fps_font, game.vars.fps_size)
        self.color = (5, 255, 30)

        self.image, self.rect = self.get_image()
        # used for self frame-rate limiting
        self.target_fps = game.vars.fps_refresh_rate  # FPS
        self.target_idle = 1000 / self.target_fps  # time is MS to wait
        self.idle_time = 0

    def get_image(self):
        game_fps = self.game.clock.get_fps()
        image = self.font.render(
            f"FPS  {int(game_fps)}", True, self.color
        )
        rect = image.get_rect()
        return image, rect

    def update(self):
        """Update the Surface with the current FPS"""
        if self.idle_time < self.target_idle:  # milliseconds
            self.idle_time += self.game.clock.get_time()
        else:
            self.image, self.rect = self.get_image()
            self.idle_time = 0

    def blitme(self):
        self.game.screen.blit(self.image, self.rect)
