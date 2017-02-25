import random

from here_the_leafsighaway.chance import rand, nodes
from here_the_leafsighaway.instruments import base_instrument
from here_the_leafsighaway.lily import lilypond_file
from here_the_leafsighaway import config


class Guitar(base_instrument.Instrument):

    def __init__(self):
        base_instrument.Instrument.__init__(self, 'Guitar', -20, 16, 2, 1000, 'treble', -12, False)
        self.open_strings = [-20, -15, -10, -5, -1, 4]
        self.allow_artificial_harmonics = True
        self.natural_harmonics = [([-8, -1, 4], 'VI'),
                                  ([-3, 4, 9], 'V'),
                                  ([2, 9, 14], 'IV'),
                                  ([7, 14, 19], 'III'),
                                  ([11, 18, 23], 'II'),
                                  ([16, 23, 28], 'I')]


    def natural_harmonic_string(self, pitch_num):
        """
        Tests a given pitch_num to see if it can be played as a natural harmonic on the instrument,
        If pitch_num can be a natural harmonic, return the str of the string's name for markup.
        If it can't be a natural harmonic, return None
        :param pitch_num: int
        :return: str or None
        """
        i = 5
        while i >= 0:
            if pitch_num in self.natural_harmonics[i][0]:
                return self.natural_harmonics[i][1]
            i -= 1
        # If we've made it this far, pitch_num can't be a natural harmonic, return None
        return None

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

                # With self.natural_harmonic_frequency, if current_pitch can be a natural harmonic, add it.
                if random.uniform(0, 1) < self.natural_harmonic_frequency:
                    harmonic_string_test = self.natural_harmonic_string(current_pitch)
                    if harmonic_string_test is not None:
                        string_code_dict = {'I': 220, 'II': 221, 'III': 222, 'IV': 223, 'V': 224, 'VI': 225}
                        self.note_array.list[-1].add_articulation(string_code_dict[harmonic_string_test], 'over')
                        self.note_array.list[-1].is_artificial_harmonic = True
                # With self.artifical_harmonic_frequency add an artificial harmonic at the 8ve
                elif (random.uniform(0, 1) < self.artificial_harmonic_frequency and
                            self.allow_artificial_harmonics and (current_pitch < self.upper_tessitura)):
                    self.note_array.list[-1].is_artificial_harmonic = True
                    if isinstance(self.note_array.list[-1].pitch_num, int):
                        self.note_array.list[-1].pitch_num = [self.note_array.list[-1].pitch_num]
                    assert isinstance(self.note_array.list[-1].pitch_num, list)
                    self.note_array.list[-1].pitch_num.append(self.note_array.list[-1].pitch_num[0]+12)
                # TODO: elaborate on guitar chords (not just open strings, over 2 strings, etc.)
                # Within self.chord_frequency, add an open-string double-stop
                elif (random.uniform(0, 1) < self.chord_frequency) and (current_pitch < self.upper_tessitura):
                    if isinstance(self.note_array.list[-1].pitch_num, int):
                        self.note_array.list[-1].pitch_num = [self.note_array.list[-1].pitch_num]
                    assert isinstance(self.note_array.list[-1].pitch_num, list)
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
