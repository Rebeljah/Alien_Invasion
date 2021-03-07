"""A module to hold the settings for the Alien Invasion game"""
import pygame as pg


class Vars:
    def __init__(self):
        """initialize the game's settings"""

        # get user's display size
        self.display_info = pg.display.Info()
        display_w = self.display_info.current_w
        display_h = self.display_info.current_h

        # screen settings
        self.max_fps = 144
        self.window_w = int(.75 * display_w)
        self.window_h = int(.90 * display_h)

        # FPS display
        self.show_fps = True
        self.fps_refresh_rate = 3  # measured in... FPS
        self.fps_font = 'fonts/arcade.ttf'
        self.fps_size = 22

        # Scoreboard
        self.scoreboard_font_rgba = (255, 255, 0, 100)  # yellow
        self.scoreboard_rgba = (0, 255, 0, 50)  # green

        # control settings
        self.key_r = pg.K_d
        self.key_l = pg.K_a
        self.key_shoot = pg.K_SPACE
        self.key_quit = pg.K_q

        # Alien settings
        self.fleet_columns = 8
        self.fleet_rows = 8
        self.alien_scale = .060  # percent of screen height
        self.alien_vel_x = 0.21 * self.window_w
        self.fleet_drop_height = 0.05 * self.window_h

        # ship settings
        self.ship_scale = 0.11
        self.ship_speed = 0.45 * self.window_w  # pixels-per-second

        # bullet settings
        self.bullet_speed = 0.80 * self.window_h  # pixels-per-second
        self.max_bullets = 3
        self.bullets_persist = True
        self.bullet_w = 0.09 * self.window_w  # 0.003 * self.window_w
        self.bullet_h = 0.028 * self.window_h
        self.bullet_color = (51, 204, 255)  # light blue

        # asteroid settings
        self.num_asteroids = 3
        self.asteroid_scale = 0.14
        self.asteroid_rps = 45  # degrees-per-second
        self.asteroid_velocity = .08 * self.window_w  # pixels-per-second


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
