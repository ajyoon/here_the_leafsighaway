import random


class Note:

    def __init__(self, pitch_num, length, x_offset=0, articulation_string="", dynamic="",
                 is_rest=False, is_artificial_harmonic=False, clef=None):
        self.pitch_num = pitch_num  # int or list of int's
        self.length = length
        self.x_offset = x_offset
        self.articulation_string = articulation_string
        self.is_rest = is_rest
        self.dynamic = dynamic
        self.dynamic_string = ""
        self.is_formatted = False
        self.pitch_string = ""
        self.commands_before = ""
        self.commands_after = ""
        self.note_string = ""
        self.is_artificial_harmonic = is_artificial_harmonic
        self.notehead_style_code = 0
        self.cross_notehead = False
        self.clef = clef
        self.is_parenthesized = False  # TODO: support note objects in parenthesis?

    def get(self):
        """returns tuple: pitchnum, length"""
        return self.pitch_num, self.length

    def set_dynamic(self, dynamic=2):
        """
        Overwrites current dynamic
        :param dynamic: int between 0 (pppp) and 9 (ffff)
        """
        if isinstance(dynamic, int):
            dynamic_dict = {0: 'pppp', 1: 'ppp', 2: 'pp', 3: 'p', 4: 'mp',
                            5: 'mf', 6: 'f', 7: 'ff', 8: 'fff', 9: 'ffff'}
            try:
                dynamic = dynamic_dict[dynamic]
            except KeyError:
                print(('Key Error in set_dynamic()! Bad value of ' +
                       str(dynamic) + ' was passed (should be between 0 and 9)'))
                return False
        self.dynamic = dynamic
        if self.dynamic != '':
            self.dynamic_string = ("\\" + dynamic + " ")

    def add_articulation(self, code, direction='default', is_raw_string=False):
        if is_raw_string:
            assert isinstance(code, str)
            self.articulation_string += code
            return
        else:
            if code == 0:
                return
            code_dict = {0: '', 1: 'accent', 2: 'marcato',
                         3: 'tenuto', 4: 'staccato', 5: 'staccatissimo',
                         100: 'upbow', 101: 'downbow', 103: 'open', 104: 'snappizzicato', 105: 'flageolet',
                         200: 'pizz', 201: 'arco', 202: '\\italic{con sord}', 203: '\\italic{senza sord}',
                         204: '\\italic{straight mute}', 205: '\\italic{practice mute}',
                         220: '\\center-align I', 221: '\\center-align II', 222: '\\center-align III',
                         223: '\\center-align IV', 224: '\\center-align V', 225: '\\center-align VI',
                         230: 'hard yarn', 231: 'soft yarn', 232: 'soft rubber',
                         500: 'stopped'
                         }
            direction_dict = {'over': '^',
                              'under': '_',
                              'default': '-'}
            assert isinstance(code, int)
            assert code in code_dict
            assert direction in direction_dict
            # For non-text-markup codes, use slash syntax
            if not (200 <= code < 300):
                new_articulation_string = direction_dict[direction] + "\\" + code_dict[code]
            # For text-markup codes (those between 200 and 300), use markup syntax
            else:
                # Special offset for string indicator markups
                if 220 <= code <= 225:
                    markup_offset = 0.4
                else:
                    markup_offset = 0
                self.commands_before += ('\\once \\override TextScript.X-offset = #' +
                                         str(self.x_offset + markup_offset) + ' ')
                new_articulation_string = (direction_dict[direction] + '\\markup {' + code_dict[code] + '}')
            self.articulation_string += new_articulation_string

    def get_notehead_style_string(self):
        # Regular style, return emtpy string
        if self.notehead_style_code == 0:
            return ''
        # Cross notehead style
        elif self.notehead_style_code == 1:
            return "\\once \\override NoteHead.style = #'cross"
        # Diamond notehead style
        elif self.notehead_style_code == 2:
            return "\\once \\override NoteHead.style = #'harmonic"
        # Open notehead style
        elif self.notehead_style_code == 3:
            return "\\OpenNotehead"
        # Square notehead style
        elif self.notehead_style_code == 4:
            return "\\SquareNotehead"

    def combine_components(self):
        self.note_string = (self.commands_before +
                            self.pitch_string +
                            self.dynamic_string +
                            self.articulation_string +
                            self.commands_after)
        self.is_formatted = True
        return self.note_string


