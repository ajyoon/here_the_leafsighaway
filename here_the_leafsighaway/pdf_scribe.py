import os
import random

import PIL.Image
import reportlab.lib.enums
import reportlab.lib.styles
import reportlab.pdfgen.canvas
import reportlab.platypus
import reportlab.rl_config
from reportlab.lib.units import inch as rl_inch

from here_the_leafsighaway import config
from here_the_leafsighaway import document_tools
from here_the_leafsighaway.chance import (network,
                                          nodes,
                                          prebuilt_networks,
                                          rand)
from here_the_leafsighaway.instruments import (
    guitar,
    toy_piano,
    trumpet,
    viola,
    bassoon,
    bass,
    horn,
    speaker,
    oboe,
    cello,
    clarinet,
    audience,
    flute,
    trombone,
    violin,
    percussion)


class TextUnit:
    def __init__(self, text, italicized=False, bold=False):
        if isinstance(text, nodes.Word):
            self.text = text.name
            # TODO: make chance.nodes.Word class carry a italic & bold property passable to here?
        else:
            self.text = text
            self.italic = italicized
            self.bold = bold


class Paragraph:
    def __init__(self, contents=None, left_indent=0, right_indent=0, alignment='LEFT'):
        if isinstance(contents, list):
            self.contents = contents
        else:
            self.contents = []
        self.left_indent = left_indent
        self.right_indent = right_indent
        self.alignment = alignment

    def tweak_indent(self):

        if self.left_indent > (config.DocWorkingWidth - self.right_indent - config.MinColumnWidth):
            self.left_indent = (config.DocWorkingWidth - self.right_indent - config.MinColumnWidth)
        if self.left_indent > config.DocWorkingWidth - config.MinColumnWidth:
            self.left_indent = config.DocWorkingWidth - config.MinColumnWidth - 25
        if config.DocWorkingWidth - self.left_indent - self.right_indent < config.MinColumnWidth:
            self.left_indent -= config.MinColumnWidth
            self.right_indent -= config.MinColumnWidth
        if self.left_indent < 0:
            self.left_indent = random.randint(0, 15)
            self.right_indent -= self.left_indent
        if config.DocWorkingWidth - self.right_indent < self.left_indent:
            self.right_indent = config.DocWorkingWidth - self.left_indent - config.MinColumnWidth - 1
        if self.right_indent < 0:
            self.right_indent = 0

    def add_text_unit(self, text_unit):
        """
        Adds inputted TextUnit or chance.nodes.Word instance to self.contents
        :param text_unit: TextUnit or chance.nodes.Word instance
        """
        assert isinstance(text_unit, TextUnit)
        self.contents.append(text_unit)

    def add_to_doc(self, flowable_list, base_style):

        self.tweak_indent()
        if self.alignment == 'LEFT':
            alignment_code = 0
        elif self.alignment == 'CENTER':
            alignment_code = 1
        elif self.alignment == 'RIGHT':
            alignment_code = 2
        elif self.alignment == 'JUSTIFY':
            alignment_code = 4
        else:
            print("Warning: unmatched alignment being passed to TextLine.add_to_doc()")
            alignment_code = 0

        # Assemble the paragraph string based on self.contents, adding bold & italic runs where called for
        paragraph_string = ''
        for element in self.contents:
            if isinstance(element, nodes.Word):
                element = TextUnit(element.name)
            elif isinstance(element, str):
                element = TextUnit(element)
            assert isinstance(element.text, str)
            run_text = element.text
            # new_run = new_line.add_run(element.text)
            if element.bold and not element.italic:
                run_text = '<b>' + run_text + '</b>'
            elif element.italic and not element.bold:
                run_text = '<i>' + run_text + '</i>'
            elif element.italic and element.bold:
                run_text = '<i><b>' + run_text + '</b></i>'
            if element.text == '\n':
                run_text = '<br/>'
            paragraph_string += run_text

        # If an empty paragraph is being used, add a blank line in the form of a reportlab.platypus.Spacer
        # sized to the global fontsize, and return
        if paragraph_string == '':
            # paragraph_string = '---'
            flowable_list.append(reportlab.platypus.Spacer(16, config.FontSize))
            return

        # (Otherwise, if text was passed)
        # Build the paragraph style to pass to the paragraph object
        style = reportlab.lib.styles.ParagraphStyle(name='modified paragraph style', parent=base_style,
                                                    leftIndent=self.left_indent, rightIndent=self.right_indent,
                                                    alignment=alignment_code)

        # Create the paragraph object and sent it to flowable_list
        flowable_list.append(reportlab.platypus.Paragraph(paragraph_string, style))
        return


