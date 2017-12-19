# -*- coding: UTF-8 -*-

import json
import os
import shutil

import pygame

from constants import ITEMS, TACTICS

# WARNING: Don't import anything from the rotj repo into here. To avoid circular imports,
# we are restricting this module to only functions that do not depend on any other rotj
# modules except constants. If you need to make a function available to other modules but it also depends
# on a module, perhaps make it in the same module it would depend on. See text.create_prompt
# as an example.

RESOURCES_DIR = 'data'


def get_intelligence(warlord):
    stats = load_stats(warlord)
    return stats['intelligence']


def can_level_up(warlord):
    stats = load_stats(warlord)
    return 'max_soldiers_by_level' in stats


def get_tactic_for_level(level):
    for tactic in TACTICS:
        if TACTICS[tactic]['min_level'] == level:
            return tactic
    return None


def get_tactics(stats, level, pretty=True):
    tactics = []
    for slot in range(1,7):
        tactics.append(_get_max_tactic(intelligence=stats['intelligence'], level=level, slot=slot))
    if pretty:
        return ['{:~<10}'.format(tactic.title().replace(' ', '~')) for tactic in tactics]
    else:
        return tactics


def _get_max_tactic(intelligence=0, level=0, slot=0):
    found_tactic = ""
    min_intelligence = 0
    min_level = 0
    for tactic_name, tactic in TACTICS.items():
        if tactic['slot'] != slot:
            continue
        if tactic['min_intelligence'] > intelligence:
            continue
        if tactic['min_level'] > level:
            continue
        if (
            tactic['min_level'] > min_level
            or (tactic['min_level'] == min_level and tactic['min_intelligence'] > min_intelligence)
        ):
            min_level = tactic['min_level']
            min_intelligence = tactic['min_intelligence']
            found_tactic = tactic_name
    return found_tactic


def get_equip_based_stat_value(stat, equips):
    return sum([ITEMS[equip['name']].get(stat, 0) for equip in equips])


def load_stats(name):
    with open('data/stats/{}.json'.format(name)) as f:
        json_data = json.loads(f.read())
    return json_data


def get_max_soldiers(warlord, level=None):
    assert level is not None
    with open('data/stats/{}.json'.format(warlord)) as f:
        json_data = json.loads(f.read())
    if 'max_soldiers_by_level' in json_data:
        soldiers = json_data['max_soldiers_by_level'][level-1]
    else:
        soldiers = json_data['max_soldiers']
    return soldiers


def hyphenate(text, chars):
    if len(text) > chars:
        return '{}{}\n{}'.format(
            text[0:chars-1],
            '-' if '-' not in text[chars-2:chars] else '',
            text[chars-1:],
        )
    else:
        return text


def get_max_tactical_points(warlord, level=None):
    assert level is not None
    with open('data/stats/{}.json'.format(warlord)) as f:
        json_data = json.loads(f.read())
    if 'tactical_points_by_level' in json_data:
        tactical_points = json_data['tactical_points_by_level'][level-1]
    else:
        tactical_points = json_data['tactical_points']
    return tactical_points


def get_enemy_stats(warlord):
    with open('data/stats/{}.json'.format(warlord)) as f:
        json_data = json.loads(f.read())
    return {
        'strength': json_data['strength'],
        'defense': json_data['defense'],
        'intelligence': json_data['intelligence'],
        'agility': json_data['agility'],
        'evasion': json_data['evasion'],
        'tactical_points': json_data['tactical_points'],
        'attack_points': json_data['attack_points'],
        'armor_class': json_data['armor_class'],
        'tactics': json_data['tactics'],
        'soldiers': json_data['soldiers'],
    }


def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCES_DIR, "images", filename))


def get_map_filename(filename):
    return os.path.join(RESOURCES_DIR, "maps", filename)


def is_half_second():
    '''
    Returns if the game time is in the bottom half of a second.
    '''
    t = pygame.time.get_ticks()/1000.0
    return round(t - int(t)) == 0


def is_quarter_second():
    t = pygame.time.get_ticks()/500.0
    return round(t - int(t)) == 0


def load_save_states():
    return [load_json_file_if_exists('data/state/{}.json'.format(x)) for x in [1,2,3]]


def save_game_state(slot, game_state):
    with open('data/state/{}.json'.format(slot), 'w') as f:
        f.write(json.dumps(game_state))


def erase_save_state(slot):
    os.remove('data/state/{}.json'.format(slot))


def create_save_state(slot, name):
    with open('data/state/{}.json'.format(slot), 'w') as f:
        f.write(json.dumps({'name': name, 'level': 0}))


def copy_save_state(from_slot, to_slot):
    shutil.copyfile('data/state/{}.json'.format(from_slot), 'data/state/{}.json'.format(to_slot))


def load_json_file_if_exists(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            json_data = json.loads(f.read())
    else:
        json_data = {}
    return json_data
