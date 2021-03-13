"""
Module for representing a menu system. The MenuManager class is initiated
in the game's __init__. The MenuManager class works by first initializing
different subclasses of a MenuTemplate abstract class and then displaying
the different menus. MenuTemplate contains methods and classes that are common
to most menus (buttons, text boxes, ...etc.)
"""
import pygame as pg
from pygame.sprite import Sprite, Group
from abc import ABC, abstractmethod


class MenuManager:
    def __init__(self, game):
        self.game = game
        self.vars = game.vars
        self.input_manager = game.input_manager

        # initialize menu screens
        self.main_menu = MainMenu(self)

        # set default menu
        self.curr_menu = self.main_menu

    def update_menu(self):
        for button in self.curr_menu.buttons:
            button.update()

    def draw_menu(self):
        self.curr_menu.blit_menu()


class MenuTemplate(ABC):
    """base class representing methods and attributes common to all menus"""
    @abstractmethod
    def __init__(self, manager):
        self.manager = manager
        self.game = manager.game
        self.vars = manager.vars
        self.input_manager = self.game.input_manager

        self.title = 'template'

        # appearance
        self.bg_rgba = pg.Color(*self.vars.green_rgb, 50)
        self.button_rgb = self.vars.grey_rgb
        self.font = self.vars.menu_font
        self.font_rgb = self.vars.menu_font_rgb

        # initialize background
        self.image = pg.Surface(
            self.game.rect.size, flags=pg.SRCALPHA | pg.HWSURFACE
        )
        self.image.fill(self.bg_rgba)
        self.rect = self.game.rect.copy()

        # a group to hold button sprites
        self.buttons = Group()

    def blit_menu(self):
        """Blit the menu to the game screen"""
        # self.buttons.draw(self.image)
        self.buttons.draw(self.image)
        self.game.screen.blit(self.image, self.rect)

    class Button(Sprite):
        def __init__(self, menu, text, size: tuple, function=None):
            super().__init__()
            # give access to attributes of menu that initialized button
            self.menu = menu
            self.game = menu.game

            # appearance / behavior
            self.function = function
            self.text = text
            self.mouse_over = False

            # create surface
            self.image = pg.Surface(size, flags=pg.SRCALPHA)
            self.rect = self.image.get_rect()
            pg.draw.rect(
                self.image, self.menu.button_rgb, self.rect, border_radius=25
            )

            # render, position, then blit text to button
            text_surf = menu.font.render(text, True, menu.font_rgb)
            text_rect = text_surf.get_rect(center=self.rect.center)
            self.image.blit(text_surf, text_rect)

        def update(self):
            """Update the button's mouseover flag, and, if clicked, do button
            function"""
            mouse_pos = self.menu.input_manager.mouse_pos
            mouse_is_clicking = self.menu.input_manager.is_clicking

            if self.rect.collidepoint(mouse_pos):
                self.mouse_over = True
            else:
                self.mouse_over = False

            if self.mouse_over and mouse_is_clicking:
                try:
                    self.function()
                except TypeError:  # no function assigned
                    pass


class MainMenu(MenuTemplate):
    def __init__(self, manager):
        super().__init__(manager)

        self.add_buttons()

    def add_buttons(self):
        start_button = self.Button(
            self, 'start', (150, 50), self.game.toggle_menu
        )
        start_button.rect.center = self.game.rect.center

        quit_button = self.Button(
            self, 'quit', (150, 50), self.game.quit_game
        )
        quit_button.rect.bottomright = \
            self.game.rect.w - 30, self.game.rect.h - 30

        self.buttons.add(start_button, quit_button)
