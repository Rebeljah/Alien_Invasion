"""Contains classes for HUD overlays, menus, etc..."""

import pygame as pg
import json
import os


class FpsDisplay:
    """Class to represent a dynamic FPS counter that can be blitted to the
    screen"""
    def __init__(self, game):
        self.game = game

        self.font = pg.font.Font(game.vars.fps_font, game.vars.fps_size)
        self.color = (255, 255, 0, 100)  # yellow

        self.image, self.rect = self._get_font_surface()
        # used for self frame-rate limiting
        self.target_fps = game.vars.fps_refresh_rate  # FPS
        self.target_idle = 1000 / self.target_fps  # time is MS to wait
        self.idle_time = 0

    def update(self):
        """Update the Surface with the current FPS"""
        if self.idle_time > self.target_idle:  # milliseconds
            self.idle_time = 0
            self.image, self.rect = self._get_font_surface()
        else:
            self.idle_time += self.game.clock.get_time()

    def _get_font_surface(self):
        current_fps = self.game.clock.get_fps()
        font_surface = self.font.render(
            f"FPS  {int(current_fps)}", True, self.color
        )
        rect = font_surface.get_rect()
        return font_surface, rect

    def blit_self(self):
        self.game.screen.blit(self.image, self.rect)


class Scoreboard:
    """Display the current player score and highest leaderboard score at the
    top of the screen"""
    def __init__(self, game):
        self.game = game

        # initialize player score and load leaderboard/highest score
        self.player_score = 0
        self.leaderboard = self.LeaderBoard(game)

        # style info
        self.font = pg.font.Font('fonts/arcade.ttf', 30)
        self.font_rgba = game.vars.scoreboard_font_rgba
        self.board_rgba = game.vars.scoreboard_rgba

        # initialize surfaces
        self._render_board()
        self._render_player_score()
        self._render_highest_score()

        # key points for positioning text elements
        self.centery = self.board_rect.centery
        self.right_centerx = self.board_rect.right - self.board_rect.w * .25
        self.left_centerx = self.board_rect.left + self.board_rect.w * .25

        # position score surface rectangles for blitting
        self.p_score_rect = self.p_score_surf.get_rect(
            center=(self.left_centerx, self.centery)
        )
        self.h_score_rect = self.h_score_surf.get_rect(
            center=(self.right_centerx, self.centery)
        )

    def update(self):
        """Update the player score surface on each loop"""
        self._render_player_score()

    def blit_self(self):
        """Bulk blit each individual surface of the board to the screen"""
        self.game.screen.blits((
            (self.board_surf, self.board_rect),
            (self.p_score_surf, self.p_score_rect),
            (self.h_score_surf, self.h_score_rect)
        ))

    def _render_board(self):
        """Returns a board surface that will be blitted underneath scores"""
        self.board_surf = pg.surface.Surface(
            (self.game.rect.w * .15, self.game.rect.h * .08), flags=pg.SRCALPHA
        )
        self.board_rect = self.board_surf.get_rect()
        # draw rounded board background
        pg.draw.rect(
            self.board_surf, self.board_rgba, self.board_rect,
            border_radius=25
        )
        offset = self.game.rect.h * 0.03
        self.board_rect.topright = (self.game.rect.w - offset, +offset)

    def _render_highest_score(self):
        """
        Update the scoreboard with the score of the current top leader
        in the leaderboard dict. The dict is sorted by highest score (value).)
        """
        # get the score value of highest (first) item in the leaderboard
        self.h_score_surf = self.font.render(
            str(self.leaderboard.high_score), True, self.font_rgba
        )

    def _render_player_score(self):
        """Update the player score surface and rect"""
        self.p_score_surf = self.font.render(
            str(self.player_score), True, self.font_rgba
        )

    class LeaderBoard(dict):
        """
        Handle loading and editing of the saved leaderboard data. Extends
        dict.
        """
        def __init__(self, game):
            super().__init__()
            self.game = game

            # load leaderboard dictionary from JSON
            self.save_path = os.path.join('savedata/', 'high_scores.json')
            self.load_leaderboard()

            if self:
                self.high_score = max(self.keys())
            else:
                self.high_score = 0

        def load_leaderboard(self) -> None:
            """
            Load the saved JSON  file and update self dictionary with the
            name and score key, value pairs from the JSON dictionary. If no
            saved data is found, create a blank leaderboard JSON file.
            """
            try:
                with open(self.save_path, 'r') as f:
                    # load JSON converting keys (scores) to ints
                    self.update({
                        int(score): name
                        for score, name in json.load(f).items()
                    })
            except FileNotFoundError:
                self.save_leaderboard()

        def save_leaderboard(self) -> None:
            """Save self leaderboard dictionary to json file. If the save folder
            is not found, then create the folder and try again."""
            while True:
                try:
                    with open(self.save_path, 'w') as f:
                        json.dump(self, f, indent=4)
                        break

                except FileNotFoundError:
                    os.mkdir(os.path.split(self.save_path)[0])

        def update_leaderboard(self):
            """
            If the current player score is greater than the minimum score
            on the leaderboard, add the player score onto the leaderboard.
            If the leaderboard is longer than 10 items, remove the item
            with the lowest score. sort the leaderboard by descending score
            """
            player_score = self.game.scoreboard.player_score
            initials = 'JAH'

            # add player score/name if greater than lowest score in leaderboard
            # or if leaderboard hs less than 10 scores on it
            if len(self) < 10 or player_score > min(self.keys()):
                if player_score > 0:
                    self.update({player_score: initials})

            if len(self) > 10:
                del self[min(self.keys())]

            """# sort self by key (score) in descending order
            sorted_self = dict(sorted(self.items(), reverse=True))
            self.clear()
            self.update(sorted_self)"""

            self.save_leaderboard()