class OffsetImage(reportlab.platypus.Image):
    """
    A simple override for reportlab.platypus.Image which does all the same things except allows a forced additional
    x_offset and y_offset to be defined in reportlab's 72-dpi point units. The offsets are applied in ADDITION
    to whatever position the typical reportlab.platypus.Image would be given (taking into account flowable positioning
    and alignment), meaning hAlign is still meaningful, though it is perhaps most intuitive to use hAlign='LEFT'
    and set x_offset to the unit distance from the left margin you want it to be drawn.
    """
    def __init__(self, filename, width=None, height=None, kind='direct', mask="auto", lazy=1, hAlign='CENTER',
                 x_offset=0, y_offset=0):
        reportlab.platypus.Image.__init__(self, filename, width=width, height=height, kind=kind, mask=mask,
                                          lazy=lazy, hAlign=hAlign)
        self.x_offset = x_offset
        self.y_offset = y_offset

    def draw(self):
        lazy = self._lazy
        if lazy >= 2:
            self._lazy = 1
        self.canv.drawImage(self._img or self.filename,
                            getattr(self, '_offs_x', 0) + self.x_offset,  # Add extra self.x_offset
                            getattr(self, '_offs_y', 0) + self.y_offset,  # Add extra self.y_offset
                            self.drawWidth,
                            self.drawHeight,
                            mask=self._mask,
                            )
        if lazy >= 2:
            self._img = self._file = None
            self._lazy = lazy


class InlineImage:
    def __init__(self, file_path, height=None, left_indent=0, right_indent=0,
                 alignment='LEFT', y_padding=16):
        self.file_path = file_path
        self.left_indent = left_indent
        self.right_indent = right_indent
        self.alignment = alignment
        self.height = height
        self.y_padding = y_padding

        # Find image width and height in 72-dpi-points (resolution of ReportLab) using PIL
        image_pix_width, image_pix_height = PIL.Image.open(self.file_path).size
        self.width = round((72.0 * image_pix_width) / config.ImageDPI, 3)
        self.height = round((72.0 * image_pix_height) / config.ImageDPI, 3)

        # default any non-left-or-right alignments randomly to either left or right
        if not (self.alignment == 'LEFT' or self.alignment == 'RIGHT'):
            if random.randint(0, 1) == 0:
                self.alignment = 'LEFT'
            else:
                self.alignment = 'RIGHT'

    def tweak_indent(self):

        # Make sure the image can fit in the first place
        if self.width > config.DocWorkingWidth:
            print("WARNING: image larger than working space being passed to doc, weird formatting inbound...")
            # Try to fit the image as best as possible
            self.left_indent = 0
            self.right_indent = 0
            self.alignment = 'LEFT'
            return False
        if self.alignment == 'RIGHT':
            self.left_indent = 0
        if self.alignment == 'LEFT':
            self.right_indent = 0
        if self.left_indent > config.DocWorkingWidth - self.width - 20:
            self.left_indent = (config.DocWorkingWidth - self.width - 20)
        if self.right_indent > config.DocWorkingWidth - self.width + self.left_indent:
            self.right_indent = config.DocWorkingWidth - self.width + self.left_indent
        if self.left_indent < 0:
            self.left_indent = 0
        if self.right_indent < 0:
            self.right_indent = 0

    def add_to_doc(self, flowable_list):

        self.tweak_indent()
        alignment_code = self.alignment.upper()
        # Set x_offset so that it will work properly in conjunction with the indentation case
        if alignment_code == 'LEFT':
            x_offset = self.left_indent
        elif alignment_code == 'RIGHT':
            x_offset = -1 * self.right_indent
        else:
            print("Warning: unmatched alignment being passed to TextLine.add_to_doc(), defaulting to left alignment")
            alignment_code = 'LEFT'
            x_offset = self.left_indent

        # Add spacing above
        if self.y_padding:
            flowable_list.append(reportlab.platypus.Spacer(16, self.y_padding))
        # Create a OffsetImage and append it to the parent flowable_list
        flowable_list.append(OffsetImage(self.file_path, width=self.width, height=self.height,
                                         hAlign=alignment_code, x_offset=x_offset))
        # Add spacing above
        if self.y_padding:
            flowable_list.append(reportlab.platypus.Spacer(16, self.y_padding))


