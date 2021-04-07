import pygame as pg
from os.path import join
import json
import os

class Scoreboard:
    """Display the current player score and highest leaderboard score at the
    top of the screen"""
    def __init__(self, game):
        self.game = game

        # initialize player score and load leaderboard/highest score
        self.player_score = 0
        self.leaderboard = self.LeaderBoard(game)

        # style info
        self.width = game.rect.w * .25
        self.height = game.rect.h * .08
        self.font = pg.font.Font(join('fonts/', 'arcade.ttf'), 30)
        self.font_color = game.vars.scoreboard_font_rgba
        self.board_rgba = *game.vars.olive_rgb, 128

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

    def draw_self(self):
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
            surf, self.board_rgba, pg.Rect(0, 0, *rect.size),
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

    class LeaderBoard(dict):
        """
        Provides a leaderboard for tracking high scores as well as the
        entered username of the person who scored the high score. Also provides
        a blittable surface that displays the current player score along with
        the top score from the leaderboard.
        """
        def __init__(self, game):
            super().__init__()
            self.game = game

            self.max_length = 1
            # todo add ability to enter initials into the menu module
            self.player_initials = '---'

            # load leaderboard dictionary from JSON
            self.save_path = os.path.join('savedata/', 'high_scores.json')
            self._load()

            # get highest score if there is data in the leaderboard dict
            try:
                self.high_score = max(self.keys())
            except ValueError:  # dict has no keys
                self.high_score = 0

        def update_high_scores(self):
            """
            If the current player score is greater than the minimum score
            on the leaderboard, add the player score onto the leaderboard.
            If the leaderboard is longer than a max length, remove the item
            with the lowest score. sort the leaderboard by descending score
            """
            player_score = self.game.scoreboard.player_score
            lowest_score = min(self.keys())

            # update leaderboard
            def score_qualifies():
                return ( len(self) < self.max_length and player_score > 0 ) or player_score > lowest_score

            if score_qualifies():
                self.update({player_score: self.player_initials})

            # sort self by key (score) in descending order
            sorted_self = sorted(self.items(), reverse=True)
            self.clear()
            self.update(sorted_self)

            # trim lowest scores while max length is exceeded
            while len(self) > self.max_length:
                self.popitem()

            self._save()

        def _load(self) -> None:
            """
            Load the saved JSON  file and update self dictionary with the
            name and score key, value pairs from the JSON dictionary. If no
            saved data is found, create a blank leaderboard JSON file.
            """
            try:
                with open(self.save_path, 'r') as f:
                    # load JSON converting keys (scores) to ints
                    self.update(
                        {int(score): name
                         for score, name in json.load(f).items()}
                    )
            except FileNotFoundError:
                # create a new leaderboard file using empty self
                self._save()

        def _save(self) -> None:
            """
            Save self leaderboard dictionary to json file. If the save
            folder is not found, then create the folder and try again.
            """
            while True:
                try:
                    with open(self.save_path, 'w') as f:
                        json.dump(self, f, indent=4)
                        break
                except FileNotFoundError:  # folder not found, create folder
                    os.mkdir(os.path.split(self.save_path)[0])


class FpsDisplay:
    """
    Class to represent a dynamic FPS counter that can be blitted to the
    screen
    """
    def __init__(self, game):
        self.game = game

        # style
        self.font = self.game.vars.fps_font
        self.font_rgb = self.game.vars.fps_font_rgb

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

    def draw_fps(self):
        self.game.screen.blit(self.image, self.rect)

    def _get_font_surface(self):
        """
        Get the current FPS and render it as a font render surface, return
        the surface and it's rect
        """
        font_surface = self.font.render(
            f"FPS  {int(self.game.clock.get_fps())}", True, self.font_rgb
        ).convert_alpha()
        rect = font_surface.get_rect()
        return font_surface, rect
