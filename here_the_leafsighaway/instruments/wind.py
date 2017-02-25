import random

from here_the_leafsighaway.chance import rand, nodes
from here_the_leafsighaway.instruments import base_instrument
from here_the_leafsighaway.lily import note, lilypond_file
from here_the_leafsighaway import config


class Wind(base_instrument.Instrument):

    def __init__(self, instrument_name='Flute'):

        if instrument_name == 'Flute':
            base_instrument.Instrument.__init__(self, instrument_name, 0, 36, 28, 60, 'treble', 0)
        elif instrument_name == 'Alto Flute':
            base_instrument.Instrument.__init__(self, instrument_name, -5, 30, 28, 60, 'treble', -5)
        elif instrument_name == 'Oboe':
            base_instrument.Instrument.__init__(self, instrument_name, -2, 28, 18, 45, 'treble', 0)
        elif instrument_name == 'Clarinet':
            base_instrument.Instrument.__init__(self, instrument_name, -10, 20, 16, 15, 'treble', -2)
        elif instrument_name == 'Bass Clarinet':
            base_instrument.Instrument.__init__(self, instrument_name, -22, 12, 6, 35, 'treble', -14)
        elif instrument_name == 'Bassoon':
            base_instrument.Instrument.__init__(self, instrument_name, -25, 10, 6, 25, 'bass', 0)
            self.clef_list = ['bass', 'tenor']
            self.clef_change_tolerance = 3
            self.preferred_clef_extra_weight = 4
        else:
            print('ERROR: instrument_name of "' + instrument_name + '" in Wind.__init__() is not valid! ' \
                                                                    'Defaulting to Flute...')
            base_instrument.Instrument.__init__(self, instrument_name, 0, 36, 28, 60, 'treble', 0)

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
        # Get first pitch with a fairly strong bias toward the lower pitches in the register
        current_pitch = current_node.pitch_set[rand.weighted_rand(
            [(0, 100), (len(current_node.pitch_set)-1, 1)], do_round=True)]

        current_time_in_upper_tessitura = 0

        for i in range(0, note_count):
            current_dur = self.length_network.pick().get_value()
            while isinstance(current_node, nodes.Action):
                current_node = self.pitch_network.pick()
            if current_node.name[:4] == 'rest':
                self.note_array.create_note(current_pitch, current_dur, is_rest=True)
                current_time_in_upper_tessitura = 0
            else:
                current_pitch = current_node.move_pitch(current_pitch)
                self.note_array.create_note(current_pitch, current_dur)
                current_time_in_upper_tessitura += current_dur

            current_node = self.pitch_network.pick()
            # If the current time in the upper range exceeds the limit, change current_node to a downward pointing one
            if current_time_in_upper_tessitura > self.max_time_at_high:
                if random.randint(0, 1) == 0:
                    current_node = self.pitch_network.node_list[5]
                else:
                    current_node = self.pitch_network.node_list[7]
                current_time_in_upper_tessitura = 0

            if random.uniform(0, 1) < self.mode_change_frequency:
                self.change_mode()

        self.auto_add_slurs()
        self.auto_add_dynamics()
        if len(self.clef_list) > 1:
            self.note_array.auto_build_clefs(self.clef_list, self.clef_list[0],
                                             self.clef_change_tolerance, self.preferred_clef_extra_weight)
        if self.instrument_name == 'Flute' or self.instrument_name == 'Alto Flute':
            self.note_array.auto_build_octave_spanners()

        self.score.note_array = self.note_array
        output_ly_file = lilypond_file.LilypondFile(self.score)
        output_file_name = self.instrument_name + '_' + str(config.FileNameIndex)
        output_png = output_ly_file.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
        config.FileNameIndex += 1
        return output_png

    def special_action_1(self):
        """
        Long accented single note on A or B with trailing dim hairpin
        :return: str - image path
        """
        self.refresh_lily()
        # Find pitch
        pitch_set = note.extend_pitches_through_range([9, 11], self.lowest_note, self.highest_note)
        weighted_pitch_set = []
        i = 0
        while i < len(pitch_set):
            weighted_pitch_set.append((pitch_set[i], 10/(i+1)))
            i += 1
        use_pitch = rand.weighted_rand(weighted_pitch_set, 'discreet')
        # Find length
        use_length = rand.weighted_rand([(5, 2), (13, 8), (25, 1)], do_round=True)
        # Find dynamic
        use_dynamic = rand.weighted_rand([(9, 1), (8, 7), (4, 5), (0, 1)], do_round=True)
        self.note_array.create_note(use_pitch, use_length, dynamic=use_dynamic)
        self.note_array.list[-1].add_articulation(1)
        if self.sustained_playing:
            self.note_array.create_spanner(0, spanner_type='dim', apply_type='start')

        if len(self.clef_list) > 1:
            self.note_array.auto_build_clefs(self.clef_list, self.clef_list[0], self.clef_change_tolerance)
        self.score.note_array = self.note_array
        if self.instrument_name == 'Flute' or self.instrument_name == 'Alto Flute':
            self.note_array.auto_build_octave_spanners()
        output_ly_file = lilypond_file.LilypondFile(self.score)
        output_file_name = self.instrument_name + '_' + str(config.FileNameIndex)
        output_png = output_ly_file.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
        config.FileNameIndex += 1
        return output_png
