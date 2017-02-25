from here_the_leafsighaway.lily.note import Note


class Score:
    def __init__(self, note_array=None, indent=0):
        """
        :param note_array: Single instance of Note.NoteArray
        :param indent: Indent in mm
        :return:
        """
        self.indent = indent
        # Array of Note objects
        self.note_array = note_array
        self.master_string = ""
        self._lily_accidental_style = "dodecaphonic"
        self._lily_clef_offset_modifier = 0
        self._lily_shortest_duration_space = None
        self._lily_eraser_markup_width_offset = 0

    def format_string(self):
        # Format note strings if it hasn't been done yet
        # if not self.note_array.notes_formatted:
        self.note_array._eraser_markup_length_offset = self._lily_eraser_markup_width_offset
        self.note_array.format_note_strings()

        # Create the master string for the entire score block
        # Overwrite self.master_string (format_string replaces old name)
        self.master_string = ""
        # Open the block
        self.master_string += "\\score {\n"
        # Format layout block
        self.master_string += ("\t\\layout { indent = " + str(self.indent) + "\\mm }\n")
        # Populate the block
        # Open staff block
        self.master_string += '\t\\new Staff '
        if self.note_array.transposition_string != 'c':
            self.master_string += ("\\transpose " + self.note_array.transposition_string + "\n\n")
        # used to be \\time 24/1\n ----------------------------------------------------------
        self.master_string += ("{\\time 10/1\n" +
                                 "\\accidentalStyle " + self._lily_accidental_style + "\n" +
                                 "\\override DynamicText.self-alignment-X = #LEFT\n" +
                                 "\\override DynamicText.X-offset = #-0.8\n" +
                                 "\\override Staff.Clef.layer = #2\n" +
                                 "\\once \\override Staff.Clef.extra-offset = #'(" +
                                 str(0.9 + self._lily_clef_offset_modifier) + " . 0.)\n" +
                                 "\\override Stem.length = #0\n" +
                                 "\\override Staff.TimeSignature #'stencil = ##f\n" +
                                 "\\override Staff.StaffSymbol.layer = #-10\n")
        self.master_string += '\\clef "' + self.note_array.initial_clef + '"'
        if self._lily_shortest_duration_space is not None:
            self.master_string += ("\\override Score.SpacingSpanner.shortest-duration-space = #" +
                                  str(self._lily_shortest_duration_space) + "\n")
        # Populate all Note strings
        for note in self.note_array.list:
            assert isinstance(note, Note)
            self.master_string += note.note_string

        # Close the block
        self.master_string += "\n\t}\n}"

        # Return master string block
        return self.master_string
