import subprocess
import sys
import time

import pygame
from pygame.locals import *

from beginning import Beginning
from constants import GAME_HEIGHT, GAME_WIDTH
from menu_screen import MenuScreen
from tiled_map import Map
from title_page import TitlePage

MAP_NAMES = [
    'overworld',
    'tunnels_of_the_north',
    'cave_of_gadianton',
    'sierra_pass',
    'cavity_of_a_rock',
    'passage_to_gid',
    'house_of_moroni',
]


class Game(object):
    def __init__(self, screen):
        self.real_screen = screen
        self.virtual_width = GAME_WIDTH
        self.virtual_height = GAME_HEIGHT
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))
        self.clock = pygame.time.Clock()
        self.fps = 1000
        self.current_map = None
        self.set_screen_state('title')
        pygame.event.set_blocked(MOUSEMOTION)
        pygame.event.set_blocked(ACTIVEEVENT)
        pygame.event.set_blocked(VIDEORESIZE)
        pygame.event.set_blocked(KEYUP)
        self.title_page = TitlePage(self.virtual_screen, self)
        self.menu_screen = MenuScreen(self.virtual_screen, self)
        self.beginning_screen = Beginning(self, self.virtual_screen)
        self.game_state = None
        self.fitted_screen = None # gets initialized in resize_window()
        self.window_size = screen.get_size()
        self.resize_window(self.window_size)

    def set_screen_state(self, state):
        '''
        Valid screen states are 'title', 'game', 'menu', 'beginning'
        '''
        self._screen_state = state
        if state in ['title', 'menu']:
            pygame.key.set_repeat(300, 300)
        else:
            pygame.key.set_repeat(50, 50)

    def update_game_state(self, updates):
        self.game_state.update(updates)

    def add_to_inventory(self, item):
        acquired_items = list(self.game_state['acquired_items'])
        if 'id' in item:
            acquired_items.append(item['id'])
        company = copy.deepcopy(self.game_state['company'])
        placed = False
        for warlord in company:
            if len(warlord['items']) == 8 or warload['soldiers'] == 0:
                continue
            placed = True
            warlord['items'].append(item['name'])
        surplus = list(self.game_state['surplus'])
        if not placed:
            surplus.append(item['name'])
        self.update_game_state({'acquired_items': acquired_items, 'company': company, 'surplus': surplus})

    def set_current_map(self, map_name, position, direction, followers='under', dialog=None):
        assert followers in [
            'trail', # position the followers trailing behind the hero
            'under', # position the followers underneath the hero on the same tile
        ]
        self.current_map = Map(
            self.virtual_screen, map_name, self, position, direction=direction, followers=followers, opening_dialog=dialog,
        )

    def resize_window(self, size):
        self.real_screen = pygame.display.set_mode(size)
        (width, height) = size
        width_multiplier = width*1.0 / self.virtual_width
        height_multiplier = height*1.0 / self.virtual_height
        multiplier = min(width_multiplier, height_multiplier)
        fitted_width = int(self.virtual_width*multiplier)
        fitted_height = int(self.virtual_height*multiplier)
        fitted_x_pos = (width - fitted_width) / 2
        fitted_y_pos = (height - fitted_height) / 2
        self.fitted_screen = self.real_screen.subsurface(
            (fitted_x_pos, fitted_y_pos, fitted_width, fitted_height)
        )

    def scale(self):
        self.real_screen.fill((0,0,0))
        pygame.transform.scale(self.virtual_screen, self.fitted_screen.get_size(), self.fitted_screen)

    def draw(self):
        if self._screen_state == 'game':
            self.current_map.draw()
        elif self._screen_state == 'title':
            self.title_page.draw()
        elif self._screen_state == 'menu':
            self.menu_screen.draw()
        elif self._screen_state == 'beginning':
            self.beginning_screen.draw()
        self.scale()

    def update(self, dt):
        if self._screen_state == 'game':
            self.current_map.update(dt)
        elif self._screen_state == 'title':
            self.title_page.update(dt)
        elif self._screen_state == 'menu':
            self.menu_screen.update(dt)
        elif self._screen_state == 'beginning':
            self.beginning_screen.update(dt)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                return
            if event.type == KEYDOWN:
                pressed = pygame.key.get_pressed()
                if pressed[K_ESCAPE]:
                    self.running = False
                    pygame.quit()
                    print(" ")
                    time.sleep(0.5)
                    print self.current_map.name
                    print("Shutdown... Complete")
                    sys.exit()
                    return
                if self._screen_state == "game":
                    self.current_map.handle_input(pressed)
                elif self._screen_state == 'title':
                    self.title_page.handle_input(pressed)
                elif self._screen_state == 'menu':
                    self.menu_screen.handle_input(pressed)
                elif self._screen_state == 'beginning':
                    self.beginning_screen.handle_input(pressed)

    def run(self):
        self.running = True
        try:
            while self.running:
                dt = self.clock.tick(self.fps)/1000.0
                self.handle_input()
                self.update(dt)
                self.draw()
                pygame.display.flip()
        except KeyboardInterrupt:
            self.running = False
            pygame.quit()
