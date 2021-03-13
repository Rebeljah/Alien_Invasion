import pygame as pg
from pygame.sprite import Sprite, Group
import random as rand
import os

from settings import scale


class AsteroidGroup(Group):
    """A group class for creating and managing asteroids"""
    def __init__(self, game):
        super().__init__()
        self.game = game

        self.image_pool = []
        self.image_folder = os.path.join('images/', 'asteroids/')
        self._load_images()

        self.num_asteroids = game.vars.num_asteroids
        self._build_self()

    def _load_images(self):
        """
        Load then scale each image in the asteroid image folder into the
        group's image list as a tuple containing the surface and rect of each
        image.
        """
        self.image_pool: list = [
            pg.image.load(self.image_folder + file_name).convert_alpha()
            for file_name in os.listdir(self.image_folder)
        ]
        # scale each loaded surface and also return a rect for each surface
        # asteroid_images = [(Surface, Rect), ...]
        for i, image in enumerate(self.image_pool):
            self.image_pool[i]: tuple = scale(
                image, self.game.screen, self.game.vars.asteroid_scale
            )

    def get_random_image(self) -> tuple:
        """Return the surface and rectangle of a random asteroid image"""
        return rand.choice(self.image_pool)

    def _build_self(self):
        """
        Initialize and add each asteroid to the group using a random image for
        each asteroid.
        """
        self.add(*[
            Asteroid(self)
            for _ in range(self.num_asteroids)
        ])


class Asteroid(Sprite):
    """
    An asteroid that randomly changes location image, size, and velocity.
    Gives the appearance of multiple asteroids entering and exiting the screen
    """
    def __init__(self, fleet):
        super().__init__()
        # get game info
        self.fleet = fleet
        self.game = fleet.game
        self.vars = fleet.game.vars

        # default x and y velocity
        self.vel_x = self.vel_y = self.base_vel = self.vars.asteroid_velocity

        self.image, self.rect = self.fleet.get_random_image()
        self.rect.center = self._random_location()

        # rotation info
        self.degree = 0.0
        self.rotation_vel = self.base_rotation_vel = self.vars.asteroid_rps
        # applied each time rotozoom is called in _spin()
        self.scale = 1
        # used for resetting image between rotations in _spin()
        self.base_img = self.image

        # track location by float for better accuracy
        self.centerx, self.centery = map(float, self.rect.center)

    def update(self, dt):
        """
        Handles the rotation and movement of the asteroid
        """
        self._check_screen_exit()
        self._spin(dt)
        # move the asteroid by its velocity in pixels per second
        self.centerx += self.vel_x * dt
        self.centery += self.vel_y * dt
        self.rect.centerx = self.centerx
        self.rect.centery = self.centery

    def _spin(self, dt):
        """
        Using a copy of the asteroid image created at init, rotate the original
        image surface to the the current degree of the asteroid object.
        -Assign the rotated image to self.image
        This method is needed as images tend to get corrupted over multiple
        rotations. Rotozoom is used here as well to size the asteroid to it's
        current scale.
        """
        # increment spin
        self.degree += self.rotation_vel * dt

        self.image = pg.transform.rotozoom(
            self.base_img, self.degree, self.scale
        )
        # preserve the center of the rectangle to produce smooth movement.
        self.rect = self.image.get_rect(center=self.rect.center)

    def _check_screen_exit(self) -> None:
        """
        When the asteroid leaves the screen, randomly amplify it's velocities,
        randomly amplify it's size, move it to another part of the screen.
        """

        # return None if the asteroid is still in the screen
        if self.rect.colliderect(self.game.rect):
            return None

        screen_w = self.game.rect.width
        screen_h = self.game.rect.height

        # check that the asteroid is actually heading away from the screen
        if any([
            self.rect.right < 0 and self.vel_x < 0,
            self.rect.left > screen_w and self.vel_x > 0,
            self.rect.bottom < 0 and self.vel_y < 0,
            self.rect.top > screen_h and self.vel_y > 0
        ]):
            self.degree = 0
            self._randomize_asteroid()
            self._teleport_asteroid()

            # todo
            # self._adjust_brightness()

    def _randomize_asteroid(self):
        """Randomly change the asteroid's velocity and rotation and image"""
        def randomize(vel):
            return vel * rand.choice([1, -1]) * rand.uniform(.5, 2)
        # randomly choose an image
        self.base_img, self.rect = self.fleet.get_random_image()
        # randomize size
        self.scale = rand.uniform(.25, 1.25)
        # randomize velocities
        self.vel_x = randomize(self.base_vel)
        self.vel_y = randomize(self.base_vel)
        self.rotation_vel = randomize(self.base_rotation_vel)

    def _teleport_asteroid(self):
        """
        Move the asteroid to a random location outside of the screen and
        make sure it is going in the right direction (towards the visible area)
        """
        # move the rect off-screen, then update accurate position
        self.rect.center = self._random_location()
        self.centerx, self.centery = map(float, self.rect.center)

        # invert velocity as needed to make the asteroid move into the screen
        if any([self.rect.bottom < 0 and self.vel_y < 0,
                self.rect.top > self.game.rect.bottom and self.vel_y > 0
                ]):
            self.vel_x *= -1

        if any([self.rect.right < 0 and self.vel_x < 0,
                self.rect.left > self.game.rect.right and self.vel_x > 0
                ]):
            self.vel_y *= -1

    def _random_location(self, reentry_time=1.0):
        """
        Returns a random coordinate position outside of the visible
        screen.

        reentry_time: [int, float] -  Seconds it will take for the asteroid to
                     re-enter visible area.
        """
        g_rect = self.game.rect
        # approximate distance away from visible part of display in seconds
        dist = reentry_time * abs(self.vel_x)

        return rand.choice(
            ((-dist, -dist), (g_rect.centerx, -dist), (g_rect.w+dist, -dist),
             (-dist, g_rect.centery), (-dist, g_rect.h+dist),
             (g_rect.centerx, g_rect.h+dist), (g_rect.w+dist, g_rect.h+dist))
        )

    # todo
    def _adjust_brightness(self):
        """
        shade the asteroid based on its size to create an effect of depth
        to screen.
        """
        print('adjust brightness')
