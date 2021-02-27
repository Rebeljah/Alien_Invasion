"""A module to hold the settings for the Alien Invasion game"""
import pygame as pg


def scale_speed(percentage, length):
    """
    Return a speed in pixels-per-second that is a certain percentage of
    the given length
    """

    return percentage * length


def scale(child_surface, comparison_surface, ratio):
    """
    Scale a surface based on a percentage of the height of a comparison
    surface. Preserves aspect ratio of the child.
    """

    child_rect = child_surface.get_rect()
    child_ratio = child_rect.width / child_rect.height

    # this is the value that the rectangle will be scaled to
    comparison_height = comparison_surface.get_height()
    # scale child rectangle
    child_rect.height = ratio * comparison_height
    child_rect.width = child_ratio * child_rect.height

    # resize the child surface to its' scaled rectangle
    child_surface = \
        pg.transform.scale(child_surface, child_rect.size)

    return child_surface, child_rect


class Vars:
    def __init__(self):
        """initialize the game's settings"""

        # get user display size
        self.display_info = pg.display.Info()
        display_w = self.display_info.current_w
        display_h = self.display_info.current_h

        # screen settings
        self.max_fps = 120
        self.window_w = int(.75 * display_w)
        self.window_h = int(.9 * display_h)

        # FPS display
        self.show_fps = True
        self.fps_refresh_rate = 3  # measured in... FPS
        self.fps_font = 'fonts/arcade.ttf'
        self.fps_size = 22

        # control settings
        self.key_r = pg.K_d
        self.key_l = pg.K_a
        self.key_shoot = pg.K_SPACE
        self.key_quit = pg.K_q

        # Alien settings
        self.fleet_columns = 4
        self.fleet_rows = 3
        self.alien_scale = .060  # percent of screen height
        self.alien_vel_x = 0.10 * self.window_w
        self.fleet_drop_height = 0.08 * self.window_h

        # ship settings
        self.ship_scale = 0.13
        self.ship_speed = 0.75 * self.window_w  # pixels-per-second

        # bullet settings
        self.bullet_speed = 1.0 * self.window_h  # pixels-per-second
        self.max_bullets = 3
        self.bullets_persist = False
        self.bullet_w = 0.004 * self.window_w
        self.bullet_h = 0.04 * self.window_h
        self.bullet_color = (51, 204, 255)  # light blue

        # asteroid settings
        self.asteroid_scale = 0.14
        self.asteroid_rps = 45  # degrees-per-second
        self.asteroid_velocity = 0.1 * self.window_w  # pixels-per-second
