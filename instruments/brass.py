from instruments import base_instrument
import random
import chance
import shared.Globals
from lily import note, lilypond_file


class Brass(base_instrument.Instrument):

    def __init__(self, name='High Horn'):
        self.current_mute = None
        if name == 'High Horn':
            base_instrument.Instrument.__init__(self, name, -16, 12, 6, 40, 'treble', -7)
            self.starting_pitch_weights = [(0, 10), (0.2, 70), (0.3, 25), (0.75, 0)]
            self.mute_list = ['senza sord', 'straight mute', 'practice mute']
        elif name == 'Low Horn':
            base_instrument.Instrument.__init__(self, name, -24, 6, 6, 40, 'treble', -7)
            self.mute_list = ['senza sord', 'straight mute', 'practice mute']
            self.clef_list = ['bass', 'treble']
            self.starting_pitch_weights = [(0, 10), (0.2, 70), (0.3, 25), (0.7, 0)]
            self.preferred_clef_extra_weight = 1
            self.clef_change_tolerance = 3
        elif name == 'Trumpet':
            base_instrument.Instrument.__init__(self, name, -8, 24, 19, 40, 'treble', -2)
            self.starting_pitch_weights = [(0, 10), (0.2, 70), (0.3, 25), (0.8, 0)]
            self.mute_list = ['senza sord', 'straight mute', 'practice mute']
        elif name == 'Tenor Trombone':
            base_instrument.Instrument.__init__(self, name, -20, 8, 4, 40, 'bass', -7)
            self.starting_pitch_weights = [(0, 10), (0.2, 70), (0.3, 25), (0.8, 0)]
            self.mute_list = ['senza sord', 'straight mute', 'practice mute']
            self.clef_list = ['bass', 'tenor']
            self.preferred_clef_extra_weight = 2
        self.mute_change_frequency = round(random.randint(20, 75)/1000.0, 2)

    def build_pitch_rules(self):
        # Build E, F#, B Sub-Network
        e_f_b_pitch_set = note.extend_pitches_through_range([4, 6, 11], self.lowest_note, self.highest_note)
        e_pn_1 = chance.nodes.NoteBehavior(name='stay put - e', direction=0, interval_weights=[(0, 1)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_2 = chance.nodes.NoteBehavior(name='step up - e', direction=1, interval_weights=[(1, 1)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_3 = chance.nodes.NoteBehavior(name='step down - e', direction=-1, interval_weights=[(1, 1)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_4 = chance.nodes.NoteBehavior(name='skip up - e', direction=1, interval_weights=[(2, 4), (3, 2)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_5 = chance.nodes.NoteBehavior(name='skip down - e', direction=-1, interval_weights=[(2, 4), (3, 2)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_6 = chance.nodes.NoteBehavior(name='big leap up - e', direction=1, interval_weights=[(3, 10), (6, 1)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_7 = chance.nodes.NoteBehavior(name='big leap down - e', direction=-1, interval_weights=[(3, 10), (6, 1)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_8 = chance.nodes.NoteBehavior(name='rest - e', pitch_set=e_f_b_pitch_set)

        e_pn_1.add_link(e_pn_2, 2); e_pn_1.add_link(e_pn_3, 2); e_pn_1.add_link(e_pn_4, 2)
        e_pn_1.add_link(e_pn_5, 2); e_pn_1.add_link(e_pn_6, 1); e_pn_1.add_link(e_pn_7, 1)
        e_pn_2.add_link(e_pn_3, 10); e_pn_2.add_link(e_pn_1, 1); e_pn_2.add_link(e_pn_8, 2)
        e_pn_2.add_link(e_pn_2, 1); e_pn_2.add_link(e_pn_5, 2); e_pn_2.add_link(e_pn_7, 0.2)
        e_pn_3.add_link(e_pn_2, 10); e_pn_3.add_link(e_pn_1, 4); e_pn_3.add_link(e_pn_4, 3)
        e_pn_3.add_link(e_pn_6, 1); e_pn_3.add_link(e_pn_4, 3); e_pn_3.add_link(e_pn_8, 2)
        e_pn_4.add_link(e_pn_1, 3); e_pn_4.add_link(e_pn_3, 8), e_pn_4.add_link(e_pn_7, 1)
        e_pn_4.add_link(e_pn_8, 4)
        e_pn_5.add_link(e_pn_1, 4); e_pn_5.add_link(e_pn_2, 7); e_pn_5.add_link(e_pn_8, 2)
        e_pn_5.add_link(e_pn_6, 1)
        e_pn_6.add_link(e_pn_1, 8); e_pn_6.add_link(e_pn_3, 8); e_pn_6.add_link(e_pn_5, 6)
        e_pn_6.add_link(e_pn_7, 2); e_pn_6.add_link(e_pn_8, 4)
        e_pn_7.add_link(e_pn_1, 8); e_pn_7.add_link(e_pn_2, 4); e_pn_7.add_link(e_pn_4, 2)
        e_pn_7.add_link(e_pn_6, 2); e_pn_7.add_link(e_pn_8, 1)
        e_pn_8.add_link(e_pn_1, 5); e_pn_8.add_link(e_pn_2, 2); e_pn_8.add_link(e_pn_3, 2)
        e_pn_8.add_link(e_pn_4, 2); e_pn_8.add_link(e_pn_5, 2); e_pn_8.add_link(e_pn_6, 1)
        e_pn_8.add_link(e_pn_7, 1)

        # Build Hexatonic Sub-Network
        # h_pitch_set consists of E, G#, A, B, C#, D#
        h_pitch_set = note.extend_pitches_through_range([1, 3, 4, 8, 9, 11], self.lowest_note, self.highest_note)
        h_pn_1 = chance.nodes.NoteBehavior(name='stay put - h', direction=0, interval_weights=[(0, 1)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_2 = chance.nodes.NoteBehavior(name='step up - h', direction=1, interval_weights=[(1, 1)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_3 = chance.nodes.NoteBehavior(name='step down - h', direction=-1, interval_weights=[(1, 1)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_4 = chance.nodes.NoteBehavior(name='skip up - h', direction=1, interval_weights=[(2, 5), (3, 2)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_5 = chance.nodes.NoteBehavior(name='skip down - h', direction=-1, interval_weights=[(2, 5), (3, 2)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_6 = chance.nodes.NoteBehavior(name='leap up - h', direction=1, interval_weights=[(3, 5), (6, 2)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_7 = chance.nodes.NoteBehavior(name='leap down - h', direction=-1, interval_weights=[(3, 5), (6, 2)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_8 = chance.nodes.NoteBehavior(name='rest - h', pitch_set=h_pitch_set)

        h_pn_1.add_link(h_pn_1, 1); h_pn_1.add_link(h_pn_2, 3); h_pn_1.add_link(h_pn_3, 6)
        h_pn_1.add_link(h_pn_4, 2); h_pn_1.add_link(h_pn_5, 2); h_pn_1.add_link(h_pn_6, 1)
        h_pn_1.add_link(h_pn_7, 1); h_pn_1.add_link(h_pn_8, 4)

        h_pn_2.add_link(h_pn_1, 3); h_pn_2.add_link(h_pn_2, 2); h_pn_2.add_link(h_pn_3, 6)
        h_pn_2.add_link(h_pn_4, 2); h_pn_2.add_link(h_pn_5, 4); h_pn_2.add_link(h_pn_6, 1)
        h_pn_2.add_link(h_pn_7, 1); h_pn_2.add_link(h_pn_8, 4)

        h_pn_3.add_link(h_pn_1, 3); h_pn_3.add_link(h_pn_2, 5); h_pn_3.add_link(h_pn_3, 1)
        h_pn_3.add_link(h_pn_4, 3); h_pn_3.add_link(h_pn_5, 4); h_pn_3.add_link(h_pn_6, 2)
        h_pn_3.add_link(h_pn_7, 1); h_pn_3.add_link(h_pn_8, 2)

        h_pn_4.add_link(h_pn_1, 3); h_pn_4.add_link(h_pn_2, 1); h_pn_4.add_link(h_pn_3, 5)
        h_pn_4.add_link(h_pn_4, 1); h_pn_4.add_link(h_pn_5, 6); h_pn_4.add_link(h_pn_7, 2)
        h_pn_4.add_link(h_pn_8, 3)

        h_pn_5.add_link(h_pn_1, 3); h_pn_5.add_link(h_pn_2, 5); h_pn_5.add_link(h_pn_3, 1)
        h_pn_5.add_link(h_pn_4, 5); h_pn_5.add_link(h_pn_5, 2); h_pn_5.add_link(h_pn_6, 1)
        h_pn_5.add_link(h_pn_8, 3)

        h_pn_6.add_link(h_pn_1, 1); h_pn_6.add_link(h_pn_2, 1); h_pn_6.add_link(h_pn_3, 5)
        h_pn_6.add_link(h_pn_4, 2); h_pn_6.add_link(h_pn_5, 4); h_pn_6.add_link(h_pn_7, 3)
        h_pn_6.add_link(h_pn_8, 7)

        h_pn_7.add_link(h_pn_1, 2); h_pn_7.add_link(h_pn_2, 5); h_pn_7.add_link(h_pn_3, 1)
        h_pn_7.add_link(h_pn_4, 3); h_pn_7.add_link(h_pn_5, 1); h_pn_7.add_link(h_pn_6, 3)
        h_pn_7.add_link(h_pn_8, 3)

        h_pn_8.add_link(h_pn_1, 2); h_pn_8.add_link(h_pn_2, 4); h_pn_8.add_link(h_pn_3, 4)
        h_pn_8.add_link(h_pn_4, 2); h_pn_8.add_link(h_pn_5, 2); h_pn_8.add_link(h_pn_6, 1)
        h_pn_8.add_link(h_pn_7, 1)

        # Build Chromatic Sub-Network
        # c_pitch_set is all possible notes between lowest and highest notes
        c_pitch_set = list(range(self.lowest_note, self.highest_note))  # Maybe later build in certain PC omissions?
        c_pn_1 = chance.nodes.NoteBehavior(name='stay put - c', direction=0, interval_weights=[(0, 1)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_2 = chance.nodes.NoteBehavior(name='step up - c', direction=1, interval_weights=[(1, 4), (2, 4)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_3 = chance.nodes.NoteBehavior(name='step down - c', direction=-1, interval_weights=[(1, 4), (2, 4)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_4 = chance.nodes.NoteBehavior(name='skip up - c', direction=1, interval_weights=[(2, 5), (4, 4)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_5 = chance.nodes.NoteBehavior(name='skip down - c', direction=-1, interval_weights=[(2, 5), (4, 4)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_6 = chance.nodes.NoteBehavior(name='leap up - c', direction=1, interval_weights=[(4, 6), (7, 1)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_7 = chance.nodes.NoteBehavior(name='leap down - c', direction=-1, interval_weights=[(4, 6), (7, 1)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_8 = chance.nodes.NoteBehavior(name='rest - c', pitch_set=c_pitch_set)

        c_pn_1.add_link(c_pn_1, 1); c_pn_1.add_link(c_pn_2, 3); c_pn_1.add_link(c_pn_3, 6)
        c_pn_1.add_link(c_pn_4, 2); c_pn_1.add_link(c_pn_5, 2); c_pn_1.add_link(c_pn_6, 1)
        c_pn_1.add_link(c_pn_7, 1); c_pn_1.add_link(c_pn_8, 4)

        c_pn_2.add_link(c_pn_1, 3); c_pn_2.add_link(c_pn_2, 6); c_pn_2.add_link(c_pn_3, 9)
        c_pn_2.add_link(c_pn_4, 2); c_pn_2.add_link(c_pn_5, 4); c_pn_2.add_link(c_pn_6, 1)
        c_pn_2.add_link(c_pn_7, 1); c_pn_2.add_link(c_pn_8, 4)

        c_pn_3.add_link(c_pn_1, 3); c_pn_3.add_link(c_pn_2, 9); c_pn_3.add_link(c_pn_3, 6)
        c_pn_3.add_link(c_pn_4, 3); c_pn_3.add_link(c_pn_5, 4); c_pn_3.add_link(c_pn_6, 2)
        c_pn_3.add_link(c_pn_7, 1); c_pn_3.add_link(c_pn_8, 3)

        c_pn_4.add_link(c_pn_1, 3); c_pn_4.add_link(c_pn_2, 1); c_pn_4.add_link(c_pn_3, 5)
        c_pn_4.add_link(c_pn_4, 1); c_pn_4.add_link(c_pn_5, 6); c_pn_4.add_link(c_pn_7, 2)
        c_pn_4.add_link(c_pn_8, 5)

        c_pn_5.add_link(c_pn_1, 3); c_pn_5.add_link(c_pn_2, 5); c_pn_5.add_link(c_pn_3, 1)
        c_pn_5.add_link(c_pn_4, 5); c_pn_5.add_link(c_pn_5, 2); c_pn_5.add_link(c_pn_6, 1)
        c_pn_5.add_link(c_pn_8, 9)

        c_pn_6.add_link(c_pn_1, 1); c_pn_6.add_link(c_pn_2, 1); c_pn_6.add_link(c_pn_3, 5)
        c_pn_6.add_link(c_pn_4, 2); c_pn_6.add_link(c_pn_5, 4); c_pn_6.add_link(c_pn_7, 3)
        c_pn_6.add_link(c_pn_8, 7)

        c_pn_7.add_link(c_pn_1, 2); c_pn_7.add_link(c_pn_2, 5); c_pn_7.add_link(c_pn_3, 1)
        c_pn_7.add_link(c_pn_4, 3); c_pn_7.add_link(c_pn_5, 1); c_pn_7.add_link(c_pn_6, 3)
        c_pn_7.add_link(c_pn_8, 5)

        c_pn_8.add_link(c_pn_1, 2); c_pn_8.add_link(c_pn_2, 4); c_pn_8.add_link(c_pn_3, 4)
        c_pn_8.add_link(c_pn_4, 2); c_pn_8.add_link(c_pn_5, 2); c_pn_8.add_link(c_pn_6, 1)
        c_pn_8.add_link(c_pn_7, 1)

        # Add shared nodes
        s_jump_node_1 = chance.nodes.Action('Jump to hexatonic pitch subnetwork')
        s_jump_node_1.add_link_to_self([e_pn_1, e_pn_2, e_pn_3, e_pn_4, e_pn_5, e_pn_6, e_pn_7, e_pn_8], 5)
        s_jump_node_1.add_link([h_pn_1, h_pn_2, h_pn_3, h_pn_4, h_pn_5, h_pn_6, h_pn_7], 1)
        s_jump_node_2 = chance.nodes.Action('Jump to chromatic pitch subnetwork')
        s_jump_node_2.add_link_to_self([h_pn_1, h_pn_2, h_pn_3, h_pn_4, h_pn_5, h_pn_6, h_pn_7, h_pn_8], 5)
        s_jump_node_2.add_link([c_pn_1, c_pn_2, c_pn_3, c_pn_4, c_pn_5, c_pn_6, c_pn_7], 1)
        s_jump_node_3 = chance.nodes.Action('Jump to E F# B pitch subnetwork')
        s_jump_node_3.add_link_to_self([c_pn_1, c_pn_2, c_pn_3, c_pn_4, c_pn_5, c_pn_6, c_pn_7, c_pn_8], 5)
        s_jump_node_3.add_link([e_pn_1, e_pn_2, e_pn_3, e_pn_4, e_pn_5, e_pn_6, e_pn_7], 1)

        self.pitch_network.add_node([e_pn_1, e_pn_2, e_pn_3, e_pn_4, e_pn_5, e_pn_6, e_pn_7, e_pn_8,
                                     h_pn_1, h_pn_2, h_pn_3, h_pn_4, h_pn_5, h_pn_6, h_pn_7, h_pn_8,
                                     c_pn_1, c_pn_2, c_pn_3, c_pn_4, c_pn_5, c_pn_6, c_pn_7, c_pn_8,
                                     s_jump_node_1, s_jump_node_2, s_jump_node_3])

    def play(self):

        self.refresh_lily()

        # Roll for special actions
        special_action_roll = chance.rand.weighted_rand(self.special_action_weights, 'discreet')
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

        note_count = chance.rand.weighted_rand(self.note_count_weights, do_round=True)
        current_node = self.pitch_network.pick()
        while (not isinstance(current_node, chance.nodes.NoteBehavior)) or (current_node.name[:4] == 'rest'):
            current_node = self.pitch_network.pick()
        # Get first pitch
        current_pitch = self._find_first_pitch(current_node.pitch_set, self.starting_pitch_weights)

        current_time_in_upper_tessitura = 0

        for i in range(0, note_count):
            current_dur = self.length_network.pick().get_value()
            while isinstance(current_node, chance.nodes.Action):
                current_node = self.pitch_network.pick()
            if current_node.name[:4] == 'rest':
                self.note_array.create_note(current_pitch, current_dur, is_rest=True)
                current_time_in_upper_tessitura = 0
            else:
                current_pitch = current_node.move_pitch(current_pitch)
                self.note_array.create_note(current_pitch, current_dur)
                current_time_in_upper_tessitura += current_dur

                # If it's the first note, do first-note rolls
                if i == 0:
                    # Roll for mute changes
                    if (random.uniform(0, 1) < self.mute_change_frequency) or (self.current_mute is None):
                        new_mute = self.current_mute
                        while new_mute == self.current_mute:
                            new_mute = random.choice(self.mute_list)
                        self.current_mute = new_mute
                        reverse_mute_dict = {'senza sord': 203, 'straight mute': 204, 'practice mute': 205}
                        self.note_array.list[-1].add_articulation(reverse_mute_dict[self.current_mute], 'over')

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

        self.auto_add_dynamics()
        if len(self.clef_list) > 1:
            self.note_array.auto_build_clefs(self.clef_list, self.initial_clef,
                                             self.clef_change_tolerance, self.preferred_clef_extra_weight)
        self.auto_add_slurs()

        self.score.note_array = self.note_array
        output_ly_file = lilypond_file.LilypondFile(self.score)
        output_file_name = self.instrument_name + '_' + str(shared.Globals.FileNameIndex)
        output_png = output_ly_file.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
        shared.Globals.FileNameIndex += 1
        return output_png

    def build_length_rules(self):

        very_short = chance.nodes.Vector('very short', [(0, 10), (2, 1)])
        short = chance.nodes.Vector('short', [(1, 10), (3, 1)])
        medium = chance.nodes.Vector('medium', [(2, 1), (4, 10), (6, 1)])
        long = chance.nodes.Vector('long', [(4, 1), (8, 10), (9, 0)])
        very_long = chance.nodes.Vector('very long', [(6, 1), (12, 10), (16, 3), (19, 0)])

        very_short.add_link(very_short, 17); very_short.add_link(short, 4);
        very_short.add_link(medium, 1); very_short.add_link(very_long, 3)

        short.add_link(very_short, 2); short.add_link(short, 1); short.add_link(medium, 8)
        short.add_link(long, 3)

        medium.add_link(short, 3); medium.add_link(long, 4)

        long.add_link(very_short, 1); long.add_link(medium, 4)

        very_long.add_link(long, 1); very_long.add_link(medium, 6); very_long.add_link(short, 3)

        self.length_network.add_node([very_short, short, medium, long, very_long])
