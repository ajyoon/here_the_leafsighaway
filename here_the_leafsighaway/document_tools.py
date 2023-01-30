import os
import random

import PyPDF2

import here_the_leafsighaway.config


def merge_pdf_files(file_strings, output_path):
    """
    Takes a list of absolute file paths and converts them to an output file in output_path
    :param file_strings:
    :param output_path:
    :return:
    """
    assert isinstance(file_strings, list)
    for test_file in file_strings:
        assert isinstance(test_file, str)
        assert test_file.endswith('.pdf')

    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, file_strings[0].replace('.pdf', '_MERGED.pdf'))
    merger = PyPDF2.PdfMerger(strict=False)
    for merge_file in file_strings:
        in_file = merge_file
        merger.append(in_file)
    merger.write(output_path)
    merger.close()
    return output_path


def part_attach_notes(input_pdf, part_name, open_when_finished=False):
    """
    Takes an input PDF file and attaches the Shared Part Notes and the part_name specific part note to the front
    :param input_pdf: str corresponding to part note file
    :param part_name: str as in 'Viola' or 'Audience', etc...
    :param open_when_finished: bool
    :return: str
    """
    # Set up resource paths
    assert input_pdf.endswith('.pdf')
    part_notes_folder = os.path.join(here_the_leafsighaway.config.ResourcesFolder, 'Part Notes')
    output_path = here_the_leafsighaway.config.PartOutputFolder
    part_notes_file = os.path.join(part_notes_folder, part_name + ' Part Notes.pdf')
    general_part_notes_file = os.path.join(part_notes_folder, 'Shared Part Notes.pdf')

    # Set up the path for the final assembled file
    output_file_name = os.path.join(output_path, part_name + ' Part - Assembled.pdf')
    # If the target file path is already taken, toss on a random integer to the end to prevent file collision (messy)
    if os.path.exists(output_file_name):
        output_file_name = output_file_name.replace('.pdf', '_' + str(random.randint(0, 1000000)) + '.pdf')

    final_pdf = merge_pdf_files([general_part_notes_file, part_notes_file, input_pdf], output_file_name)

    if open_when_finished:
        import subprocess
        subprocess.call(['start', '', os.path.realpath(final_pdf)], shell=True)

    return final_pdf


def register_font(font_name='Crimson Text'):
    """
    Registers the Gentium TTF for embedding into documents
    (because I have become a snob and I think Times New Roman is for losers)
    """
    import reportlab.rl_config
    reportlab.rl_config.warnOnMissingFontGlyphs = 0
    import reportlab.pdfbase.pdfmetrics
    import reportlab.pdfbase.ttfonts
    font_folder = os.path.join(here_the_leafsighaway.config.ResourcesFolder, 'fonts')

    if font_name == 'Crimson Text':
        normal = os.path.join(font_folder, 'CrimsonText-Roman.ttf')
        bold = os.path.join(font_folder, 'CrimsonText-Bold.ttf')
        italic = os.path.join(font_folder, 'CrimsonText-Italic.ttf')
        bold_italic = os.path.join(font_folder, 'CrimsonText-BoldItalic.ttf')
        reportlab.pdfbase.pdfmetrics.registerFont(
            reportlab.pdfbase.ttfonts.TTFont('Crimson Text', normal))
        reportlab.pdfbase.pdfmetrics.registerFont(
            reportlab.pdfbase.ttfonts.TTFont('Crimson Text-Bold', bold))
        reportlab.pdfbase.pdfmetrics.registerFont(
            reportlab.pdfbase.ttfonts.TTFont('Crimson Text-Italic', italic))
        reportlab.pdfbase.pdfmetrics.registerFont(
            reportlab.pdfbase.ttfonts.TTFont('Crimson Text-BoldItalic', bold_italic))

        reportlab.pdfbase.pdfmetrics.registerFontFamily('Crimson Text',
                                                        'Crimson Text',
                                                        'Crimson Text-Bold',
                                                        'Crimson Text-Italic',
                                                        'Crimson Text-BoldItalic')
    else:
        print('Invalid font_name being passed to register_font, ignoring (major errors may be inbound...)')
        return False
