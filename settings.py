"""A module to hold the settings for the Alien Invasion game"""
import pygame as pg
from pygame.color import Color
from pygame.font import Font
from os.path import join


class Vars:
    def __init__(self):
        """initialize the game's settings. The idea to use a settings class
        comes from Python Crash Course"""

        # Get user's display size
        display_info = pg.display.Info()
        display_w = display_info.current_w
        display_h = display_info.current_h

        # Screen settings
        self.max_fps = 144
        self.window_w = int(.75 * display_w)
        self.window_h = int(.90 * display_h)

        # Universal color settings
        self.black_rgb = 0, 0, 0
        self.grey_rgb = 89, 89, 89
        self.yellow_rgb = 255, 255, 0
        self.green_rgb = 0, 255, 0
        self.light_blue_rgb = 51, 204, 255

        # Menu Settings
        self.menu_bg_rgb = self.black_rgb
        self.menu_font = Font(join('fonts/', 'arcade.ttf'), 35)
        self.menu_font_rgb = self.black_rgb

        # Control settings
        self.key_move_r = pg.K_d
        self.key_move_l = pg.K_a
        self.key_shoot = pg.K_SPACE
        self.key_quit = pg.K_q
        self.key_menu = pg.K_ESCAPE

        # Ship settings
        self.ship_scale = 0.11
        self.ship_speed = 0.50 * self.window_w  # pixels-per-second

        # Bullet settings
        self.bullet_speed = 0.80 * self.window_h  # pixels-per-second
        self.max_bullets = 3
        self.bullets_persist = True
        self.bullet_w = 0.09 * self.window_w  # 0.003 * self.window_w
        self.bullet_h = 0.028 * self.window_h
        self.bullet_color = self.light_blue_rgb

        # Alien settings
        self.fleet_columns = 5
        self.fleet_rows = 2
        self.alien_scale = .060  # percent of screen height
        self.alien_vel_x = 0.21 * self.window_w
        self.fleet_drop_height = 0.05 * self.window_h

        # FPS display
        self.show_fps = True
        self.fps_refresh_rate = 3  # measured in... FPS
        self.fps_font = Font(join('fonts/', 'arcade.ttf'), 22)
        self.fps_font_rgb = self.yellow_rgb

        # Scoreboard
        self.scoreboard_font_rgba = Color(*self.yellow_rgb, 100)
        self.scoreboard_rgba = Color(*self.green_rgb, 50)

        # Asteroid settings
        self.num_asteroids = 2
        self.asteroid_scale = 0.14
        self.asteroid_rps = 45  # degrees-per-second
        self.asteroid_velocity = .08 * self.window_w  # pixels-per-second


def scale(child_surface, comparison_surface, ratio):
    """
    Scale a surface based on a percentage of the height of a comparison
    surface. Preserves aspect ratio of the child. Returns the scaled surface and
    its rectangle
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