class DynamicScribe:
    def __init__(self, source, relationship_weights=None, instrument_name=None, allow_self_links=False,
                 draw_header=True, merge_same_words=False):
        self.source = source
        self.merge_same_words = merge_same_words
        if isinstance(source, network.Network):
            self.network = source
        else:
            self.network = network.word_mine(source, relationship_weights, allow_self_links=allow_self_links,
                                             merge_same_words=self.merge_same_words)

        self.instrument_name = instrument_name
        self.instrument = None
        self.instrument_is_initialized = False
        self.initialize_instrument()
        self.allow_self_links = allow_self_links

        self.file_cleanup_list = []
        self.item_list = []
        self.flowable_list = []

        # Initialize font from global FontName
        document_tools.register_font(config.FontName)
        # Set up base_paragraph_style, passing in globals
        self.base_paragraph_style = reportlab.lib.styles.ParagraphStyle('Default Style',
                                                                        fontSize=config.FontSize,
                                                                        fontName=config.FontName)

        self.indenter_network_left = prebuilt_networks.indenter()
        self.indenter_network_right = prebuilt_networks.indenter()
        self.pause_or_write_network = prebuilt_networks.text_pause_or_write()
        # Set up relationship weights for dynamic weights
        if relationship_weights is not None:
            self.relationship_weights = relationship_weights
        else:
            self.relationship_weights = {1: 1200, 2: 400, 3: 100, 4: 60, 5: 50,
                                         6: 40, 7: 30, 8: 17, 9: 14, 10: 10,
                                         11: 10, 12: 10, 13: 5, 14: 5, 15: 75}
        self.punctuation_list = [',', '.', ';', '!', '?', ':', '-']

        self.allow_self_links = allow_self_links
        self.draw_header = draw_header
        self._extra_image_padding = 0  # For special cases only, maybe remove delete?

    def initialize_instrument(self, instrument_name=None):
        if instrument_name is not None:
            self.instrument_name = instrument_name
        if self.instrument_name == "Flute":
            self.instrument = flute.Flute()
        elif self.instrument_name == "Alto Flute":
            self.instrument = flute.Flute(self.instrument_name)
        elif self.instrument_name == 'Oboe':
            self.instrument = oboe.Oboe()
        elif self.instrument_name == 'Clarinet':
            self.instrument = clarinet.Clarinet(self.instrument_name)
        elif self.instrument_name == 'Bass Clarinet':
            self.instrument = clarinet.Clarinet(self.instrument_name)
        elif self.instrument_name == 'Bassoon':
            self.instrument = bassoon.Bassoon()
        elif self.instrument_name == 'Low Horn':
            self.instrument = horn.Horn(self.instrument_name)
        elif self.instrument_name == 'High Horn':
            self.instrument = horn.Horn(self.instrument_name)
        elif self.instrument_name == 'Trumpet':
            self.instrument = trumpet.Trumpet()
        elif self.instrument_name == 'Tenor Trombone':
            self.instrument = trombone.Trombone()
        elif self.instrument_name == "Bass":
            self.instrument = bass.Bass()
        elif self.instrument_name == 'Viola':
            self.instrument = viola.Viola()
        elif self.instrument_name == 'Cello':
            self.instrument = cello.Cello()
        elif self.instrument_name == 'Violin':
            self.instrument = violin.Violin()
        elif self.instrument_name == 'Percussion':
            self.instrument = percussion.Percussion()
        elif self.instrument_name == 'Guitar':
            self.instrument = guitar.Guitar()
        elif self.instrument_name == 'Audience':
            self.instrument = audience.Audience()
        elif self.instrument_name == 'Speaker':
            self.instrument = speaker.Speaker()
        elif self.instrument_name == 'Toy Piano':
            self.instrument = toy_piano.ToyPiano()
        self.instrument_is_initialized = True

    def refresh_network(self):
        r_network = network.word_mine(self.source, self.relationship_weights,
                                      merge_same_words=self.merge_same_words)
        self.network.refresh_links(r_network)

    def populate_item_list(self, steps, dynamic_weights=False, update_frequency=500):
        """
        Fills self.item_list with Node instances
        :param steps: int for how many items to populate
        :param dynamic_weights: Bool
        :param update_frequency: int for how often to print a status update
        """
        if self.network is None:
            self.network = network.word_mine(self.source,
                                             self.relationship_weights,
                                             allow_self_links=self.allow_self_links,
                                             merge_same_words=self.merge_same_words)
        if not self.network.node_list:
            print("ERROR: trying to walk an empty network, ignoring...")
            return False

        # Main item population loop
        for i in range(0, steps):
            if i % update_frequency == 0:
                print(('Populating items step:  ' + str(i) +
                       '  -  ' + str(round((i / (steps * 1.0)*100))) + '%'))
            if dynamic_weights:  # Modify dynamic weights every time if called for
                # ---change self.relationship_weights somehow
                # So iteration isn't done every time (to save render time, can be reverted later)
                if random.randint(0, 1000) == 999:
                    self.relationship_weights[1] -= random.randint(0, 1000)
                    self.relationship_weights[2] -= random.randint(0, 100)
                    self.relationship_weights[12] += random.randint(-10, 100)
                    self.relationship_weights[8] += random.randint(-10, 50)
                    self.relationship_weights[15] += random.randint(-10, 90)
                    self.refresh_network()

            # Determine with self.pause_or_write_network whether to append a blank line or a word to self.item_list
            if self.pause_or_write_network.pick().get_value() == 0:
                self.item_list.append(nodes.BlankLine('BLANK LINE'))
            else:
                new_node = self.network.pick()
                self.item_list.append(new_node)
                if new_node.self_destruct:
                    self.network.remove_node_by_name(new_node.name)

    def clean_up_files(self, ly=True, png=False):
        """
        deletes temporary files (lilypond and image files) contained in self.file_cleanup_list. Should only be used
        once the final output PDF has been built & saved. Takes two bool's to decide if lilypond files, image files,
        or both should be deleted
        :param ly: Bool
        :param png: Bool
        """
        import subprocess
        if not self.file_cleanup_list:
            print("DynamicScribe.clean_up_files() was called, but no files to clean up!")
            return False

        for file_string in self.file_cleanup_list:
            if (file_string[-4:] == '.png' and png) or (file_string[-3:] == '.ly' and ly):
                subprocess.call(['del', file_string], shell=True)

    def render(self, output_file, open_when_finished=False, update_frequency=25):
        """
        Cycles through every Node in self.item_list[] and creates a word doc accordingly
        :param output_file: path to output to
        :param open_when_finished: Bool
        :param update_frequency: int - give an update via print function every update_frequency steps in the render
        :return: str - path to newly built PDF file
        """

        output_file_path = output_file
        if not os.path.isabs(output_file_path):
            output_file_path = os.path.realpath(output_file_path)

        if not self.network.node_list:
            print("ERROR: trying to walk an empty network, ignoring...")
            return False

        left_indent = rand.weighted_rand(
            [rand.Weight(0, 95),
             rand.Weight(10, 125),
             rand.Weight(60, 55),
             rand.Weight(135, 0)])
        right_indent = rand.weighted_rand(
            [rand.Weight(0, 40),
             rand.Weight(10, 80),
             rand.Weight(60, 60),
             rand.Weight(130, 40)])

        # Cycle through all nodes stored in self.item_list, use them to fill the contents of self.flowable_list
        current_line = Paragraph()
        for i in range(len(self.item_list)):

            if i % update_frequency == 0:
                print(('Rendering step:  ' + str(i) +
                       '  -  ' + str(round((i / (len(self.item_list) - 1.0))*100)) + '%'))
            # Find indentation and alignment
            left_indent += self.indenter_network_left.pick().get_value()
            right_indent += self.indenter_network_right.pick().get_value()
            if left_indent > config.DocWorkingWidth - config.MinColumnWidth:
                left_indent = config.DocWorkingWidth - config.MinColumnWidth - 30
            if left_indent < 0:
                left_indent = random.randint(0, 30)
                right_indent -= left_indent
            if config.DocWorkingWidth - right_indent < left_indent + config.MinColumnWidth:
                right_indent = config.DocWorkingWidth - left_indent - config.MinColumnWidth - 1
            if right_indent < 0:
                right_indent = random.randint(0, 30)
                left_indent -= right_indent

            dummy_align = rand.weighted_rand(
                [rand.Weight('LEFT', 70),
                 rand.Weight('RIGHT', 5),
                 rand.Weight('JUSTIFY', 15)],
                run_type='discreet')

            if isinstance(self.item_list[i], nodes.Word):
                temp_text_unit = TextUnit('')
                temp_string = self.item_list[i].name
                if temp_string[0] == '^':
                    temp_text_unit.italic = True
                    temp_string = temp_string[1:]
                if temp_string[0] == '%':
                    temp_text_unit.bold = True
                    temp_string = temp_string[1:]
                if len(current_line.contents) != 0:
                    temp_string = " " + temp_string
                temp_text_unit.text = temp_string

                current_line.add_text_unit(temp_text_unit)

            elif isinstance(self.item_list[i], nodes.Punctuation):
                temp_string = self.item_list[i].name
                if temp_string == '-':
                    temp_string = ' -'
                current_line.add_text_unit(TextUnit(temp_string))

            elif isinstance(self.item_list[i], nodes.Image):
                if current_line.contents is not None:
                    # Send current_line contents to a new line
                    # current_line.add_to_doc(self.doc, self.base_style)
                    current_line.add_to_doc(self.flowable_list, self.base_paragraph_style)
                    current_line = Paragraph()
                if self.item_list[i].left_indent is not None:
                    left_indent = self.item_list[i].left_indent
                if self.item_list[i].right_indent is not None:
                    right_indent = self.item_list[i].right_indent
                if self.item_list[i].alignment is not None:
                    dummy_align = self.item_list[i].alignment
                image_line = InlineImage(self.item_list[i].get_value(),
                                         left_indent=left_indent,
                                         right_indent=right_indent,
                                         alignment=dummy_align)
                image_line.add_to_doc(self.flowable_list)

            elif isinstance(self.item_list[i], nodes.Action):
                if self.item_list[i].name == '+':
                    if current_line.contents is not None:
                        # Send current_line contents to a new line
                        current_line.add_to_doc(self.flowable_list, self.base_paragraph_style)
                        current_line = Paragraph()
                    # Add image with self.instrument
                    if self.instrument is not None:

                        if not self.instrument_is_initialized:
                            self.initialize_instrument()
                        image_path = self.instrument.play()
                        ly_path = image_path[:-4] + ".ly"
                        # Add image_path and ly_path to self.file_cleanup_list for optional cleanup later on
                        self.file_cleanup_list.append(image_path)
                        self.file_cleanup_list.append(ly_path)

                        image_line = InlineImage(image_path,
                                                 left_indent=left_indent,
                                                 right_indent=right_indent,
                                                 alignment=dummy_align)
                        image_line.add_to_doc(self.flowable_list)

            elif isinstance(self.item_list[i], nodes.BlankLine):
                if current_line.contents is not None:
                        # Send current_line contents to a new line
                        current_line.left_indent = left_indent
                        current_line.right_indent = right_indent
                        current_line.alignment = dummy_align
                        current_line.add_to_doc(self.flowable_list, self.base_paragraph_style)
                        current_line = Paragraph()
                self.flowable_list.append(reportlab.platypus.Spacer(16, config.FontSize))

            elif (i == len(self.item_list) - 1) and (current_line.contents is not None):
                current_line.left_indent = left_indent
                current_line.right_indent = right_indent
                current_line.alignment = dummy_align
                current_line.add_to_doc(self.flowable_list, self.base_paragraph_style)
                current_line = Paragraph()

        # Build page header function to be passed later to output_doc.build()
        def build_header_canvas(canvas, doc):
            # Set up positions
            header_y_position = (11 * rl_inch) - 45
            page_number = doc.page
            if page_number % 2 == 0:
                # Left-hand page
                page_number_x_position = 60
            else:
                # Right-hand page
                page_number_x_position = (8.5 * rl_inch) - 60

            canvas.saveState()
            canvas.setFont(config.FontName, 11)
            canvas.drawCentredString((8.5 * rl_inch) / 2, header_y_position, self.instrument_name)

            canvas.drawString(page_number_x_position, header_y_position, str(page_number))
            canvas.restoreState()

        # Save the doc to an output pdf file
        output_doc = reportlab.platypus.SimpleDocTemplate(output_file_path)
        output_doc.pagesize = (8.5 * rl_inch, 11 * rl_inch)
        if self.draw_header:
            output_doc.build(self.flowable_list, onFirstPage=build_header_canvas, onLaterPages=build_header_canvas)
        else:
            output_doc.build(self.flowable_list)

        # Open the finished pdf file if requested in render() call
        if open_when_finished:
            import subprocess
            subprocess.call(['start', '', output_file_path], shell=True)

        # Return path to the final built pdf
        return output_file


