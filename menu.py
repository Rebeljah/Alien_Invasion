"""
Module for representing a menu system. The MenuManager class is initiated
in the game's __init__. The MenuManager class works by first initializing
different subclasses of a MenuTemplate abstract class and then displaying
the different menus. MenuTemplate contains methods and classes that are common
to most menus (buttons, text boxes, ...etc.)
"""
import pygame as pg
from pygame.sprite import Sprite, Group
from pygame.rect import Rect


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
        self.curr_menu.update()

    def draw_menu(self):
        self.curr_menu.blit_menu()


class MenuTemplate:
    """base class representing methods and attributes common to all menus"""
    def __init__(self, manager):
        self.manager = manager
        self.game = manager.game
        self.vars = manager.vars
        self.input_manager = self.game.input_manager

        self.title = 'template'

        # appearance
        self.bg_rgba = pg.Color(*self.vars.light_blue_rgb, 50)

        self.button_rgb = self.vars.olive_rgb
        self.button_hover_rgba = (*self.vars.black_rgb, 100)
        self.button_border_rgb = self.vars.black_rgb

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

        self.menu_areas = []
        self._create_menu_areas()

    def _create_menu_areas(self):
        margin = self.rect.w * 0.02

        # Top center
        self.top_center_group = self.MenuArea(
            (self.game.rect.w * .50, self.game.rect.h * .02)
        )
        self.top_center_group.rect.midtop = self.rect.midtop
        self.menu_areas.append(self.top_center_group)

        # Center
        self.center_group = self.MenuArea(
            (self.game.rect.w * .30, self.game.rect.h * .5)
        )
        self.center_group.rect.center = self.game.rect.center
        self.menu_areas.append(self.center_group)

        # Bottom left
        self.bottom_l_group = self.MenuArea(
            (self.game.rect.w * .15, self.game.rect.h * .2)
        )
        self.bottom_l_group.rect.bottomleft = self.game.rect.bottomleft
        self.bottom_l_group.rect.left += margin
        self.bottom_l_group.rect.bottom -= margin
        self.menu_areas.append(self.bottom_l_group)

        # Bottom right
        self.bottom_r_group = self.MenuArea(
            (self.game.rect.w * .15, self.game.rect.h * .2)
        )
        self.bottom_r_group.rect.bottomright = self.game.rect.bottomright
        self.bottom_r_group.rect.right -= margin
        self.bottom_r_group.rect.bottom -= margin
        self.menu_areas.append(self.bottom_r_group)

    def add_buttons(self):
        """
        Initialize buttons. You can show the formatting areas by pressing
        the debug key while on the menu
        """
        pass

    def update(self):
        for area in self.menu_areas:
            area.update()

    def blit_menu(self):
        """Blit the menu to the game screen"""
        if self.game.debug:
            pg.draw.rect(self.game.screen, (0,0,0), self.center_group.rect)
            pg.draw.rect(self.game.screen, (0,0,0), self.bottom_l_group.rect)
            pg.draw.rect(self.game.screen, (0,0,0), self.bottom_r_group.rect)

        for area in self.menu_areas:
            area.draw(self.image)

        self.game.screen.blit(self.image, self.rect)

    class MenuArea(Group):
        """
        An object that can be be used to group sprites together and position them
        within a rectangle on the menu. The rectangle is initiated with a size
        parameter, which should be a tuple containing width and height values.
        """

        def __init__(self, size, *sprites):
            Group.__init__(self, *sprites)

            self.rect = pg.Rect(0, 0, *size)

            self.scale_sprites()
            self.space_sprites()

        # todo
        def scale_sprites(self):
            """
            Scale each member sprite's width to fill the width of the MenuArea.
            Preserves the ratio of width to height when transforming each sprite.
            """
            pass

        # todo
        def space_sprites(self):
            """
            Space the sprites in the MenuArea so that they are evenly spread across
            the MenuArea's height.
            """
            pass


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

        self.image = pg.Surface(size, flags=pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.inner_rect = self.rect.inflate(-6, -6)

        # draw a rect that will become the button's border
        pg.draw.rect(
            self.image, self.menu.button_border_rgb, self.rect,
            border_radius=25
        )
        # draw the button slightly smaller than the border rectangle
        pg.draw.rect(
            self.image, self.menu.button_rgb, self.inner_rect,
            border_radius=25
        )
        # render, position, then blit text to button
        font_surf = menu.font.render(text, True, menu.font_rgb)
        font_rect = font_surf.get_rect(center=self.rect.center)
        self.image.blit(font_surf, font_rect)

    def update(self):
        """Update the button's mouseover flag, and, if clicked, do button
        function"""
        mouse_pos = self.menu.input_manager.mouse_pos
        mouse_is_clicking = self.menu.input_manager.is_clicking
        print(mouse_pos)
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
        """Initialize and position buttons"""
        super().add_buttons()
        # start button
        start_button = Button(
            self, 'start', (150, 50), self.game.toggle_menu
        )
        start_button.rect.midtop = self.center_group.rect.midtop
        self.center_group.add(start_button)

        # quit button
        quit_button = Button(
            self, 'quit', (150, 50), self.game.quit_game
        )
        quit_button.rect.midbottom = self.bottom_l_group.rect.midbottom
        self.bottom_r_group.add(quit_button)
