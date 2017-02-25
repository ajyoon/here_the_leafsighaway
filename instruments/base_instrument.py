import random

import chance.network
import chance.nodes
import chance.rand
import lily.lilypond_file
import lily.note
import lily.score
import shared
import special_instructions.text_instructions


class Instrument:

    def __init__(self, instrument_name='Flute', lowest_note=0, highest_note=36,
                 upper_tessitura=28, max_time_at_high=60,
                 initial_clef='treble', transposition_int=0,
                 sustained_playing=True):
        self.instrument_name = instrument_name
        self.lowest_note = lowest_note
        self.highest_note = highest_note
        self.upper_tessitura = upper_tessitura
        self.max_time_at_high = max_time_at_high  # Longest allowed time to stay in a very high register
        self.initial_clef = initial_clef
        self.transposition_int = transposition_int
        self.note_array = lily.note.NoteArray(initial_clef=self.initial_clef, transposition_int=self.transposition_int)
        self.score = lily.score.Score(self.note_array)
        self.pitch_network = chance.network.Network()
        self.build_pitch_rules()
        self.length_network = chance.network.Network()
        self.build_length_rules()
        self.clef_list = [initial_clef]
        # True if instrument uses sustained sound (flute, arco string), false if not (piano, percussion, pizz string)
        self.sustained_playing = sustained_playing
        self.special_action_weights = [(0, 80), (1, 7), (2, 4), (3, 1)]
        self.text_instruction_list = special_instructions.text_instructions.shared_list
        self.previous_action = None
        self.clef_change_tolerance = 5
        self.preferred_clef_extra_weight = 4
        self.starting_pitch_weights = [(0, 40), (0.15, 70), (1, 0)]
        self.note_count_weights = chance.rand.random_weight_list(1, random.randint(6, 15), 0.15)
        self.mode_change_frequency = 0.03
        self.natural_harmonic_frequency = round(random.uniform(0.04, 0.4), 3)
        self.artificial_harmonic_frequency = round(chance.rand.weighted_rand(
            [(0.01, 150), (0.2, 20), (0.4, 5), (0.5, 1)]), 3)
        self.chord_frequency = round(chance.rand.weighted_rand([(0.01, 150), (0.1, 20), (0.2, 0)]), 3)

    def refresh_lily(self):
        """
        Reinitialized self.note_array and self.score.note_array
        :return: None
        """
        self.note_array = lily.note.NoteArray(initial_clef=self.initial_clef, transposition_int=self.transposition_int)
        # self.score = lily.score.Score(self.note_array)
        self.score.note_array = self.note_array

    def build_pitch_rules(self):
        """
        Builds self.pitch_network
        :return: None
        """
        # Build E, F#, B Sub-Network
        e_f_b_pitch_set = lily.note.extend_pitches_through_range([4, 6, 11], self.lowest_note, self.highest_note)
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
        e_pn_6 = chance.nodes.NoteBehavior(name='big leap up - e', direction=1, interval_weights=[(4, 10), (8, 1)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_7 = chance.nodes.NoteBehavior(name='big leap down - e', direction=-1, interval_weights=[(4, 10), (8, 1)],
                                           pitch_set=e_f_b_pitch_set, count_intervals_by_slots=True)
        e_pn_8 = chance.nodes.NoteBehavior(name='rest - e', pitch_set=e_f_b_pitch_set)

        e_pn_1.add_link(e_pn_2, 2)
        e_pn_1.add_link(e_pn_3, 2)
        e_pn_1.add_link(e_pn_4, 2)
        e_pn_1.add_link(e_pn_5, 2)
        e_pn_1.add_link(e_pn_6, 1)
        e_pn_1.add_link(e_pn_7, 1)
        e_pn_2.add_link(e_pn_3, 10)
        e_pn_2.add_link(e_pn_1, 1)
        e_pn_2.add_link(e_pn_8, 2)
        e_pn_2.add_link(e_pn_2, 1)
        e_pn_2.add_link(e_pn_5, 2)
        e_pn_2.add_link(e_pn_7, 0.2)
        e_pn_3.add_link(e_pn_2, 10)
        e_pn_3.add_link(e_pn_1, 4)
        e_pn_3.add_link(e_pn_4, 3)
        e_pn_3.add_link(e_pn_6, 1)
        e_pn_3.add_link(e_pn_4, 3)
        e_pn_3.add_link(e_pn_8, 2)
        e_pn_4.add_link(e_pn_1, 3)
        e_pn_4.add_link(e_pn_3, 8)
        e_pn_4.add_link(e_pn_7, 1)
        e_pn_4.add_link(e_pn_8, 4)
        e_pn_5.add_link(e_pn_1, 4)
        e_pn_5.add_link(e_pn_2, 7)
        e_pn_5.add_link(e_pn_8, 2)
        e_pn_5.add_link(e_pn_6, 1)
        e_pn_6.add_link(e_pn_1, 8)
        e_pn_6.add_link(e_pn_3, 8)
        e_pn_6.add_link(e_pn_5, 6)
        e_pn_6.add_link(e_pn_7, 2)
        e_pn_6.add_link(e_pn_8, 4)
        e_pn_7.add_link(e_pn_1, 8)
        e_pn_7.add_link(e_pn_2, 4)
        e_pn_7.add_link(e_pn_4, 2)
        e_pn_7.add_link(e_pn_6, 2)
        e_pn_7.add_link(e_pn_8, 1)
        e_pn_8.add_link(e_pn_1, 5)
        e_pn_8.add_link(e_pn_2, 2)
        e_pn_8.add_link(e_pn_3, 2)
        e_pn_8.add_link(e_pn_4, 2)
        e_pn_8.add_link(e_pn_5, 2)
        e_pn_8.add_link(e_pn_6, 1)
        e_pn_8.add_link(e_pn_7, 1)

        # Build Hexatonic Sub-Network
        # h_pitch_set consists of E, G#, A, B, C#, D#
        h_pitch_set = lily.note.extend_pitches_through_range([1, 3, 4, 8, 9, 11], self.lowest_note, self.highest_note)
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
        h_pn_6 = chance.nodes.NoteBehavior(name='leap up - h', direction=1, interval_weights=[(4, 5), (9, 2)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_7 = chance.nodes.NoteBehavior(name='leap down - h', direction=-1, interval_weights=[(4, 5), (9, 2)],
                                           pitch_set=h_pitch_set, count_intervals_by_slots=True)
        h_pn_8 = chance.nodes.NoteBehavior(name='rest - h', pitch_set=h_pitch_set)

        h_pn_1.add_link(h_pn_1, 1)
        h_pn_1.add_link(h_pn_2, 3)
        h_pn_1.add_link(h_pn_3, 6)
        h_pn_1.add_link(h_pn_4, 2)
        h_pn_1.add_link(h_pn_5, 2)
        h_pn_1.add_link(h_pn_6, 1)
        h_pn_1.add_link(h_pn_7, 1)
        h_pn_1.add_link(h_pn_8, 4)

        h_pn_2.add_link(h_pn_1, 3)
        h_pn_2.add_link(h_pn_2, 2)
        h_pn_2.add_link(h_pn_3, 6)
        h_pn_2.add_link(h_pn_4, 2)
        h_pn_2.add_link(h_pn_5, 4)
        h_pn_2.add_link(h_pn_6, 1)
        h_pn_2.add_link(h_pn_7, 1)
        h_pn_2.add_link(h_pn_8, 4)

        h_pn_3.add_link(h_pn_1, 3)
        h_pn_3.add_link(h_pn_2, 5)
        h_pn_3.add_link(h_pn_3, 1)
        h_pn_3.add_link(h_pn_4, 3)
        h_pn_3.add_link(h_pn_5, 4)
        h_pn_3.add_link(h_pn_6, 2)
        h_pn_3.add_link(h_pn_7, 1)
        h_pn_3.add_link(h_pn_8, 2)

        h_pn_4.add_link(h_pn_1, 3)
        h_pn_4.add_link(h_pn_2, 1)
        h_pn_4.add_link(h_pn_3, 5)
        h_pn_4.add_link(h_pn_4, 1)
        h_pn_4.add_link(h_pn_5, 6)
        h_pn_4.add_link(h_pn_7, 2)
        h_pn_4.add_link(h_pn_8, 3)

        h_pn_5.add_link(h_pn_1, 3)
        h_pn_5.add_link(h_pn_2, 5)
        h_pn_5.add_link(h_pn_3, 1)
        h_pn_5.add_link(h_pn_4, 5)
        h_pn_5.add_link(h_pn_5, 2)
        h_pn_5.add_link(h_pn_6, 1)
        h_pn_5.add_link(h_pn_8, 3)

        h_pn_6.add_link(h_pn_1, 1)
        h_pn_6.add_link(h_pn_2, 1)
        h_pn_6.add_link(h_pn_3, 5)
        h_pn_6.add_link(h_pn_4, 2)
        h_pn_6.add_link(h_pn_5, 4)
        h_pn_6.add_link(h_pn_7, 3)
        h_pn_6.add_link(h_pn_8, 7)

        h_pn_7.add_link(h_pn_1, 2)
        h_pn_7.add_link(h_pn_2, 5)
        h_pn_7.add_link(h_pn_3, 1)
        h_pn_7.add_link(h_pn_4, 3)
        h_pn_7.add_link(h_pn_5, 1)
        h_pn_7.add_link(h_pn_6, 3)
        h_pn_7.add_link(h_pn_8, 3)

        h_pn_8.add_link(h_pn_1, 2)
        h_pn_8.add_link(h_pn_2, 4)
        h_pn_8.add_link(h_pn_3, 4)
        h_pn_8.add_link(h_pn_4, 2)
        h_pn_8.add_link(h_pn_5, 2)
        h_pn_8.add_link(h_pn_6, 1)
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
        c_pn_4 = chance.nodes.NoteBehavior(name='skip up - c', direction=1, interval_weights=[(3, 5), (6, 4)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_5 = chance.nodes.NoteBehavior(name='skip down - c', direction=-1, interval_weights=[(3, 5), (6, 4)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_6 = chance.nodes.NoteBehavior(name='leap up - c', direction=1, interval_weights=[(7, 6), (20, 1)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_7 = chance.nodes.NoteBehavior(name='leap down - c', direction=-1, interval_weights=[(7, 6), (20, 1)],
                                           pitch_set=c_pitch_set, count_intervals_by_slots=False)
        c_pn_8 = chance.nodes.NoteBehavior(name='rest - c', pitch_set=c_pitch_set)

        c_pn_1.add_link(c_pn_1, 1)
        c_pn_1.add_link(c_pn_2, 3)
        c_pn_1.add_link(c_pn_3, 6)
        c_pn_1.add_link(c_pn_4, 2)
        c_pn_1.add_link(c_pn_5, 2)
        c_pn_1.add_link(c_pn_6, 1)
        c_pn_1.add_link(c_pn_7, 1)
        c_pn_1.add_link(c_pn_8, 4)

        c_pn_2.add_link(c_pn_1, 3)
        c_pn_2.add_link(c_pn_2, 6)
        c_pn_2.add_link(c_pn_3, 9)
        c_pn_2.add_link(c_pn_4, 2)
        c_pn_2.add_link(c_pn_5, 4)
        c_pn_2.add_link(c_pn_6, 1)
        c_pn_2.add_link(c_pn_7, 1)
        c_pn_2.add_link(c_pn_8, 4)

        c_pn_3.add_link(c_pn_1, 3)
        c_pn_3.add_link(c_pn_2, 9)
        c_pn_3.add_link(c_pn_3, 6)
        c_pn_3.add_link(c_pn_4, 3)
        c_pn_3.add_link(c_pn_5, 4)
        c_pn_3.add_link(c_pn_6, 2)
        c_pn_3.add_link(c_pn_7, 1)
        c_pn_3.add_link(c_pn_8, 3)

        c_pn_4.add_link(c_pn_1, 3)
        c_pn_4.add_link(c_pn_2, 1)
        c_pn_4.add_link(c_pn_3, 5)
        c_pn_4.add_link(c_pn_4, 1)
        c_pn_4.add_link(c_pn_5, 6)
        c_pn_4.add_link(c_pn_7, 2)
        c_pn_4.add_link(c_pn_8, 5)

        c_pn_5.add_link(c_pn_1, 3)
        c_pn_5.add_link(c_pn_2, 5)
        c_pn_5.add_link(c_pn_3, 1)
        c_pn_5.add_link(c_pn_4, 5)
        c_pn_5.add_link(c_pn_5, 2)
        c_pn_5.add_link(c_pn_6, 1)
        c_pn_5.add_link(c_pn_8, 9)

        c_pn_6.add_link(c_pn_1, 1)
        c_pn_6.add_link(c_pn_2, 1)
        c_pn_6.add_link(c_pn_3, 5)
        c_pn_6.add_link(c_pn_4, 2)
        c_pn_6.add_link(c_pn_5, 4)
        c_pn_6.add_link(c_pn_7, 3)
        c_pn_6.add_link(c_pn_8, 7)

        c_pn_7.add_link(c_pn_1, 2)
        c_pn_7.add_link(c_pn_2, 5)
        c_pn_7.add_link(c_pn_3, 1)
        c_pn_7.add_link(c_pn_4, 3)
        c_pn_7.add_link(c_pn_5, 1)
        c_pn_7.add_link(c_pn_6, 3)
        c_pn_7.add_link(c_pn_8, 5)

        c_pn_8.add_link(c_pn_1, 2)
        c_pn_8.add_link(c_pn_2, 4)
        c_pn_8.add_link(c_pn_3, 4)
        c_pn_8.add_link(c_pn_4, 2)
        c_pn_8.add_link(c_pn_5, 2)
        c_pn_8.add_link(c_pn_6, 1)
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

    def build_length_rules(self):

        very_short = chance.nodes.Vector('very short', [(0, 10), (2, 1)])
        short = chance.nodes.Vector('short', [(1, 10), (3, 1)])
        medium = chance.nodes.Vector('medium', [(2, 1), (4, 10), (6, 1)])
        long = chance.nodes.Vector('long', [(4, 1), (8, 10), (9, 0)])
        very_long = chance.nodes.Vector('very long', [(6, 1), (12, 10), (16, 3), (19, 0)])

        very_short.add_link(very_short, 17)
        very_short.add_link(short, 4)
        very_short.add_link(medium, 1)
        very_short.add_link(very_long, 3)

        short.add_link(very_short, 4)
        short.add_link(short, 1)
        short.add_link(medium, 8)
        short.add_link(long, 3)

        medium.add_link(short, 3)
        medium.add_link(long, 4)

        long.add_link(very_short, 1)
        long.add_link(medium, 4)

        very_long.add_link(long, 1)
        very_long.add_link(medium, 6)
        very_long.add_link(short, 3)

        self.length_network.add_node([very_short, short, medium, long, very_long])


    def auto_add_dynamics(self):
        """
        Takes a completed self.note_array and adds spanners and dynamics
        :return: None
        """
        note_array_length = len(self.note_array.list)-1

        # Add dynamics #######
        # Add starting dynamic
        starting_dynamic = chance.rand.weighted_rand(
            [(0, 100), (2, 400), (4, 50), (6, 2), (9, 1)], do_round=True)
        list_of_dynamics = [(0, starting_dynamic)]  # list of tuples of form (attach index, dynamic_key)

        # Add tuples to list_of_dynamics
        for i in range(1, note_array_length - 1):
            # Find next dynamic attachee index based on previous tuple
            next_index = list_of_dynamics[i-1][0] + chance.rand.weighted_rand(
                [(1, 3), (6, 100), (10, 0)], do_round=True)
            if next_index > note_array_length - 1:
                break
            # Find next dynamic based on distance from previous dynamic
            next_dynamic = list_of_dynamics[i-1][1] + chance.rand.weighted_rand(
                [(-4, 1), (-1, 10), (0, 0), (1, 10), (4, 1)], do_round=True)
            if next_dynamic > 9:
                next_dynamic = 9
            elif next_dynamic < 0:
                next_dynamic = 0
            # To prevent dynamic repetition, reroll until next_dynamic is different than the previous dynamic
            while next_dynamic == list_of_dynamics[i-1][1]:
                next_dynamic = list_of_dynamics[i-1][1] + chance.rand.weighted_rand(
                    [(-4, 1), (-1, 10), (0, 0), (1, 10), (4, 1)], do_round=True)
            list_of_dynamics.append((next_index, next_dynamic))

        # Attach dynamics to Note instances in self.note_array.list
        for dynamic_tuple in list_of_dynamics:
            try:
                if not self.note_array.list[dynamic_tuple[0]].is_rest:
                    self.note_array.list[dynamic_tuple[0]].set_dynamic(dynamic_tuple[1])
            except IndexError:
                print(('Index Error in Instrument.auto_add_dynamics()' +
                      'while attaching dynamics to note instances, skipping this one...'))
                continue

        ############################### Build Hairpins ##################################

        def find_dynamic_beteen(note_array_instance, start_index, stop_index):
            # Returns the index of the left-most dynamic between two indices,
            # returns None if there are no dynamics between
            for test_index in range(start_index + 1, stop_index):
                try:
                    if note_array_instance.list[test_index].dynamic != '':
                        return test_index
                except IndexError:
                    return None
            else:
                return None

        # Randomly get number of hairpin counts based on a weighted rand within bounds of note_array_length
        if self.sustained_playing:
            hairpin_length_weights = [(1, 2), (4, 5), (7, 1), (9, 0)]
        else:
            hairpin_length_weights = [(3, 2), (4, 5), (7, 1), (9, 0)]
        hairpin_gap_weights = [(0, 6), (4, 2), (6, 1), (10, 3)]
        current_index = 0
        current_index += chance.rand.weighted_rand(hairpin_gap_weights, do_round=True)

        while current_index < note_array_length:

            # If we've reached the final real note (at [note_array_length - 1] )
            # and the note is very short, stop adding hairpins
            if (current_index == note_array_length - 1) and (self.note_array.list[current_index].length < 3):
                break

            # Find start_index
            start_index = current_index
            # Check that self.note_array[start_index] is not on a rest, moving forward 1 if so
            if self.note_array.list[start_index].is_rest:
                current_index += 1
                start_index = current_index

            # Find stop_index
            current_index += chance.rand.weighted_rand(hairpin_length_weights, do_round=True)
            # If needed, move stop_index left until there are no in-between dynamics
            between_index = find_dynamic_beteen(self.note_array, start_index, current_index)
            while between_index is not None:
                between_index = find_dynamic_beteen(self.note_array, start_index, current_index)
                if between_index is not None:
                    current_index = between_index
            stop_index = current_index
            # Check that self.note_array[start_index] is not AFTER a rest, moving back 1 if so
            try:
                if self.note_array.list[stop_index-1].is_rest:
                    current_index -= 1
                    stop_index = current_index
            except IndexError:
                stop_index = note_array_length - 1

            if start_index < 0:
                start_index = 0
            if stop_index > note_array_length: #################### used to test/put to note_array_length - 1
                stop_index = note_array_length

            ##################### Get hairpin direction #######################
            start_dynamic = None
            stop_dynamic = None

            def find_dynamic(note_array_instance, index, direction):
                # direction = 1 if searching rightward, -1 if searching leftward
                array_end_reached = False
                search_index = index
                while not array_end_reached:
                    try:
                        if note_array_instance.list[search_index].dynamic != '':
                            return note_array_instance.list[search_index].dynamic
                        search_index += direction
                    except IndexError:
                        array_end_reached = True
                return None

            if self.note_array.list[start_index].dynamic == '':
                start_dynamic = find_dynamic(self.note_array, start_index, -1)
            else:
                start_dynamic = self.note_array.list[start_index].dynamic

            if self.note_array.list[stop_index].dynamic == '':
                stop_dynamic = find_dynamic(self.note_array, stop_index, 1)
            else:
                stop_dynamic = self.note_array.list[stop_index].dynamic

            reverse_dynamic_dict = {'pppp': 0, 'ppp': 1, 'pp': 2, 'p': 3, 'mp': 4,
                                    'mf': 5, 'f': 6, 'ff': 7, 'fff': 8, 'ffff': 9}
            try:
                start_dynamic = reverse_dynamic_dict[start_dynamic]
            except KeyError:
                start_dynamic = random.randint(0, 9)

            try:
                stop_dynamic = reverse_dynamic_dict[stop_dynamic]
            except KeyError:
                stop_dynamic = random.randint(0, 9)

            if start_dynamic > stop_dynamic:
                # dim
                hairpin_direction = -1
            else:
                # cresc
                hairpin_direction = 1

            # Move forward for next hairpin start
            current_index += chance.rand.weighted_rand(hairpin_gap_weights, do_round=True)

            if start_index == stop_index:
                continue
            else:
                if self.note_array.approximate_distance(start_index, stop_index) < 9:
                    continue
                if hairpin_direction == -1:
                    self.note_array.create_spanner(start_index, stop_index, 'dim')
                else:
                    self.note_array.create_spanner(start_index, stop_index, 'cresc')

    def auto_add_slurs(self):
        # Set up variables and weights
        slur_length_weights = [(1, 2), (4, 3), (6, 1)]
        slur_gap_weights = [(0, 4), (2, 5), (12, 1)]
        current_index = 0
        note_array_length = len(self.note_array.list)
        while 1 == 1:
            # reset current_index
            # Move current_index forward by slur_gap_weights
            current_index += chance.rand.weighted_rand(slur_gap_weights, do_round=True)
            if current_index > note_array_length - 1:
                break
            if self.note_array.list[current_index].is_rest:
                current_index += 1
            slur_start = current_index
            # Find ideal stop_index based on slur_length_weights, snapping to before the first rest encountered (if any)
            ideal_stop_index = current_index + chance.rand.weighted_rand(slur_length_weights, do_round=True)
            if ideal_stop_index > note_array_length - 1:
                ideal_stop_index = note_array_length - 1
            while current_index < ideal_stop_index:
                current_index += 1
                if self.note_array.list[current_index].is_rest or (
                      self.note_array.list[current_index].pitch_num == self.note_array.list[current_index-1].pitch_num):
                    current_index -= 1
                    break
            slur_stop = current_index
            if current_index > note_array_length - 1:
                break
            else:
                if slur_start == slur_stop:
                    continue
                else:
                    self.note_array.create_spanner(slur_start, slur_stop, 'slur')

    @staticmethod
    def _find_first_pitch(pitch_set, percent_weights):
        """
        Takes a list of pitch slots and a list of percent weights and finds a pitch accordingly.
        Objects in percent_weights are tuples of the form (percent_along_pitch_set between 0.00 and 1.00, weight)
        :param pitch_set: list
        :param percent_weights: list of tuples which are proxy weights of form (percent_along_pitch_set, weight)
        :return: int pitch
        """
        import copy
        percent_weights = copy.copy(percent_weights)
        for i in range(0, len(percent_weights)):
            weight = percent_weights[i]
            assert isinstance(weight, tuple)
            new_x = int(round(weight[0] * len(pitch_set)))
            if weight[0] < 0:
                new_x = 0
            if weight[0] > len(pitch_set) - 1:
                new_x = len(pitch_set) - 1
            weight = (new_x, weight[1])
            percent_weights[i] = weight

        pitch_index = chance.rand.weighted_rand(percent_weights, do_round=True)
        try:
            return pitch_set[pitch_index]
        except IndexError:
            print(('IndexError in base_instrument.Instrument._find_first_pitch(): index of ' + str(pitch_index) +
                   ' is invalid! Using pitch_index of 0 instead...'))
            return pitch_set[0]

    def change_mode(self, mode_change_frequency=True, note_count_weights=True, natural_harmonic_frequency=True,
                    artificial_harmonic_frequency=True, chord_frequency=True, length_network=True):
        if mode_change_frequency:
            self.mode_change_frequency = round(random.uniform(0.01, 0.2), 3)
        if note_count_weights:
            self.note_count_weights = chance.rand.random_weight_list(1, random.randint(6, 15), 0.15)
        if natural_harmonic_frequency:
            self.natural_harmonic_frequency = round(random.uniform(0.04, 0.4), 3)
        if artificial_harmonic_frequency:
            self.artificial_harmonic_frequency = round(
                chance.rand.weighted_rand([(0.01, 150), (0.2, 20), (0.4, 5), (0.5, 1)]), 3)
        if chord_frequency:
            self.chord_frequency = round(chance.rand.weighted_rand([(0.01, 150), (0.1, 20), (0.2, 0)]), 3)
        if length_network:
            self.length_network.apply_noise(round(random.uniform(0.001, 0.05), 5))

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

        self.score.note_array = self.note_array
        output_ly_file = lily.lilypond_file.LilypondFile(self.score)
        output_file_name = self.instrument_name + '_' + str(shared.Globals.FileNameIndex)
        output_png = output_ly_file.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
        shared.Globals.FileNameIndex += 1
        return output_png

    def special_action_1(self):
        """
        Long accented single note on A or B with trailing dim hairpin
        :return: str - image path
        """
        self.refresh_lily()
        # Find pitch
        pitch_set = lily.note.extend_pitches_through_range([9, 11], self.lowest_note, self.highest_note)
        weighted_pitch_set = []
        i = 0
        while i < len(pitch_set):
            weighted_pitch_set.append((pitch_set[i], 10/(i+1)))
            i += 1
        use_pitch = chance.rand.weighted_rand(weighted_pitch_set, 'discreet')
        # Find length
        use_length = chance.rand.weighted_rand([(5, 2), (13, 8), (25, 1)], do_round=True)
        # Find dynamic
        use_dynamic = chance.rand.weighted_rand([(9, 1), (8, 7), (4, 5), (0, 1)], do_round=True)
        self.note_array.create_note(use_pitch, use_length, dynamic=use_dynamic)
        self.note_array.list[-1].add_articulation(1)
        if self.sustained_playing:
            self.note_array.create_spanner(0, spanner_type='dim', apply_type='start')

        if len(self.clef_list) > 1:
            self.note_array.auto_build_clefs(self.clef_list, self.initial_clef,
                                             self.clef_change_tolerance, self.preferred_clef_extra_weight)
        self.score.note_array = self.note_array
        output_ly_file = lily.lilypond_file.LilypondFile(self.score)
        output_file_name = self.instrument_name + '_' + str(shared.Globals.FileNameIndex)
        output_png = output_ly_file.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
        shared.Globals.FileNameIndex += 1
        return output_png

    def special_action_2(self):
        """
        Boxed text with special instructions
        :return:
        """
        draw_text = self.text_instruction_list[random.randint(0, len(self.text_instruction_list)-1)]
        return special_instructions.text_instructions.draw_boxed_text(draw_text[0], draw_text[1])

    def special_action_3(self):
        """
        Draws a big fermata with variable length
        :return:
        """
        return special_instructions.text_instructions.draw_big_fermata([(15, 1), (30, 8), (50, 2), (100, 0)])
