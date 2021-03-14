"""Provides a leaderboard for tracking the top 10 high scores as well as the
entered username of the person who scored the high score. Also provides
a blittable surface that displays the current player score along with
the top score from the leaderboard."""

import json
import os


class LeaderBoard(dict):
    """
    Handle loading and editing of the saved leaderboard data. Extends
    dict.
    """
    def __init__(self, game):
        super().__init__()
        self.game = game

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
        If the leaderboard is longer than 10 items, remove the item
        with the lowest score. sort the leaderboard by descending score
        """
        player_score = self.game.scoreboard.player_score

        # update leaderboard
        if len(self) < 10 or player_score > min(self.keys()):
            if player_score > 0:
                self.update({player_score: self.player_initials})

        # trim lowest score
        if len(self) > 10:
            del self[min(self.keys())]

        # sort self by key (score) in descending order
        sorted_self = sorted(self.items(), reverse=True)
        self.clear()
        self.update(sorted_self)

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
        """Save self leaderboard dictionary to json file. If the save folder
        is not found, then create the folder and try again."""
        while True:
            try:
                with open(self.save_path, 'w') as f:
                    json.dump(self, f, indent=4)
                    break
            except FileNotFoundError:  # folder not found, create folder
                os.mkdir(os.path.split(self.save_path)[0])
