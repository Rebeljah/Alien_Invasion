"""
Module for representing a menu system. The MenuManager class is initiated
in the game's __init__. The MenuManager class works by first initializing
different subclasses of a MenuTemplate and then displaying the different
menus. MenuTemplate contains methods and classes that are common
to most menus (buttons, text boxes, ...etc.)
"""
import pygame as pg
from pygame.sprite import Sprite, Group
from pygame.rect import Rect


class _Elements:
    class Element(Sprite):
        def __init__(self, menu):
            super().__init__()
            # give access to attributes of menu that initialized button
            self.menu = menu
            self.game = menu.game

    class Button(Element):
        def __init__(self, menu, text, size: tuple, func=None):
            super().__init__(menu)

            self.size = size
            self.text = text
            self.function = func
            self.mouse_over = False

            self._render_button()

        def _render_button(self):
            """
            Draw a button with a border by drawing a larger rectangle
            underneath of a smaller rectangle
            """
            self.image = pg.Surface(self.size, flags=pg.SRCALPHA)
            self.rect = self.image.get_rect()

            border_size = self.game.rect.w * 0.0045

            border_rect = self.rect.copy()
            inner_rect = border_rect.inflate(-border_size, -border_size)

            # draw a rect that will become the button's border
            pg.draw.rect(self.image, self.menu.button_border_rgb, border_rect,
                        border_radius=25)
            # draw a slightly smaller than rectangle over the border rectangle
            pg.draw.rect(self.image, self.menu.button_rgb, inner_rect,
                        border_radius=25)
            # add text to button
            font_surf = self.menu.font.render(self.text, True, self.menu.font_rgb)
            font_rect = font_surf.get_rect(center=inner_rect.center)
            self.image.blit(font_surf, font_rect)

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

    # TODO
    class LeaderBoard(Element):
        def __init__(self, menu):
            super().__init__(menu)

            self.leaderboard: dict = self.game.scoreboard.leaderboard


class _MenuArea(Group):
    """
    An object that can be be used to group sprites together and position them
    within a rectangle on the menu. The rectangle is initiated with a size
    parameter, which should be a tuple containing width and height values. Menu
    elements are stored within the Group in the order that they are displayed
    within the area.
    """

    def __init__(self, size, *sprites):
        Group.__init__(self, *sprites)

        self.rect = Rect(0, 0, *size)

    def add(self, *sprites):
        """Add sprites to group and then re-space elements in group."""
        super().add(*sprites)
        self.position_elements()

    def position_elements(self):
        """
        Space the sprites in the MenuArea on the y-axis so that they are evenly
        spread across the MenuArea's height.

        All elements start centered at the top of the area, they are moved
        downward according to the element_spacing variable and accounting for
        total height of all previously added elements. The elements are then
        moved uniformly up or down so that the group of elements is centered
        vertically within the area.
        """
        if len(self) > 0:  # skip empty areas

            spacing = 0.10 * self.rect.h
            spaced_elements = []

            for element in self:

                if not spaced_elements:
                    element.rect.midtop = self.rect.midtop
                else:
                    last_rect = spaced_elements[-1].rect
                    element.rect.midtop = last_rect.midbottom
                    element.rect.y += spacing

                spaced_elements.append(element)

            # get height of group.
            top_y = spaced_elements[0].rect.top
            bottom_y = spaced_elements[-1].rect.bottom
            # use top and bottom y-values for total height of spaced elements
            used_height = bottom_y - top_y

            margin = (self.rect.h - used_height) / 2  # can be negative
            # move all elements so that the group is centered in the area
            for element in self:
                element.rect.y += margin


