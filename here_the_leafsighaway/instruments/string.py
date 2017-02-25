import random

from here_the_leafsighaway import config
from here_the_leafsighaway.chance import nodes, rand
from here_the_leafsighaway.instruments import base_instrument
from here_the_leafsighaway.lily import lilypond_file


class String(base_instrument.Instrument):

    def __init__(self, instrument_name='Violin'):
        self.is_currently_pizz = False
        self.is_currently_muted = False
        if instrument_name == 'Violin':
            base_instrument.Instrument.__init__(self, instrument_name, -5, 44, 28, 80, 'treble', 0)
            self.allow_artificial_harmonics = True
            self.open_strings = [-5, 2, 9, 16]
            self.natural_harmonics = [7, 14, 19, 23,   # G String
                                      14, 21, 26, 30,  # D String
                                      21, 28, 33,      # A String
                                      28, 35, 40]      # E String
        elif instrument_name == 'Viola':
            base_instrument.Instrument.__init__(self, instrument_name, -12, 32, 21, 73, 'alto', 0)
            self.allow_artificial_harmonics = True
            self.open_strings = [-12, -5, 2, 9]
            self.natural_harmonics = [0, 7, 12, 16,   # C String
                                      7, 14, 19, 23,  # G String
                                      14, 21, 26,     # D String
                                      21, 28, 33]     # A String
            self.clef_list = ['alto', 'treble']
            self.clef_change_tolerance = 4
            self.preferred_clef_extra_weight = 4
        elif instrument_name == 'Cello':
            base_instrument.Instrument.__init__(self, instrument_name, -24, 24, 12, 61, 'bass', 0)
            self.allow_artificial_harmonics = True
            self.open_strings = [-24, -17, -10, -3]
            self.natural_harmonics = [-12, -5, 0, 4,  # C String
                                      -5, 2, 7, 11,   # G String
                                      2, 9, 14,       # D String
                                      9, 16, 21]      # A String
            self.clef_list = ['bass', 'treble']
            self.clef_change_tolerance = 2
            self.preferred_clef_extra_weight = 2
        else:
            # Assume otherwise Bass
            base_instrument.Instrument.__init__(self, instrument_name, -32, 8, 6, 61, 'bass', -12)
            self.allow_artificial_harmonics = False
            self.open_strings = [-32, -27, -22, -17]
            self.natural_harmonics = [-20, -13, -8, -4, -1,  # E String
                                      -15, -7, -3, 1, 4,     # A String
                                      -10, -2, 2, 6, 9,      # D String
                                      -5, 3, 7, 11, 14]      # G String
            self.clef_list = ['bass', 'treble']
            self.clef_change_tolerance = 2
            self.preferred_clef_extra_weight = 4

    def can_be_harmonic(self, pitch_num):
        """
        Tests a given pitch_num to see if it can be played as a natural harmonic on the instrument
        :param pitch_num:
        :return:
        """
        if pitch_num in self.natural_harmonics:
            return True
        else:
            return False

    def get_best_open_string(self, input_pitch):
        """
        Takes an input pitch, calculates which string it will be best played on, and returns an available open string
        :param input_pitch: int
        :return: int
        """
        if input_pitch < self.open_strings[0]:
            print("ERROR: input_pitch in String.get_best_open_string() is lower than lowest open string! Skipping")
            return False
        # If input_pitch is on the 4th string, return the 3rd string
        if self.open_strings[0] <= input_pitch < self.open_strings[1]:
            return self.open_strings[1]
        # elif input_pitch is on the 3rd string, return either the 4th or 2nd string randomly
        elif self.open_strings[1] <= input_pitch < self.open_strings[2]:
            if random.randint(0, 7) > 2:
                return self.open_strings[0]
            else:
                return self.open_strings[2]
        # elif input_pitch is on the 2nd string, return either the 3rd or 1st string randomly
        elif self.open_strings[2] <= input_pitch < self.open_strings[3]:
            if random.randint(0, 7) > 2:
                return self.open_strings[1]
            else:
                return self.open_strings[3]
        # else, (if input_pitch is higher than the 1st string), return the 2nd string
        else:
            return self.open_strings[2]

    # Override play() method
    def play(self):

        self.refresh_lily()

        # Roll for special actions
        special_action_roll = rand.weighted_rand(self.special_action_weights, 'discreet')
        if special_action_roll != 0:
            if special_action_roll == 1:
                self.previous_action = 'Special Action 1'
                return self.special_action_1()
            elif special_action_roll == 2:
                self.previous_action = 'Special Action 2'
                return self.special_action_2()
            elif special_action_roll == 3 and self.previous_action != 'Special Action 3':
                self.previous_action = 'Special Action 3'
                return self.special_action_3()
        else:
            self.previous_action = 'Normal Play'

        note_count = rand.weighted_rand(self.note_count_weights, do_round=True)
        current_node = self.pitch_network.pick()
        while (not isinstance(current_node, nodes.NoteBehavior)) or (current_node.name[:4] == 'rest'):
            current_node = self.pitch_network.pick()
        # Get first pitch
        current_pitch = self._find_first_pitch(current_node.pitch_set, self.starting_pitch_weights)

        for i in range(0, note_count):
            current_dur = self.length_network.pick().get_value()

            # pick through action (sub-network link) nodes
            while isinstance(current_node, nodes.Action):
                current_node = self.pitch_network.pick()
            if current_node.name[:4] == 'rest':
                self.note_array.create_note(current_pitch, current_dur, is_rest=True)
            else:
                current_pitch = current_node.move_pitch(current_pitch)
                self.note_array.create_note(current_pitch, current_dur)

                # If it's the first note, roll for pizz/mute changes
                if i == 0:
                    if self.is_currently_pizz and random.randint(0, 6) == 0:
                        self.note_array.list[0].add_articulation(201, 'over')
                        self.is_currently_pizz = False
                        self.sustained_playing = True
                    elif not self.is_currently_pizz and random.randint(0, 16) == 0:
                        self.note_array.list[0].add_articulation(200, 'over')
                        self.is_currently_pizz = True
                        self.sustained_playing = False

                    if self.is_currently_muted and random.randint(0, 15) == 0:
                        self.note_array.list[0].add_articulation(203, 'over')
                        self.is_currently_muted = False
                    elif not self.is_currently_muted and random.randint(0, 15) == 0:
                        self.note_array.list[0].add_articulation(202, 'over')
                        self.is_currently_muted = True

                # Within self.natural_harmonic_frequency, if current_pitch can be a natural harmonic, add it
                if random.uniform(0, 1) < self.natural_harmonic_frequency and self.can_be_harmonic(current_pitch):
                    self.note_array.list[-1].add_articulation(105, 'over')
                # Within self.artificial_harmonic_frequency, add an artificial harmonic at the 4th
                elif (random.uniform(0, 1) < self.artificial_harmonic_frequency and
                            self.allow_artificial_harmonics and (current_pitch < self.upper_tessitura)):
                    self.note_array.list[-1].is_artificial_harmonic = True
                    if isinstance(self.note_array.list[-1].pitch_num, int):
                        self.note_array.list[-1].pitch_num = [self.note_array.list[-1].pitch_num]
                    assert isinstance(self.note_array.list[-1].pitch_num, list)
                    self.note_array.list[-1].pitch_num.append(self.note_array.list[-1].pitch_num[0]+5)
                # Within self.chord_frequency, add an open-string double-stop
                elif (random.uniform(0, 1) < self.chord_frequency) and (current_pitch < self.upper_tessitura):
                    if isinstance(self.note_array.list[-1].pitch_num, int):
                        self.note_array.list[-1].pitch_num = [self.note_array.list[-1].pitch_num]
                    open_string_pitch = self.get_best_open_string(self.note_array.list[-1].pitch_num[0])
                    self.note_array.list[-1].pitch_num.append(open_string_pitch)

            current_node = self.pitch_network.pick()

            if random.uniform(0, 1) < self.mode_change_frequency:
                self.change_mode()

        self.note_array.auto_build_octave_spanners()
        self.auto_add_dynamics()
        self.auto_add_slurs()
        if len(self.clef_list) > 1:
            self.note_array.auto_build_clefs(self.clef_list, self.initial_clef,
                                             self.clef_change_tolerance, self.preferred_clef_extra_weight)

        self.score.note_array = self.note_array
        output_ly_file = lilypond_file.LilypondFile(self.score)
        output_file_name = self.instrument_name + '_' + str(config.FileNameIndex)
        output_png = output_ly_file.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
        config.FileNameIndex += 1
        return output_png

    def build_length_rules(self):

        very_short = nodes.Vector('very short', [(0, 10), (2, 1)])
        short = nodes.Vector('short', [(1, 10), (3, 1)])
        medium = nodes.Vector('medium', [(2, 1), (4, 10), (6, 1)])
        long = nodes.Vector('long', [(4, 1), (8, 10), (9, 0)])
        very_long = nodes.Vector('very long', [(6, 1), (12, 10), (16, 3), (19, 0)])

        very_short.add_link(very_short, 17); very_short.add_link(short, 4)
        very_short.add_link(medium, 1); very_short.add_link(very_long, 3)

        short.add_link(very_short, 2); short.add_link(short, 1); short.add_link(medium, 8)
        short.add_link(long, 3)

        medium.add_link(short, 3); medium.add_link(long, 4)

        long.add_link(very_short, 1); long.add_link(medium, 4)

        very_long.add_link(long, 1); very_long.add_link(medium, 6); very_long.add_link(short, 3)

        self.length_network.add_node([very_short, short, medium, long, very_long])
