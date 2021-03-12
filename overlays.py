import pygame as pg
from os.path import join

import leaderboard


class Scoreboard:
    """Display the current player score and highest leaderboard score at the
    top of the screen"""
    def __init__(self, game):
        self.game = game

        # initialize player score and load leaderboard/highest score
        self.player_score = 0
        self.leaderboard = leaderboard.LeaderBoard(game)

        # style info
        self.width = game.rect.w * .25
        self.height = game.rect.h * .08
        self.font = pg.font.Font(join('fonts/', 'arcade.ttf'), 30)
        self.font_color = game.vars.scoreboard_font_rgba
        self.board_color = game.vars.scoreboard_rgba

        # Important points for blitting onto the scoreboard
        self.centery = self.height // 2
        self.board_l_centerx = 0 + self.width * .25
        self.board_r_centerx = self.width - self.width * .25

        # initialize surfaces and rects for elements that don't change
        self.rendered_scoreboard: tuple = self._render_board()
        self.rendered_high_score: tuple = self._render_high_score()

        # image is built in update()
        self.image = None
        self.rect = self.rendered_scoreboard[1]

    def update(self):
        """
        Reset the scoreboard surface and then blit text onto the scoreboard.
        Only the player score is rendered on each frame, board and high score
        are rendered at init.
        """
        self.image = self.rendered_scoreboard[0].copy()
        self.image.blits([
            self.rendered_high_score,
            self._render_player_score()
        ])

    def blit_self(self):
        """blit scoreboard to the screen"""
        self.game.screen.blit(self.image, self.rect)

    def _render_board(self):
        """
        Returns a board surface and rect that will be blitted to the game
        screen. This is the surface that the score font render surfaces
        are blitted onto.
        """
        edge_offset = self.game.rect.h * 0.03
        surf = pg.surface.Surface(
            (self.width, self.height),  flags=pg.SRCALPHA
        )
        rect = surf.get_rect(
            topright=(self.game.rect.w - edge_offset, edge_offset)
        )
        # draw rounded rectangle background
        pg.draw.rect(
            surf, self.board_color, pg.Rect(0, 0, *rect.size),
            border_radius=25
        )

        return surf, rect

    def _render_high_score(self):
        """
        Render current high score and return its surface and rect
        """
        surf = self.font.render(
            str(self.leaderboard.high_score), True, self.font_color
        )
        rect = surf.get_rect(
            center=(self.board_r_centerx, self.centery)
        )

        return surf, rect

    def _render_player_score(self) -> tuple:
        """
        Render current player score and return its surface and rect
        """
        surf = self.font.render(
            str(self.player_score), True, self.font_color
        )
        rect = surf.get_rect(
            center=(self.board_l_centerx, self.centery)
        )

        return surf, rect


class FpsDisplay:
    """Class to represent a dynamic FPS counter that can be blitted to the
    screen"""
    def __init__(self, game):
        self.game = game

        # style
        self.font = pg.font.Font(game.vars.fps_font, game.vars.fps_size)
        self.color_rgb = self.game.vars.yellow_rgb

        self.image, self.rect = self._get_font_surface()
        # used for self frame-rate limiting
        target_fps = game.vars.fps_refresh_rate
        self.target_idle = 1000 / target_fps  # time is MS to wait
        self.idle_time = 0

    def update(self):
        """Update the Surface with the current FPS"""
        if self.idle_time < self.target_idle:  # milliseconds
            self.idle_time += self.game.clock.get_time()
        else:
            self.idle_time = 0
            self.image, self.rect = self._get_font_surface()

    def blit_self(self):
        self.game.screen.blit(self.image, self.rect)

    def _get_font_surface(self):
        current_fps = self.game.clock.get_fps()
        font_surface = self.font.render(
            f"FPS  {int(current_fps)}", True, self.color_rgb
        ).convert_alpha()
        rect = font_surface.get_rect()
        return font_surface, rect
