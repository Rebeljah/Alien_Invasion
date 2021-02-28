import pygame as pg
from pygame.sprite import Sprite
import random as r

from settings import scale


class AsteroidGroup(pg.sprite.Group):
    """A group class for creating and managing asteroids"""
    def __init__(self, game, num_asteroids=1):
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
    Simulate a big'ol asteroid that bounces all over the screen like one
    of those 90's DVD screensavers.
    """
    def __init__(self, game, image, rect):
        super().__init__()
        # get game info
        self.game = game
        self.vars = game.vars

        self.image = image
        self.rect = rect
        # applied each time rotozoom is called in _spin()
        self.unique_scale = 1
        # used for resetting image between rotations in _spin()
        self.image_mem = self.image

        # rotation info
        self.base_rotation_vel = self.vars.asteroid_rps
        self.rotation_vel = self.base_rotation_vel
        self.degree = 0.0

        # Get base velocity then set x and y vel
        self.base_vel = self.vars.asteroid_velocity
        self.vel_x = self.vel_y = self.base_vel

        # track location by float for better accuracy
        self.centerx, self.centery = map(float, self.rect.center)

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
                self.image_mem, self.degree, self.unique_scale
            )
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
            self._randomize_asteroid()
            self._teleport_asteroid()
        elif self.rect.left > screen_w and self.vel_x > 0:
            self._randomize_asteroid()
            self._teleport_asteroid()

        # check top / bottom exit
        elif self.rect.bottom < 0 and self.vel_y < 0:
            self._randomize_asteroid()
            self._teleport_asteroid()
        elif self.rect.top > screen_h and self.vel_y > 0:
            self._randomize_asteroid()
            self._teleport_asteroid()

    def _randomize_asteroid(self):
        """Randomly change the asteroid's velocity and rotation.
        - Currently preserves direction of movement velocity"""
        random_vel_x = self.base_vel * r.uniform(.5, 2)
        if self.vel_x < 0:
            random_vel_x *= -1
        self.vel_x = random_vel_x

        random_vel_y = self.base_vel * r.uniform(.5, 2)
        if self.vel_y < 0:
            random_vel_y *= -1
        self.vel_y = random_vel_y

        # randomize the direction and speed of spin
        self.rotation_vel = \
            self.base_rotation_vel * r.uniform(.5, 2) * r.choice([1, -1])

        # randomize rotozoom scale
        self.unique_scale = r.uniform(.25, 1.25)

    def _teleport_asteroid(self):
        self.rect.center = r.choice([
            (-100, -100), (self.game.rect.w+100, -100),
            (-100, self.game.rect.h+100),
            (self.game.rect.w+100, self.game.rect.h+100)
        ])
        self.centerx, self.centery = map(float, self.rect.center)

        # turn the asteroid the correct way to re-enter the screen
        if self.rect.bottom < 0 and self.vel_y < 0:
            self.vel_y *= -1
        elif self.rect.top > self.game.rect.bottom and self.vel_y > 0:
            self.vel_y *= -1
        if self.rect.right < 0 and self.vel_x < 0:
            self.vel_x *= -1
        elif self.rect.left > self.game.rect.right and self.vel_x > 0:
            self.vel_x *= -1


class FpsDisplay:
    """Class to represent a dynamic FPS counter that can be blitted to the
    screen"""
    def __init__(self, game):
        self.game = game

        self.font = pg.font.Font(game.vars.fps_font, game.vars.fps_size)
        self.color = (5, 255, 30)

        self.image, self.rect = self._get_image()
        # used for self frame-rate limiting
        self.target_fps = game.vars.fps_refresh_rate  # FPS
        self.target_idle = 1000 / self.target_fps  # time is MS to wait
        self.idle_time = 0

    def update(self):
        """Update the Surface with the current FPS"""
        if self.idle_time < self.target_idle:  # milliseconds
            self.idle_time += self.game.clock.get_time()
        else:
            self.image, self.rect = self._get_image()
            self.idle_time = 0

    def _get_image(self):
        current_fps = self.game.clock.get_fps()
        surface = self.font.render(
            f"FPS  {int(current_fps)}", True, self.color
        )
        rect = surface.get_rect()
        return surface, rect

    def blitme(self):
        self.game.screen.blit(self.image, self.rect)