def eraser_markup(width, start_x=0, start_y=12, height=20):
    extra_width = 1.5
    width += extra_width
    debug = False
    box_color = "1 1 1"
    if debug:
        c_r = random.randint(800, 1000) / 1000.0
        c_g = random.randint(800, 1000) / 1000.0
        c_b = random.randint(800, 1000) / 1000.0
        box_color = str(c_r) + " " + str(c_g) + " " + str(c_b)
    # TODO: find a way to avoid the markup moving vertically with the notehead?
    string = ("-\\tweak layer #0  -\\markup {\n" +
              "\\postscript\n" +
              "#\"\n" +
              "newpath\n" +
              str(start_x) + " " + str(start_y) + " moveto\n" +
              str(start_x) + " " + str(start_y - height) + " lineto\n" +
              str(start_x + width) + " " + str(start_y - height) + " lineto\n" +
              str(start_x + width) + " " + str(start_y) + " lineto\n" +
              "closepath\n" +
              box_color + " setrgbcolor\n" +
              "fill\n" +
              "\"\n" +
              "}\n\n"
              )
    return string


def staff_connector_line(height=20):
    start_x = -0.1
    start_y = -5
    width = 0.1
    box_color = "0 0 0"
    string = ("^\\tweak layer #1  ^\\markup {\n" +
              "\\postscript\n" +
              "#\"\n" +
              "newpath\n" +
              str(start_x) + " " + str(start_y) + " moveto\n" +
              str(start_x) + " " + str(start_y + height) + " lineto\n" +
              str(start_x + width) + " " + str(start_y + height) + " lineto\n" +
              str(start_x + width) + " " + str(start_y) + " lineto\n" +
              "closepath\n" +
              box_color + " setrgbcolor\n" +
              "fill\n" +
              "\"\n" +
              "}\n\n"
              )
    return string


def find_pitch_class(pitch):
    """
    Finds the 0-11 pitch class of any pitch
    :param pitch: int
    :return:int pitch class of 0-11
    """
    if pitch <= 0:
        direction = 1
    else:
        direction = -1
    while not (0 <= pitch <= 11):
        pitch += direction * 12
    return pitch


def get_pitch_string(pitch_num, mode='sharp'):
    """
    Takes a given pitch_num and returns a lilypond-ready pitch string
    (it's possible to have a higher-up algorithm analyze a passage and pass mixed modes to this within a passage)
    :param pitch_num: int
    :param mode: str 'sharp' or 'flat' (will default to 'flat' if invalid)
    :return: str
    """
    # Middle C is index 0, which should be represented in a lilypond string as c'
    # Adjust pitch num by adding 12 to reconcile the difference for easy divmod manipulation later
    adjusted_pitch_num = pitch_num + 12

    sharp_pitch_dict = {0: 'c', 1: 'cs', 2: 'd', 3: 'ds', 4: 'e', 5: 'f',
                        6: 'fs', 7: 'g', 8: 'gs', 9: 'a', 10: 'as', 11: 'b'}
    flat_pitch_dict = {0: 'c', 1: 'df', 2: 'd', 3: 'ef', 4: 'e', 5: 'f',
                        6: 'gf', 7: 'g', 8: 'af', 9: 'a', 10: 'bf', 11: 'b'}
    if mode == 'sharp':
        base_string = sharp_pitch_dict[find_pitch_class(adjusted_pitch_num)]
    else:
        base_string = flat_pitch_dict[find_pitch_class(adjusted_pitch_num)]

    if adjusted_pitch_num > 0:
        ticks_num = divmod(adjusted_pitch_num, 12)[0]
    else:
        ticks_num = divmod(adjusted_pitch_num, -12)[0]
    if adjusted_pitch_num > 0:
        tick_string = "'" * ticks_num
    else:
        tick_string = "," * ticks_num
    out_string = base_string + tick_string
    return out_string



