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
        self.previous_menu = None

    def goto_previous_menu(self):
        """Set current menu to the previous menu, or, if the user is on the
        main menu, return to the game."""
        if self.curr_menu is self.main_menu:
            self.game.toggle_menu()  # return to game if on main menu
        else:
            # swap current menu with previous menu
            self.curr_menu, self.previous_menu = \
                self.previous_menu, self.curr_menu

    def update_menu(self):
        for area in self.curr_menu.areas:
            area.update()

    def blit_menu(self):
        """Blit the menu to the game screen"""
        menu = self.curr_menu

        if self.game.debug:
            pg.draw.rect(
                self.game.screen, (0, 0, 0), menu.center_group.rect)
            pg.draw.rect(
                self.game.screen, (0, 0, 0), menu.bottom_l_group.rect)
            pg.draw.rect(
                self.game.screen, (0, 0, 0), menu.bottom_r_group.rect)

        for area in menu.areas:
            area.draw(menu.image)

        self.game.screen.blit(menu.image, menu.rect)


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

        self.button_rgb = self.vars.black_rgb
        self.button_border_rgb = self.vars.white_rgb

        self.font = self.vars.menu_font
        self.font_rgb = self.vars.white_rgb

        # initialize background
        self.image = pg.Surface(
            self.game.rect.size, flags=pg.SRCALPHA | pg.HWSURFACE
        )
        self.image.fill(self.bg_rgba)
        self.rect = self.game.rect.copy()

        self.areas = []
        self._create_areas()

    def _create_areas(self):
        margin = self.rect.w * 0.02

        # Top center
        self.top_center_group = \
            MenuArea((self.game.rect.w * .50, self.game.rect.h * .02))
        self.top_center_group.rect.midtop = self.rect.midtop

        # Center
        self.center_group = \
            MenuArea((self.game.rect.w * .30, self.game.rect.h * .5))
        self.center_group.rect.center = self.rect.center

        # Bottom left
        self.bottom_l_group = \
            MenuArea((self.game.rect.w * .15, self.game.rect.h * .2))
        self.bottom_l_group.rect.bottomleft = \
            (margin, self.rect.h - margin)

        # Bottom right
        self.bottom_r_group = \
            MenuArea((self.game.rect.w * .15, self.game.rect.h * .2))
        self.bottom_r_group.rect.bottomright = \
            (self.rect.w - margin, self.rect.h - margin)

        self.areas.extend([self.top_center_group, self.center_group,
                           self.bottom_l_group, self.bottom_r_group])

    def add_buttons(self):
        """
        Initialize buttons. You can show the formatting areas by pressing
        the debug key while on the menu. Buttons should be added to the group
        in the order that they appear #todo enable moving buttons after init
        """
        # back button
        back_button = Button(
            self, 'back', (120, 35), self.manager.goto_previous_menu
        )
        self.center_group.add(back_button)

        # quit button
        quit_button = Button(
            self, 'quit', (120, 35), self.game.quit_game
        )
        self.bottom_r_group.add(quit_button)


class MainMenu(MenuTemplate):
    def __init__(self, manager):
        super().__init__(manager)

        self.add_buttons()

    def add_buttons(self):
        """Initialize and position buttons"""
        # start button
        start_button = Button(
            self, 'start', (150, 50), self.game.toggle_menu
        )
        self.center_group.add(start_button)

        # add buttons defined in template under custom buttons
        super().add_buttons()


class MenuArea(Group):
    """
    An object that can be be used to group sprites together and position them
    within a rectangle on the menu. The rectangle is initiated with a size
    parameter, which should be a tuple containing width and height values. Menu
    elements are stored within the Group in the order that they are displayed
    within the area
    """

    def __init__(self, size, *sprites):
        Group.__init__(self, *sprites)

        self.rect = Rect(0, 0, *size)

    def add(self, *sprites):
        """Add sprites to group and then re-space elements in group."""
        super().add(*sprites)
        self.space_elements()

    def space_elements(self):
        """
        Space the sprites in the MenuArea on the y-axis so that they are evenly
        spread across the MenuArea's height.

        All elements start centered at the top of the area, they are moved
        downward according to the element_spacing variable and accounting for
        total height of all previously added elements. The elements are then
        moved uniformly downward so that the group of elements is centered
        vertically within the area.
        """
        if len(self) > 0:  # skip empty areas

            element_spacing = 0.10 * self.rect.h
            spaced_elements = []

            for row, element in enumerate(self):
                # start each element at top of area
                element.rect.midtop = self.rect.midtop

                # vertically space element
                height_elements_above = sum(x.rect.h for x in spaced_elements)
                space = row * element_spacing
                space += height_elements_above
                element.rect.y += space

                spaced_elements.append(element)

            # use top and bottom elements to find total used height
            top_y = spaced_elements[0].rect.top
            bottom_y = spaced_elements[-1].rect.bottom
            used_height = bottom_y - top_y

            # move all elements so that the group is centered in the area
            margin = (self.rect.h - used_height) / 2  # can be negative
            for element in self:
                element.rect.y += margin


class Button(Sprite):
    def __init__(self, menu, text, size: tuple, function=None):
        super().__init__()
        # give access to attributes of menu that initialized button
        self.menu = menu
        self.game = menu.game

        # appearance / behavior
        self.size = size
        self.text = text
        self.function = function
        self.mouse_over = False

        self.draw_button()

    def draw_button(self):
        """
        Draw a button with a border by drawing a larger rectangle underneath
        of a smaller rectangle
        """
        self.image = pg.Surface(self.size, flags=pg.SRCALPHA)
        self.rect = self.image.get_rect()

        border_size = self.game.rect.w * 0.0045

        border_rect = self.rect.copy()
        inner_rect = border_rect.inflate(-border_size, -border_size)

        # draw a rect that will become the button's border
        pg.draw.rect(
            self.image, self.menu.button_border_rgb, border_rect,
            border_radius=25
        )
        # draw the button slightly smaller than the border rectangle
        pg.draw.rect(
            self.image, self.menu.button_rgb, inner_rect,
            border_radius=25
        )
        # add text to button
        font_surf = self.menu.font.render(self.text, True, self.menu.font_rgb)
        font_rect = font_surf.get_rect(center=border_rect.center)
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
