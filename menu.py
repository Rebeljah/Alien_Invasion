"""
Module for representing a menu system. The MenuManager class is initiated
in the game's __init__. The MenuManager class works by first initializing
different subclasses of a MenuTemplate abstract class and then displaying
the different menus. MenuTemplate contains methods and classes that are common
to most menus (buttons, text boxes, ...etc.)
"""
import pygame as pg
from abc import ABC, abstractmethod


class MenuManager:
    def __init__(self, game):
        self.game = game
        self.vars = game.vars

        self.menus = [
            MainMenu(self)
        ]

    def check_menu_events(self):
        pass

    def update_menu(self):
        pass

    def draw_menu(self):
        pass


class MenuTemplate(ABC):
    """base class representing methods and attributes common to all menus"""
    @abstractmethod
    def __init__(self, manager):
        self.game = manager.game
        self.vars = manager.vars

    class Button:
        pass


class MainMenu(MenuTemplate):
    def __init__(self, manager):
        super().__init__(manager)
        self.x = 2
