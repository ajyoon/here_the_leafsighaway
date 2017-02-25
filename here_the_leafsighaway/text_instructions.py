import random

from here_the_leafsighaway import config
from here_the_leafsighaway.chance import rand
from here_the_leafsighaway.lily import lilypond_file

shared_list = [("wait for the nearest instrumentalist to finish one phrase before continuing", 37),

               ("go back one page and repeat much more quietly before continuing", 33),

               ("listen to one of the closest instrumentalists and imitate their next phrase", 38),

               ("listen to the instrumentalist furthest away and imitate their next phrase", 35),

               ("listen to the nearest speaker and imitate the rhythm and contour of their next phrase", 42),

               ("listen to any instrumentalist far away and imitate their next phrase, but more loudly", 42),

               ("listen to the instrumentalist furthest away and imitate their next phrase, but more quietly", 45),

               ("listen to the nearest instrumentalist and imitate their next phrase, but almost inaudibly", 45),

               ("listen to the nearest instrumentalist and imitate their next phrase, but more quietly", 40),

               ("listen to the instrumentalist furthest away and imitate their next phrase as loudly as possible", 45)
               ]

speaker_list = [("listen to the nearest speaker and repeat their next phrase", 28),

                ("listen to any speaker far away and repeat their next phrase", 30),

                ("listen to the speaker furthest away and repeat their next phrase, changing a word or two", 42)
                ]


def visualize_a_color():
    """
    Randomly constructs a text string, sends it to draw_boxed_text, and returns newly built image path
    :return: str path
    """
    color_list = ['magenta', 'turquoise', 'teal', 'beige', 'murky grey', 'deep red',
                  'brown-orange', 'sky blue', 'navy blue', 'olive', 'maroon']
    use_color = color_list[random.randint(0, len(color_list) - 1)]
    out_string = 'visualize a shade of ' + use_color
    out_width = 26
    return draw_boxed_text(out_string, out_width)


def listen_until_you_hear():
    """
    Randomly constructs a text string, sends it to draw_boxed_text, and returns newly built image path
    :return: str path
    """
    word_list = ['the', 'a', 'here', 'to', 'away', 'toward', 'again']
    use_word = word_list[random.randint(0, len(word_list) - 1)]

    out_string = 'listen to the nearest speakers until you hear one of them say the word, \\"' + use_word + '\\"'
    out_width = 38
    return draw_boxed_text(out_string, out_width)


def notice_something():
    """
    Randomly selects an item from a list of texts to send to a boxed text, returns path to new image
    :return: str path
    """
    notice_list = [('notice that you are sitting in a chair', 24),
                   ('notice the air moving around you', 20),
                   ('notice that you are surrounded by people', 24)]
    index = random.randint(0, 2)
    return draw_boxed_text(notice_list[index][0], notice_list[index][1])


def speaker_boxed_text():
    """ Builds & returns a path to a boxed text containing an item from speaker_list"""
    out_text = speaker_list[random.randint(0, len(speaker_list) - 1)]
    return draw_boxed_text(out_text[0], out_text[1])


def call_if_needed(item):
    """
    Takes an item and calls it if possible, otherwise, returning just the item.
    Not in use right now, but could be useful in elegantly handling a list containing both variables and methods
    :param item: Any
    :return: Any
    """
    if hasattr(item, '__call__'):
        return item()
    else:
        return item


def draw_big_fermata(length_weights, size_factor=1):
    """
    Builds and renders a lilypond file of a large fermata with an approximate timecode.
    The fermata is scaled according to the timecode. Returns the image path.
    :param length_weights: list of tuples for how many seconds the fermata should last
    :param size_factor: int multiplier for the scale of the fermata
    :return: str of new image path
    """
    assert isinstance(length_weights, list)
    # Note that this file path only works if both the lilypond file and the eps file are located in the same
    #   directories relative to each other! This could cause a big confusion in refactoring, but as far as I can tell,
    #   lilypond doesn't accept absolute paths in epsfile syntax
    vector_file_path = '../../Graphics/big_fermata_vector.eps'

    # Convert an input seconds value into a string representation timecode for use in the fermata
    def seconds_to_timecode(seconds):
        minutes, out_seconds = divmod(seconds, 60)
        if minutes == 0:
            minute_string = ''
        else:
            minute_string = str(minutes) + "\"\\char ##x2019\" "
        second_string = str(out_seconds)
        if len(second_string) == 1:
            second_string = "0" + second_string
        second_string += '\"\\char ##x201D'
        return minute_string + second_string

    length = rand.weighted_rand(length_weights, do_round=True)
    fermata_size = length * 0.222 * size_factor
    # Round length to the nearest 10 seconds
    length = int(round(length, -1))
    length_string = seconds_to_timecode(length)
    score = lilypond_file.LilypondFile()
    score.master_string = ("""\\version "2.18.2"\n
                            \\header { tagline = #" " }
                            \\markup {\n
                            \\center-column {\n
                            \\line {\n
                            \\epsfile #X #""" + str(fermata_size) + ' #"' + vector_file_path + '"\n' +
                           "}\n\\line {\\abs-fontsize #11\n\\bold {\\italic{ \\concat {" +
                           "\n\\override #' (font-name . \"Book Antiqua Bold\")\n" +
                           "\\char ##x2248\n\\override #' (font-name . \"CrimsonText bold italic\")\n \"" +
                           length_string + ' }}}}}}')
    score._string_built = True

    output_file_name = "fermata_" + str(config.FileNameIndex)
    output_png = score.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
    config.FileNameIndex += 1
    return output_png


def draw_big_fermata_without_timecode(size):
    """
    Uses lilypond to draw a big fermata of input size, returns new image path
    :param size: number
    :return: str path to newly built png image
    """
    # Note that this file path only works if both the lilypond file and the eps file are located in the same
    #   directories relative to each other! This could cause a big confusion in refactoring, but as far as I can tell,
    #   lilypond doesn't accept absolute paths in epsfile syntax
    vector_file_path = '../../Graphics/big_fermata_vector.eps'
    fermata_size = size
    score = lilypond_file.LilypondFile()
    score.master_string = ("""\\version "2.18.2"\n
                            \\header { tagline = #" " }
                            \\markup {\n
                            \\center-column {\n
                            \\line {\n
                            \\epsfile #X #""" + str(fermata_size) + ' #"' + vector_file_path + '"\n' +
                           '}}}')
    score._string_built = True
    output_file_name = "fermata_" + str(config.FileNameIndex)
    output_png = score.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
    config.FileNameIndex += 1
    return output_png


def draw_boxed_text(text_string, line_width=45):
    """
    Creates and renders a lilypond file containing a boxed text markup with the text of text_string
    :param text_string: str
    :param line_width: int
    :return: str of png path
    """
    score = lilypond_file.LilypondFile()
    score.master_string = ("\\version \"2.18.2\"\n" +
                           "\\header { tagline = #\" \" }\n" +
                           "\\markup {\n\n" +
                           "\\override #' (font-name . \"CrimsonText bold italic\")\n" +
                           "\\abs-fontsize #11 \\box{ \\bold{ \\italic{ \\pad-around #1 {\n" +
                           "\\override #'(line-width . " + str(line_width) + ")\n" +
                           "\\wordwrap-string #\"" +
                           text_string + "\" }}}}}")
    score._string_built = True

    output_file_name = "text_string_" + str(config.FileNameIndex)
    output_png = score.save_and_render(output_file_name, view_image=False, autocrop=True, delete_ly=False)
    config.FileNameIndex += 1
    return output_png