class _MenuTemplate:
    """base class representing methods and attributes common to all menus"""

    def __init__(self, manager):
        self.manager = manager
        self.game = manager.game
        self.vars = manager.vars
        self.input_manager = self.game.input_manager

        self.title = 'template'

        # appearance
        self.bg_rgba = pg.Color(*self.vars.light_blue_rgb, 50)

        self.button_rgb = self.vars.black_rgb
        self.button_border_rgb = self.vars.white_rgb

        self.font = self.vars.menu_font
        self.font_rgb = self.vars.white_rgb

        # initialize menu surface and fill with bg color
        self.image = pg.Surface(
            self.game.rect.size, flags=pg.SRCALPHA | pg.HWSURFACE
        )
        self.image.fill(self.bg_rgba)
        self.rect = self.image.get_rect()

        self.areas = self._define_areas()
        

    def update(self):
        """Update the elements in each area of the menu"""
        for area in self.areas.values():
            area.update()

    def draw_menu(self):
        """Blit each element in the menu areas to the menu image, then blit
        the menu image to the game screen"""

        # hit the debug key to show areas for formatting
        if self.game.debug:
            for area in self.areas.values():
                pg.draw.rect(self.game.screen, (0, 0, 0), area.rect)

        # blit elements to menu image then blit menu image to screen
        for area in self.areas.values():
            area.draw(self.image)

        self.game.screen.blit(self.image, self.rect)

    def _define_areas(self) -> dict:
        """Create default areas that can be used to place elements"""

        # margin for spacing areas away from menu edge
        margin = self.rect.w * 0.02

        areas = {
            'title':
                _MenuArea((self.game.rect.w * .50, self.game.rect.h * .14)),
            'center':
                _MenuArea((self.game.rect.w * .30, self.game.rect.h * .5)),
            'bottom l':
                _MenuArea((self.game.rect.w * .15, self.game.rect.h * .2)),
            'bottom r':
                _MenuArea((self.game.rect.w * .15, self.game.rect.h * .2))
        }

        menu_w, menu_h = self.rect.w, self.rect.h

        # position areas using rectangles
        areas['title'].rect.midtop = \
            self.rect.midtop
        areas['center'].rect.center = \
            self.rect.center
        areas['bottom l'].rect.bottomleft = \
            (margin, menu_h - margin)
        areas['bottom r'].rect.bottomright = \
            (menu_w - margin, menu_h - margin)
        
        return areas

    def add_elements(self):
        """
        Initialize elements. You can show the formatting areas by pressing
        the debug key while on the menu. Elements should be added to the group
        in the order that they are to appear in the menu area.
        """
        # back button
        self.areas['bottom l'].add(_Elements.Button(
            self, 'back', (120, 35), self.manager.goto_previous_menu
        ))

        # quit button
        self.areas['bottom r'].add(_Elements.Button(
            self, 'quit', (120, 35), self.game.quit_game
        ))


class MainMenu(_MenuTemplate):
    def __init__(self, manager):
        super().__init__(manager)

        self.add_elements()
        super().add_elements()

    def add_elements(self):
        """Initialize and position elements"""
        # start button
        self.areas['center'].add(_Elements.Button(
            self, 'start', (165, 65), func=self.game.toggle_menu
        ))


class LeaderBoardMenu(_MenuTemplate):
    def __init__(self, manager):
        super().__init__(manager)

        self.add_elements()
        super().add_elements()

    def add_elements(self):
        self.areas['center'].add(_LeaderBoard(self))


class MenuManager:
    """
    Main acces point for the game loop to control switching,
    updating, and drawing of menus.
    """
    def __init__(self, game):
        self.game = game
        self.vars = game.vars
        self.input_manager = game.input_manager

        # initialize menu screens
        self.main_menu = MainMenu(self)
        # TODO self.leaderboard_menu = LeaderBoardMenu(self)

        # set default menu
        self.curr_menu = self.main_menu
        self.last_menu = None

    def goto_previous_menu(self):
        """Set current menu to the previous menu, or, if the user is on the
        main menu, return to the game."""
        if self.curr_menu is self.main_menu:
            self.game.toggle_menu()  # return to game if on main menu
        else:
            # swap current menu with previous menu
            self.curr_menu, self.last_menu = self.last_menu, self.curr_menu

    def update_menu(self):
        """Call the update method on the current menu"""
        self.curr_menu.update()

    def draw_menu(self):
        """Blit the menu to the game screen"""
        self.curr_menu.draw_menu()

