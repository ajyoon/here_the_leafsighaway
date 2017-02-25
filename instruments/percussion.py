import random

from instruments import base_instrument
from chance import rand, nodes
from lily import note, lilypond_file
from shared import Globals


class Percussion(base_instrument.Instrument):

    def __init__(self):
        base_instrument.Instrument.__init__(self, 'Percussion', -7, 7, initial_clef='percussion')
        self.score._lily_accidental_style = 'default'
        self.score._lily_clef_offset_modifier = 1.25
        self.score._lily_shortest_duration_space = 1
        self.score._lily_eraser_markup_width_offset = -1.35

        self.beater_list = ['hard yarn', 'soft yarn', 'soft rubber']
        self.beater_change_frequency = round(random.uniform(0.03, 0.3), 3)
        self.current_beater = None

        self.minimum_rest_length = 1.75
        self.sustained_playing = False
        # if instrument_number != 9:
        #     d_pitch_set = note.extend_pitches_through_range([0, 2, 4, 5, 7, 9, 11],
        #                                                          self.lowest_note, self.highest_note)
        self.starting_pitch_weights = rand.random_weight_list(0.0, 1.0, 0.17, return_as_tuples=True)
        self.mode_change_frequency = 0.03
        self.special_action_weights = [(0, 80), (1, 7), (2, 4), (3, 1)]

    def build_pitch_rules(self):
        """
        Builds self.pitch_network
        :return: None
        """
        # Note that pitch, in percussion context, refers simply to staff spaces.
        # 'Pitch' network using only white keys since pitches here really refer to instruments
        pitch_set = note.extend_pitches_through_range([0, 2, 4, 5, 7, 9, 11], self.lowest_note, self.highest_note)
        pn_1 = nodes.NoteBehavior(name='stay put', direction=0, interval_weights=[(0, 1)],
                                         pitch_set=pitch_set, count_intervals_by_slots=True)
        pn_2 = nodes.NoteBehavior(name='step up', direction=1, interval_weights=[(1, 1)],
                                         pitch_set=pitch_set, count_intervals_by_slots=True)
        pn_3 = nodes.NoteBehavior(name='step down', direction=-1, interval_weights=[(1, 1)],
                                         pitch_set=pitch_set, count_intervals_by_slots=True)
        pn_4 = nodes.NoteBehavior(name='skip up', direction=1, interval_weights=[(2, 4), (3, 2)],
                                         pitch_set=pitch_set, count_intervals_by_slots=True)
        pn_5 = nodes.NoteBehavior(name='skip down', direction=-1, interval_weights=[(2, 4), (3, 2)],
                                         pitch_set=pitch_set, count_intervals_by_slots=True)
        pn_6 = nodes.NoteBehavior(name='big leap up', direction=1, interval_weights=[(4, 10), (8, 1)],
                                         pitch_set=pitch_set, count_intervals_by_slots=True)
        pn_7 = nodes.NoteBehavior(name='big leap down', direction=-1, interval_weights=[(4, 10), (8, 1)],
                                         pitch_set=pitch_set, count_intervals_by_slots=True)
        pn_8 = nodes.NoteBehavior(name='rest', pitch_set=pitch_set)

        pn_1.add_link(pn_2, 2)
        pn_1.add_link(pn_1, 8)
        pn_1.add_link(pn_3, 2)
        pn_1.add_link(pn_4, 2)
        pn_1.add_link(pn_5, 2)
        pn_1.add_link(pn_6, 1)
        pn_1.add_link(pn_7, 1)

        pn_2.add_link(pn_3, 10)
        pn_2.add_link(pn_1, 1)
        pn_2.add_link(pn_8, 2)
        pn_2.add_link(pn_2, 1)
        pn_2.add_link(pn_5, 2)
        pn_2.add_link(pn_7, 0.2)

        pn_3.add_link(pn_2, 10)
        pn_3.add_link(pn_1, 4)
        pn_3.add_link(pn_4, 3)
        pn_3.add_link(pn_6, 1)
        pn_3.add_link(pn_4, 3)
        pn_3.add_link(pn_8, 2)

        pn_4.add_link(pn_1, 3)
        pn_4.add_link(pn_3, 8)
        pn_4.add_link(pn_7, 1)
        pn_4.add_link(pn_8, 4)

        pn_5.add_link(pn_1, 4)
        pn_5.add_link(pn_2, 7)
        pn_5.add_link(pn_8, 2)
        pn_5.add_link(pn_6, 1)

        pn_6.add_link(pn_1, 8)
        pn_6.add_link(pn_3, 8)
        pn_6.add_link(pn_5, 6)
        pn_6.add_link(pn_7, 2)
        pn_6.add_link(pn_8, 4)

        pn_7.add_link(pn_1, 8)
        pn_7.add_link(pn_2, 4)
        pn_7.add_link(pn_4, 2)
        pn_7.add_link(pn_6, 2)
        pn_7.add_link(pn_8, 1)

        pn_8.add_link(pn_1, 5)
        pn_8.add_link(pn_2, 2)
        pn_8.add_link(pn_3, 2)
        pn_8.add_link(pn_4, 2)
        pn_8.add_link(pn_5, 2)
        pn_8.add_link(pn_6, 1)
        pn_8.add_link(pn_7, 1)

        self.pitch_network.add_node([pn_1, pn_2, pn_3, pn_4, pn_5, pn_6, pn_7, pn_8])

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
        while (not isinstance(current_node, nodes.NoteBehavior)) or (current_node.name == 'rest'):
            current_node = self.pitch_network.pick(current_node)

        # Pick first note randomly
        current_pitch = self._find_first_pitch(current_node.pitch_set, self.starting_pitch_weights)

        for i in range(0, note_count):
            current_dur = self.length_network.pick().get_value()

            while isinstance(current_node, nodes.Action):
                current_node = self.pitch_network.pick()
            if current_node.name == 'rest':
                if current_dur < self.minimum_rest_length:
                    current_dur = self.minimum_rest_length
                self.note_array.create_note(current_pitch, current_dur, is_rest=True)
            else:
                current_pitch = current_node.move_pitch(current_pitch)

                # Special handling for spacing of square noteheads, make a little wider
                if current_pitch in [4, 5, 7]:
                    current_dur += 1

                self.note_array.create_note(current_pitch, current_dur)
                if current_pitch == -3:
                    self.note_array.list[-1].notehead_style_code = 1
                elif current_pitch in [-5, -7]:
                    self.note_array.list[-1].notehead_style_code = 3
                elif current_pitch in [4, 5, 7]:
                    self.note_array.list[-1].notehead_style_code = 4

                # If it's the first note, do first-note rolls
                if i == 0:
                    # Roll for beater changes
                    if (random.uniform(0, 1) < self.beater_change_frequency) or self.current_beater is None:
                        new_beater = self.current_beater
                        while new_beater == self.current_beater:
                            new_beater = random.choice(self.beater_list)
                        self.current_beater = new_beater
                        reverse_mute_dict = {'hard yarn': 230, 'soft yarn': 231, 'soft rubber': 232}
                        self.note_array.list[-1].add_articulation(reverse_mute_dict[self.current_beater], 'over')

            current_node = self.pitch_network.pick(current_node)

            if random.uniform(0, 1) < self.mode_change_frequency:
                self.perc_change_mode()

        self.auto_add_dynamics()
        self.auto_add_slurs()

        self.score.note_array = self.note_array
        output_ly_file = lilypond_file.LilypondFile(self.score)
        output_file_name = self.instrument_name + '_' + str(Globals.FileNameIndex)
        output_png = output_ly_file.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
        Globals.FileNameIndex += 1
        return output_png

    def perc_change_mode(self, mode_change_frequency=True, note_count_weights=True, length_network=True,
                         beater_change_frequency=True):
        if mode_change_frequency:
            self.mode_change_frequency = round(random.uniform(0.01, 0.2), 3)
        if note_count_weights:
            self.note_count_weights = rand.random_weight_list(1, random.randint(6, 15), 0.15)
        if length_network:
            self.length_network.apply_noise(round(random.uniform(0.001, 0.05), 5))
        if beater_change_frequency:
            self.beater_change_frequency = round(random.uniform(0.03, 0.3), 3)

    def special_action_1(self):
        """
        Long accented single note on A or B with trailing dim hairpin
        :return: str - image path
        """
        self.refresh_lily()
        # Find pitch
        pitch_set = [-1, 0, 2]
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
            self.note_array.auto_build_clefs(self.clef_list, self.initial_clef,
                                             self.clef_change_tolerance, self.preferred_clef_extra_weight)
        self.score.note_array = self.note_array
        output_ly_file = lilypond_file.LilypondFile(self.score)
        output_file_name = self.instrument_name + '_' + str(Globals.FileNameIndex)
        output_png = output_ly_file.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
        Globals.FileNameIndex += 1
        return output_png
