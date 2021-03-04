import pygame as pg
from pygame.sprite import Sprite
import random as rand

from settings import scale


class AsteroidGroup(pg.sprite.Group):
    """A group class for creating and managing asteroids"""
    def __init__(self, game, num_asteroids):
        super().__init__()

        image = pg.image.load('images/asteroid.bmp').convert_alpha()
        image, rect = scale(
            image, game.screen, game.vars.asteroid_scale
        )
        self.add(*[
            Asteroid(game, image, rect) for _ in range(num_asteroids)
        ])


class Asteroid(Sprite):
    """
    An asteroid that randomly changes location size and shape. Gives the
    appearance of mutiple asteroids entering and exiting the screen
    """
    def __init__(self, game, image, rect):
        super().__init__()
        # get game info
        self.game = game
        self.vars = game.vars
        # default x and y velocity
        self.vel_x = self.vel_y = self.base_vel = self.vars.asteroid_velocity

        # load image and rect
        self.image = image
        self.rect = rect
        self.rect.center = self._random_location(3)

        # rotation info
        self.degree = 0.0
        self.base_rotation_vel = self.vars.asteroid_rps
        self.rotation_vel = self.base_rotation_vel
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
        self.degree += self.rotation_vel * dt
        # reset the angle after 360 degrees to save memory
        if -360 < self.degree < 360:
            self.image = pg.transform.rotozoom(
                self.base_img, self.degree, self.scale
            )
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.degree = 0

    def _check_screen_exit(self):
        """
        When the asteroid leaves the screen, randomly amplify it's velocities,
        randomly amplify it's size, move it to another part of the screen.
        """
        def randomize():
            self._randomize_asteroid()
            self._teleport_asteroid()

        screen_w = self.game.rect.width
        screen_h = self.game.rect.height

        # check left / right exit
        if self.rect.right < 0 and self.vel_x < 0:
            randomize()
        elif self.rect.left > screen_w and self.vel_x > 0:
            randomize()

        # check top / bottom exit
        elif self.rect.bottom < 0 and self.vel_y < 0:
            randomize()
        elif self.rect.top > screen_h and self.vel_y > 0:
            randomize()

    def _randomize_asteroid(self):
        """Randomly change the asteroid's velocity and rotation."""
        def randomize(vel, amplitude=1.2):
            return vel * rand.choice([1, -1]) * rand.uniform(.5, 2) * amplitude

        self.vel_x = randomize(self.base_vel)
        self.vel_y = randomize(self.base_vel)
        # randomize the direction / speed of rotation
        self.rotation_vel = randomize(self.base_rotation_vel)
        # randomize rotozoom scale
        self.scale = rand.uniform(.25, 1.25)

    def _teleport_asteroid(self):
        """
        Move the asteroid to a random location outside of the screen and
        make sure it is going in the right direction (towards the visible area)
        """
        # move the rect off-screen, then update float center positions
        self.rect.center = self._random_location(3)
        self.centerx, self.centery = map(float, self.rect.center)

        # invert velocity as needed to make the asteroid move into the screen
        if self.rect.bottom < 0 and self.vel_y < 0:
            self.vel_y *= -1
        elif self.rect.top > self.game.rect.bottom and self.vel_y > 0:
            self.vel_y *= -1
        if self.rect.right < 0 and self.vel_x < 0:
            self.vel_x *= -1
        elif self.rect.left > self.game.rect.right and self.vel_x > 0:
            self.vel_x *= -1

    def _random_location(self, travel_time=2):
        """
        Returns a random coordinate position outside of the visible
        screen.

        travel_time: [int, float] -  Seconds it will take for the asteroid to
                     re-enter visible area.
        """
        g_rect = self.game.rect
        # distance away from visible part of display in seconds
        dist = travel_time * abs(self.vel_x)

        return rand.choice(
            ((-dist, -dist), (g_rect.centerx, -dist), (g_rect.w+dist, -dist),
             (-dist, g_rect.centery), (-dist, g_rect.h+dist),
             (g_rect.centerx, g_rect.h+dist), (g_rect.w+dist, g_rect.h+dist))
        )


class FpsDisplay:
    """Class to represent a dynamic FPS counter that can be blitted to the
    screen"""
    def __init__(self, game):
        self.game = game

        self.font = pg.font.Font(game.vars.fps_font, game.vars.fps_size)
        self.color = (5, 255, 30)

        self.image, self.rect = self._get_font_surface()
        # used for self frame-rate limiting
        self.target_fps = game.vars.fps_refresh_rate  # FPS
        self.target_idle = 1000 / self.target_fps  # time is MS to wait
        self.idle_time = 0

    def update(self):
        """Update the Surface with the current FPS"""
        if self.idle_time < self.target_idle:  # milliseconds
            self.idle_time += self.game.clock.get_time()
        else:
            self.image, self.rect = self._get_font_surface()
            self.idle_time = 0

    def _get_font_surface(self):
        current_fps = self.game.clock.get_fps()
        font_surface = self.font.render(
            f"FPS  {int(current_fps)}", True, self.color
        )
        rect = font_surface.get_rect()
        return font_surface, rect

    def blit_self(self):
        self.game.screen.blit(self.image, self.rect)