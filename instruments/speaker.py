import random

import chance.network
import chance.nodes
import chance.rand
import special_instructions.text_instructions as instructions


class Speaker:
    def __init__(self):
        self.action_weights = [('listen until', 18), ('fermata', 6)]
        self.mode_change_frequency = round(random.uniform(0.1, 0.3), 3)
        self.fermata_length_weights = chance.rand.random_weight_list(20, 100)

    def change_mode(self):
        self.mode_change_frequency = round(random.uniform(0.1, 0.3), 3)
        self.fermata_length_weights = chance.rand.random_weight_list(20, 100)

    def play(self):
        if random.uniform(0, 1) < self.mode_change_frequency:
            self.change_mode()
        action = chance.rand.weighted_rand(self.action_weights, run_type='discreet')
        if action == 'listen until':
            return instructions.speaker_boxed_text()
        elif action == 'fermata':
            return instructions.draw_big_fermata(self.fermata_length_weights)
