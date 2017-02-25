import random

import here_the_leafsighaway.text_instructions as instructions
from here_the_leafsighaway.chance import rand


class Audience:
    def __init__(self):
        self.action_weights = [('listen until', 15), ('visualize', 1), ('notice', 2), ('fermata', 7)]
        self.mode_change_frequency = round(random.uniform(0.1, 0.3), 3)
        self.fermata_length_weights = rand.random_weight_list(20, 100)

    def change_mode(self):
        self.mode_change_frequency = round(random.uniform(0.1, 0.3), 3)
        self.fermata_length_weights = rand.random_weight_list(20, 100)

    def play(self):
        if random.uniform(0, 1) < self.mode_change_frequency:
            self.change_mode()
        action = rand.weighted_rand(self.action_weights, run_type='discreet')
        if action == 'listen until':
            return instructions.listen_until_you_hear()
        elif action == 'visualize':
            return instructions.visualize_a_color()
        elif action == 'fermata':
            return instructions.draw_big_fermata(self.fermata_length_weights)
        elif action == 'notice':
            return instructions.notice_something()
        else:
            print('WARNING: Invalid action is being passed to Audience.play(), defaulting to "listen until"...')
            return instructions.listen_until_you_hear()
