import os
import subprocess

from here_the_leafsighaway import image_trimmer
from here_the_leafsighaway.lily import note, score
from here_the_leafsighaway import config


class LilypondFile:
    def __init__(self, contents=None):
        self.top_elements = [
            '\\version "2.18.2"',
            '\language "english"',
            '#(set-default-paper-size "CustomLong" \'portrait)'
        ]
        self.top = ""
        self.header_elements = [
            'tagline = #" "'
        ]
        self.header = ""
        self.paper_elements = []
        self.paper = ""
        self.paper_width = 180  # in mm
        self.paper_height = 45  # in mm
        self.score_list = []
        self.score = ""
        self.file_string = ""
        self._is_formatted = False
        self._string_built = False
        self.master_string = ""
        # self.set_paper_size(self.paper_width, self.paper_height)

        # Initialize contents if passed
        if contents:
            if isinstance(contents, score.Score):
                self.add_score(contents)  # Attach a score if one was given
            elif isinstance(contents, note.NoteArray):
                self.add_score(score.Score(contents))
            elif isinstance(contents, note.Note):
                t_array = note.NoteArray(note.Note)
                self.add_score(score.Score(t_array))
            else:
                print("WARNING: Unrecognized content being passed to LilypondFile, ignoring...")

    def set_paper_size(self, width, height):
        """
        :param width: Paper width in mm
        :param height: Paper height in mm
        :return:
        """
        top_string = ("#(set! paper-alist (cons '(\"CustomSize\" . " +
                      "(cons (* " + str(width) + " mm) (* " + str(height) + " mm))) paper-alist)) ")
        self.add_top_line(top_string)
        self.add_top_line("#(set-global-staff-size 16)")
        self.add_paper_line("#(set-paper-size \"CustomSize\")")

    def set_up_special_notehead_functions(self, square_notes=True, open_notes=True):
        """
        Defines special commands to top_elements which set up functions within lilypond.
        \SquareNoteHead makes the next note a solid square, \OpenNoteHead makes the next note a regular open note head
        :param square_notes: bool
        :param open_notes: bool
        :return:
        """

        if square_notes:
            self.add_top_line('SquareNotehead = { \\once \\override NoteHead.stencil = #ly:text-interface::print\n' +
                              '\\once \\override NoteHead.text = \\markup { \n\\postscript'
                              '#" newpath 0 .45 moveto 0 -.45 lineto 0.9 -.45 lineto 0.9 .45 lineto closepath '
                              '0 0 0 setrgbcolor fill " } }')
        if open_notes:
            self.add_top_line('OpenNotehead = { \\once \\override NoteHead.stencil = #ly:text-interface::print\n' +
                              '\\once \\override NoteHead.text = \\markup { \\musicglyph #"noteheads.s1" } }')
        if (not square_notes) and (not open_notes):
            print('Neither the square note or open note functions have been '
                  'requested in LilypondFile.set_up_special_noteheads(), ignoring!')
            return None

        # Return true if everything went well
        return True

    def add_top_line(self, string):
        self.top_elements.append(string)

    def add_header_line(self, string):
        self.header_elements.append(string)

    def add_paper_line(self, string):
        self.paper_elements.append(string)

    def add_score(self, score):
        self.score_list.append(score)

    def format_elements(self):

        # Initial setup
        self.set_paper_size(self.paper_width, self.paper_height)
        self.set_up_special_notehead_functions()

        # Top-level elements
        for x in range(0, len(self.top_elements)):
            self.top += self.top_elements[x]
            if not self.top.endswith('\n'):
                self.top += "\n"
        # Header block
        # Open block
        self.header += "\header { \n"
        # Fill block body
        for x in range(0, len(self.header_elements)):
            self.header += ("\t" + self.header_elements[x])
            self.header += "\n"
        # Close block
        self.header += "}\n\n"

        # Paper block
        # Open block
        self.paper += "\paper { \n"
        # Fill block body
        # self.paper += '''#(define fonts
        #                     (set-global-fonts
        #                       #:music "lilyboulez"
        #                       #:factor (/ staff-height pt 20)
        #                      ))'''  # Turn on lilyboulez font    ######### ^ used to be pt 20
        for x in range(0, len(self.paper_elements)):
            self.paper += ("\t" + self.paper_elements[x])
            if self.paper[-2:] != "\n":
                self.paper += "\n"
        # Close block
        self.paper += "}\n\n"

        # Score block  ---- probably will need to be handled very differently
        for x in range(0, len(self.score_list)):
            self.score += self.score_list[x].format_string()

        self._is_formatted = True

    def create_string(self):

        if not self._is_formatted:
            self.format_elements()

        master_string = (self.top +
                         self.header +
                         self.paper +
                         self.score)

        self._string_built = True
        self.master_string = master_string
        return master_string

    def save_file(self, target_ly_file):
        """
        Takes a name for an output ly file and saves it, building the file's master_string if needed
        :param target_ly_file: str file name for new .ly file
        :return: full path to new .ly file
        """
        if not target_ly_file.endswith('.ly'):
            target_ly_file += '.ly'
        if not self._string_built:
            self.create_string()
        output_path = os.path.join(config.ResourcesFolder, 'temp', 'lily', target_ly_file)
        new_file = open(output_path, 'w')
        new_file.write(self.master_string)
        new_file.close()
        return output_path

    @staticmethod
    def render_file(path):
        """
        Takes a path to a .ly file and renders it with lilypond to PNG
        :param path: str pointing to an existing .ly file
        :return: str of new PNG file path
        """
        if not path.endswith('.ly'):
            path += '.ly'
        if not os.path.exists(path):
            raise ValueError('Path % does not exist' % path)

        subprocess.call(["lilypond", "--png", "-dresolution=" + str(config.ImageDPI), path],
                        cwd=os.path.dirname(path))

        # Return the newly-created PNG file path
        return path[:-3] + '.png'

    def save_and_render(self, name, view_image=False, autocrop=True, delete_ly=False):
        """
        Saves and renders the LilypondFile to name where name is the name of the output .ly and .png file.
        Returns a full path to the newly built .png file
        :param name: str optionally ending in .ly
        :param view_image: Bool
        :param autocrop: Bool
        :param delete_ly: Bool
        :return: str
        """
        if not self._string_built:
            self.create_string()
        ly_file = self.save_file(name)
        png_file = self.render_file(ly_file)
        if delete_ly:
            subprocess.call(['del', ly_file], shell=True)
        if autocrop:
            image_trimmer.trim(png_file)
        if view_image:
            subprocess.call(["start", '', png_file], shell=True)
        return png_file