class InstrumentScribe:
    """
    Based on DynamicScribe with some specializations. Uses only render(), no need to populate_item_list()
    Does not reference a source text for word_mine-ing, instead uses a predefined network
    (chance.prebuilt_networks.instrument_pause_or_play()) to decide if a blank line should be written or if
    the instrument should play
    """
    def __init__(self, instrument_name='Violin', draw_header=True):

        self.instrument_name = instrument_name
        self.instrument = None
        self.instrument_is_initialized = False
        self.initialize_instrument()

        self.file_cleanup_list = []
        self.item_list = []
        self.flowable_list = []

        # Initialize font from global FontName
        document_tools.register_font(config.FontName)
        # Set up base_paragraph_style, passing in globals
        self.base_paragraph_style = reportlab.lib.styles.ParagraphStyle('Default Style',
                                                                        fontSize=config.FontSize,
                                                                        fontName=config.FontName)

        self.action_network = prebuilt_networks.instrument_pause_or_play()
        self.indenter_network_left = prebuilt_networks.instrument_indenter()
        self.indenter_network_right = prebuilt_networks.instrument_indenter()

        self.draw_header = draw_header

    def initialize_instrument(self, instrument_name=None):
        if instrument_name is not None:
            self.instrument_name = instrument_name
        if self.instrument_name == "Flute":
            self.instrument = flute.Flute()
        elif self.instrument_name == "Alto Flute":
            self.instrument = flute.Flute(self.instrument_name)
        elif self.instrument_name == 'Oboe':
            self.instrument = oboe.Oboe()
        elif self.instrument_name == 'Clarinet':
            self.instrument = clarinet.Clarinet(self.instrument_name)
        elif self.instrument_name == 'Bass Clarinet':
            self.instrument = clarinet.Clarinet(self.instrument_name)
        elif self.instrument_name == 'Bassoon':
            self.instrument = bassoon.Bassoon()
        elif self.instrument_name == 'Low Horn':
            self.instrument = horn.Horn(self.instrument_name)
        elif self.instrument_name == 'High Horn':
            self.instrument = horn.Horn(self.instrument_name)
        elif self.instrument_name == 'Trumpet':
            self.instrument = trumpet.Trumpet()
        elif self.instrument_name == 'Tenor Trombone':
            self.instrument = trombone.Trombone()
        elif self.instrument_name == "Bass":
            self.instrument = bass.Bass()
        elif self.instrument_name == 'Viola':
            self.instrument = viola.Viola()
        elif self.instrument_name == 'Cello':
            self.instrument = cello.Cello()
        elif self.instrument_name == 'Violin':
            self.instrument = violin.Violin()
        elif self.instrument_name == 'Percussion':
            self.instrument = percussion.Percussion()
        elif self.instrument_name == 'Guitar':
            self.instrument = guitar.Guitar()
        elif self.instrument_name == 'Audience':
            self.instrument = audience.Audience()
        elif self.instrument_name == 'Speaker':
            self.instrument = speaker.Speaker()
        elif self.instrument_name == 'Toy Piano':
            self.instrument = toy_piano.ToyPiano()

    def clean_up_files(self, ly=True, png=False):
        """
        deletes temporary files (lilypond and image files) contained in self.file_cleanup_list. Should only be used
        once the final output PDF has been built & saved. Takes two bool's to decide if lilypond files, image files,
        or both should be deleted
        :param ly: Bool
        :param png: Bool
        """
        import subprocess
        if not self.file_cleanup_list:
            print("InstrumentScribe.clean_up_files() was called, but no files to clean up!")
            return False

        for file_string in self.file_cleanup_list:
            if (file_string[-4:] == '.png' and png) or (file_string[-3:] == '.ly' and ly):
                subprocess.call(['del', file_string], shell=True)

    def render(self, steps, output_file, open_when_finished=False, update_frequency=25):

        output_file_path = output_file
        if not os.path.isabs(output_file_path):
            output_file_path = os.path.realpath(output_file_path)

        left_indent = rand.weighted_rand(
                [rand.Weight(0, 95),
                 rand.Weight(10, 125),
                 rand.Weight(60, 55),
                 rand.Weight(135, 0)])
        right_indent = rand.weighted_rand(
                [rand.Weight(0, 40),
                 rand.Weight(10, 80),
                 rand.Weight(60, 60),
                 rand.Weight(130, 40)])
        # Cycle through all nodes stored in self.item_list, use them to fill the contents of self.flowable_list
        for i in range(steps):
            if i % update_frequency == 0:
                print(('Rendering step:  ' + str(i) +
                       '  -  ' + str(round((i/(steps * 1.0))*100, 0)) + '%'))

            left_indent += self.indenter_network_left.pick().get_value()
            right_indent += self.indenter_network_right.pick().get_value()
            if left_indent > config.DocWorkingWidth - config.MinColumnWidth:
                left_indent = config.DocWorkingWidth - config.MinColumnWidth - 30
            if left_indent < 0:
                left_indent = random.randint(0, 15)
            if config.DocWorkingWidth - right_indent < left_indent:
                right_indent = config.DocWorkingWidth - left_indent - 30
            if right_indent < 0:
                right_indent = 0
            dummy_align = rand.weighted_rand(
                [rand.Weight('LEFT', 70),
                 rand.Weight('RIGHT', 8)],
                run_type='discreet')

            if self.instrument.previous_action == 'Special Action 3':
                self.action_network.current_node = self.action_network.node_list[-1]
            play_or_blank = self.action_network.pick().get_value()

            if play_or_blank:
                image_path = self.instrument.play()
                ly_path = image_path[:-4] + ".ly"
                # Add image_path and ly_path to self.file_cleanup_list for optional cleanup later on
                self.file_cleanup_list.append(image_path)
                self.file_cleanup_list.append(ly_path)

                image_line = InlineImage(image_path,
                                         left_indent=left_indent,
                                         right_indent=right_indent,
                                         alignment=dummy_align)
                image_line.add_to_doc(self.flowable_list)
            else:
                self.flowable_list.append(reportlab.platypus.Spacer(16, config.FontSize))

        # Build page header function to be passed later to output_doc.build()
        def build_header_canvas(canvas, doc):
            # Set up positions
            header_y_position = (11 * rl_inch) - 45
            page_number = doc.page
            if page_number % 2 == 0:
                # Left-hand page
                page_number_x_position = 60
            else:
                # Right-hand page
                page_number_x_position = (8.5 * rl_inch) - 60

            canvas.saveState()
            canvas.setFont(config.FontName, 11)
            canvas.drawCentredString((8.5 * rl_inch) / 2, header_y_position, self.instrument_name)

            canvas.drawString(page_number_x_position, header_y_position, str(page_number))
            canvas.restoreState()

        # Save the doc to an output pdf file
        output_doc = reportlab.platypus.SimpleDocTemplate(output_file_path)
        output_doc.pagesize = (8.5 * rl_inch, 11 * rl_inch)
        if self.draw_header:
            output_doc.build(self.flowable_list, onFirstPage=build_header_canvas, onLaterPages=build_header_canvas)
        else:
            output_doc.build(self.flowable_list)

        # Open the finished pdf file if requested in render() call
        if open_when_finished:
            import subprocess
            subprocess.call(['start', '', output_file_path], shell=True)

        # Return path to the final built pdf
        return output_file