def extend_pitches_through_range(pitch_class_list, lowest, highest):
    """
    Takes a list of pitch classes (int's between 0 and 11) and transposes and extends it through the window given
    :param pitch_class_list: list of int's
    :param min: int
    :param max: int
    :return: extended list
    """
    assert isinstance(pitch_class_list, list)
    full_range = list(range(lowest, highest))
    return_list = []
    for pitch in full_range:
        if find_pitch_class(pitch) in pitch_class_list:
            return_list.append(pitch)
    return return_list

class NoteArray:
    def __init__(self, input_list=None, initial_clef='treble', transposition_int=0):
        self.list = input_list
        if self.list is None:
            self.list = []
        self.cumulative_length = 0
        self.max_length = 180
        self.notes_formatted = False
        self.initial_clef = initial_clef
        self.transposition_int = transposition_int
        self._eraser_markup_length_offset = 0

        # Set up transposition_string
        self.transposition_string = "c'"
        if transposition_int == -2:
            self.transposition_string = "bf"
        elif transposition_int == -5:
            self.transposition_string = "g"
        elif transposition_int == -7:
            self.transposition_string = "f"
        elif transposition_int == -12:
            self.transposition_string = "c"
        elif transposition_int == -14:
            self.transposition_string = "bf,"
        else:
            if transposition_int != 0:
                print('WARNING: in NoteArray.__init__(), transposition_int of ' + str(transposition_int) + \
                      ' is unsupported, defaulting to 0')
        self.transposition_string += " c'"

    def format_note_strings(self):

        if self.notes_formatted:
            print("WARNING, NoteArray.format_note_strings can only be called once. Ignoring call.")
            return False

        # If the last note in the list is a rest, just remove it
        if self.list[-1].is_rest:
            self.list = self.list[:-1]

        # Append the final invisible rest which extends the staff to the length needed by the final note
        # (use the direct append method instead of add_note() to avoid cumulative length check
        self.list.append(Note(0, 6, articulation_string='\\!', is_rest=True))

        i = 0
        x_offset = 0
        while i < len(self.list):

            assert isinstance(self.list[i], Note)
            # If this isn't the first note, set the x_offset to last note's length
            if i != 0:
                x_offset = self.list[i - 1].length
                # If this is the last note, subtract 1 from x_offset
                if i == len(self.list) - 1:
                    x_offset -= 1
            # If it IS the first note, do some initial string building
            else:
                if self.list[i].is_rest:
                    print("WARNING: First note in a staff is a rest. Ignoring...")
                    i += 1
                    continue
                self.list[i].commands_after += eraser_markup(5.7, -7.5)

            if not self.list[i].is_rest:
                # If it's not a rest, set note offset and super high layer
                self.list[i].commands_before += ("\\once \\override NoteColumn.X-offset = #" + str(x_offset) + " " +
                                                 "\\tweak layer #100\n")
                self.list[i].commands_before += self.list[i].get_notehead_style_string() + ' '

            else:
                # If this note IS a rest
                # Change pitch to match the pitch of previous note to prevent weird clef changes & such
                self.list[i].pitch_num = self.list[i - 1].pitch_num
                # Set x-offset and hide notehead & ledgers
                self.list[i].commands_before += ("\\once \\override NoteColumn.X-offset = #" + str(x_offset-1.1) + " " +
                                                 "\\once \\override NoteHead.transparent = ##t " +
                                                 "\\once \\override NoteHead.no-ledgers = ##t " +
                                                 "\\once \\override Accidental.stencil = ##f")
                eraser_markup_x_pos = x_offset
                # If this is the final dummy eraser-rest, push eraser markup forward a bit to cancel out
                # the x_offset change at the top of the While loop
                if i == len(self.list) - 1:
                    eraser_markup_x_pos += 1.25
                # Draw eraser markup
                self.list[i].commands_after += eraser_markup(
                    self.list[i].length + self._eraser_markup_length_offset, eraser_markup_x_pos)

            if self.list[i].clef is not None:
                self.create_clef(self.list[i].clef, True, i)

            # Format pitch strings. If a pitch is a list instead of int, use < > notation to build a chord
            if isinstance(self.list[i].pitch_num, int):
                # self.list[i].pitch_string = NumberedPitch(self.list[i].pitch_num).pitch_name
                self.list[i].pitch_string = get_pitch_string(self.list[i].pitch_num)
                if self.list[i].is_artificial_harmonic:
                    self.list[i].pitch_string = '<' + self.list[i].pitch_string + '\\harmonic>'
            elif isinstance(self.list[i].pitch_num, list):
                if not self.list[i].is_artificial_harmonic:
                    self.list[i].pitch_string = "<"
                    for t_pitch_num in self.list[i].pitch_num:
                        # self.list[i].pitch_string += (NumberedPitch(t_pitch_num).pitch_name + " ")
                        self.list[i].pitch_string += (get_pitch_string(t_pitch_num) + " ")
                    self.list[i].pitch_string += ">"
                else:
                    # If this note is an artificial harmonic, build the pitch string accordingly
                    # Make sure exactly 2 notes are passed, otherwise print a warning
                    if len(self.list[i].pitch_num) != 2:
                        print(('WARNING, artificial-harmonic-flagged note group is being passed ' +
                               'to format_note_strings() with ' + str(len(self.list[i].pitch_num)) +
                               ' (not 2), \n\t\tignoring notes above first 2...'))
                    # sort self.list[i].pitch_num so that top note gets diamond shape
                    self.list[i].pitch_num = sorted(self.list[i].pitch_num)
                    # build string for first note
                    # self.list[i].pitch_string = ("<" + NumberedPitch(self.list[i].pitch_num[0]).pitch_name + ' ' +
                    #                              NumberedPitch(self.list[i].pitch_num[1]).pitch_name + '\\harmonic>')
                    self.list[i].pitch_string = ("<" + get_pitch_string(self.list[i].pitch_num[0]) + ' ' +
                                                 get_pitch_string(self.list[i].pitch_num[1]) + '\\harmonic>')
            """
            # Format dynamic strings   CUT??????????
            self.list[i].set_dynamic(self.list[i].dynamic)
            """
            self.list[i].combine_components()
            i += 1

        self.notes_formatted = True

    def add_note(self, note):
        """
        All note adds should run through here!
        :param note: existing Note object
        :return:
        """
        # Check that adding this note won't overrun the cumulative length
        if (self.cumulative_length + note.length) > self.max_length:
            print("WARNING: Adding this note exceeds staff length, ignoring...")
            return False
        self.list.append(note)
        self.set_cumulative_length()
        return True

    def create_note(self, pitch_num, length, x_offset=None, articulation_string="", dynamic="", is_rest=False):
        # Find x_offset if it wasn't passed
        if x_offset is None:
            if len(self.list) == 0:
                x_offset = 0
            else:
                x_offset = self.list[-1].length
        new_note = Note(pitch_num, length, x_offset=x_offset,
                        articulation_string=articulation_string, is_rest=is_rest)
        if dynamic != "":
            new_note.set_dynamic(dynamic)
        self.add_note(new_note)

    def create_rest(self, length, x_offset=0):
        self.create_note(0, length, is_rest=True)

    def create_spanner(self, start_index=None, stop_index=None, spanner_type='cresc', apply_type='both'):
        """
        Can either create a complete spanner, only open one, or only close one. If no index is specified,
        attaches to the last added note
        :param start_index: NoteArray.list index to begin spanner
        :param stop_index: NoteArray.list index to close spanner
        :param spanner_type: String of either 'cresc' 'dim' or 'slur'
        :param apply_type: String of either 'start' 'stop' or 'both'
        :return:
        """
        if start_index is None:
            start_index = -1
        if stop_index is None:
            stop_index = -1
        if apply_type == 'both' and start_index == stop_index:
            print("WARNING: trying to add a spanner starting and stopping at the same index. Ignoring...")
            return False

        # Adjust start and stop indexes to prevent IndexErrors
        if start_index < 0:
            start_index = 0
        if stop_index >= len(self.list):
            stop_index = -1
        # Handling for octave transpositions first
        if spanner_type == '8va' or spanner_type == '8vb' or spanner_type == '0va':
            start_command_string = ""
            stop_command_string = "\\ottava #0 "
            if spanner_type == '8va':
                start_command_string = '\\ottava #1 '
            elif spanner_type == '8vb':
                start_command_string = '\\ottava #-1 '
            elif spanner_type == '0va':
                start_command_string = '\\ottava #0 '
            if apply_type == 'both' or apply_type == 'start':
                self.list[start_index].commands_before += start_command_string
            if apply_type == 'both' or apply_type == 'stop':
                self.list[stop_index].commands_after += stop_command_string
            return True
        else:
            start_types = {'cresc': '\\<',
                           'dim': '\\>',
                           'slur': '('}
            stop_types = {'cresc': '\\!',
                          'dim': '\\!',
                          'slur': ')'}
            if apply_type == 'both' or apply_type == 'start':
                self.list[start_index].articulation_string += start_types[spanner_type]
            if apply_type == 'both' or apply_type == 'stop':
                self.list[stop_index].articulation_string += stop_types[spanner_type]
            return True

    def create_clef(self, clef_type='treble', place_before=False, index=None):
        """
        Adds a clef. If no index is specified, clef goes after the last entered note
        :param clef_type: String 'treble' 'bass' 'tenor' or 'alto'
        :param index: NoteArray.list index
        :return:
        """
        if index is None:
            index = -1

        clef_command = ""
        # In order to prevent weird clef placement in non-default first clefs, only do clef offset if index isn't 0
        if index != 0:
            clef_command = ("\\once \\override Staff.Clef.extra-offset = #'(" +
                            str(self.list[index].x_offset - 0.5) + " . 0.) ")
        clef_command += '\\clef "' + clef_type + '" '

        if place_before:
            self.list[index].commands_before += clef_command
        else:
            self.list[index].commands_after += clef_command

    def set_cumulative_length(self):
        length = 0
        for x in self.list:
            length += (x.length + 1)
        self.cumulative_length = length
        return length

    def approximate_distance(self, index_1, index_2):
        distance = 0
        try:
            for index in range(index_1, index_2):
                distance += 1
                distance += self.list[index].x_offset
            return distance
        except IndexError:
            print('Invalid index being passed to NoteArray.approximate_distance(), returning 0')
            return 0

    def print_array(self, verbose=False):
        # Print the array's contents for debugging purposes

        if not self.notes_formatted:
            self.format_note_strings()  # Make sure notes are formatted

        print("Array Contents:\n -------------\n")
        x = 0
        extra_string = ""
        while x < len(self.list):
            if verbose:
                extra_string = ("\nCommands before: \n" + self.list[x].commands_before + "\n\n" +
                                "Commands after: \n" + self.list[x].commands_after + "\n\n")
            print(("Index " + str(x) + " ::::::::::::::::::::::::::::::::::\n" +
                   "Is Rest: " + str(self.list[x].is_rest) + "\n" +
                   "Pitch Number: " + str(self.list[x].pitch_num) + ", Pitch String: " + str(
                self.list[x].pitch_string) +
                   "Length: " + str(self.list[x].length) + "\n" +
                   "Articulation String: " + str(self.list[x].articulation_string) + "\n" +
                   "Dynamic String: " + str(self.list[x].dynamic_string) + extra_string + "\n:::::::::::::::::::\n"))
            x += 1

    def auto_build_clefs(self, clef_options, preferred_clef, tolerance=3, preferred_clef_extra_weight=4):
        """
        Goes through self.list[] and changes clefs where necessary.
        :param clef_options: list of str objects - MUST BE in ascending order from lowest to highest clef
        :param preferred_clef: str of preferred clef
        :return: True if successful, False if not
        """
        list_of_clefs = ['bass', 'tenor', 'alto', 'treble']
        for option in clef_options:
            if not option in list_of_clefs:
                print('Warning - clef_options in NoteArray.auto_build_clefs() contains ' + option + ', ignoring...')
                return False
        if (preferred_clef not in list_of_clefs) or (preferred_clef not in clef_options):
            print('Warning - preferred_clef in NoteArray.auto_build_clefs() is ' + preferred_clef + ', ignoring...')

        class WeightedClef:
            def __init__(self, clef_name, lowest_comfortable=4, highest_comfortable=17, weight=1):
                self.clef_string = clef_name
                self.lowest_comfortable = lowest_comfortable
                self.highest_comfortable = highest_comfortable
                self.weight = weight

        # Initialize usable_clef_list as a list of WeightedClef options derived from clef_options
        usable_clef_list = []
        for clef_string in clef_options:
            usable_clef_list.append(WeightedClef(clef_string))
            if clef_string == 'treble':
                usable_clef_list[-1].lowest_comfortable = -3
                usable_clef_list[-1].highest_comfortable = 24
                if preferred_clef == 'treble':
                    usable_clef_list[-1].weight = preferred_clef_extra_weight
            elif clef_string == 'alto':
                usable_clef_list[-1].lowest_comfortable = -12
                usable_clef_list[-1].highest_comfortable = 10
                if preferred_clef == 'alto':
                    usable_clef_list[-1].weight = preferred_clef_extra_weight
            elif clef_string == 'tenor':
                usable_clef_list[-1].lowest_comfortable = -7
                usable_clef_list[-1].highest_comfortable = 7
                if preferred_clef == 'tenor':
                    usable_clef_list[-1].weight = preferred_clef_extra_weight
            elif clef_string == 'bass':
                usable_clef_list[-1].lowest_comfortable = -32
                usable_clef_list[-1].highest_comfortable = 3
                if preferred_clef == 'bass':
                    usable_clef_list[-1].weight = preferred_clef_extra_weight

        # Find the NoteArray's initial_clef in usable_clef_list, defaulting to usable_clef_list[0] if not found
        for usable_clef in usable_clef_list:
            if usable_clef.clef_string == self.initial_clef:
                current_clef = usable_clef
                break
        else:
            print("Warning in NoteArray.auto_build_clefs(): NoteArray.initial_clef wasn't found in usable_clef_list, " \
                  "defaulting to first item in usable_clef_list")
            current_clef = usable_clef_list[0]

        # iterate through self.list[], creating clefs when a note's pitch_num is outside the comfortable range
        # by more than (WeightedClef.weight + tolerance) and there is another clef to move to in the correct direction
        i = 0
        # while i < (len(self.list) - 1): USED TO BE THIS INSTEAD ###########################################
        while i < len(self.list):
            # Make sure that the pitch_num being tested is an int, not a list
            # Things like this are why it's probably a good reason to move toward
            # generalizing Note.pitch_num into a list everywhere
            if isinstance(self.list[i].pitch_num, list):
                # if the current_clef is the lowest clef in usable_clef_list, test the upper pitch
                if usable_clef_list.index(current_clef) == 0:
                    testing_pitch = self.list[i].pitch_num[-1]
                # otherwise test the highest pitch
                else:
                    testing_pitch = self.list[i].pitch_num[0]
            else:
                testing_pitch = self.list[i].pitch_num
            # Adjust every note's pitch according to self.transposition_int for transposed instruments
            adjusted_pitch_num = testing_pitch - self.transposition_int
            if (adjusted_pitch_num > (current_clef.highest_comfortable + current_clef.weight + tolerance)) and (
                                                    usable_clef_list.index(current_clef) < len(usable_clef_list) - 1):
                current_clef = usable_clef_list[usable_clef_list.index(current_clef) + 1]
                self.list[i].clef = current_clef.clef_string
            elif(adjusted_pitch_num < (current_clef.lowest_comfortable - current_clef.weight - tolerance)) and (
                                                         usable_clef_list.index(current_clef) > 0):
                current_clef = usable_clef_list[usable_clef_list.index(current_clef) - 1]
                self.list[i].clef = current_clef.clef_string

            i += 1

    def auto_build_octave_spanners(self, highest_pitch=28, tolerance=4):
        """
        Automatically adds 8va spanners for pitches above or below highst_pitch +/- tolerance
        :param highest_pitch: int
        :param tolerance: int
        :return:
        """

        i = 0
        currently_transposed = False
        while i < len(self.list):
            if isinstance(self.list[i].pitch_num, int):
                test_pitch = self.list[i].pitch_num
            else:
                test_pitch = sorted(self.list[i].pitch_num)[-1]
            if (test_pitch > highest_pitch + tolerance) and not currently_transposed:
                currently_transposed = not currently_transposed
                self.create_spanner(start_index=i, spanner_type='8va', apply_type='start')
            elif (test_pitch < highest_pitch - tolerance) and currently_transposed:
                currently_transposed = not currently_transposed
                self.create_spanner(start_index=i, spanner_type='0va', apply_type='start')

            i += 1
