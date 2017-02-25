import os
import random
import time
import subprocess

from chance import rand, nodes
from document_tools import pdf_scribe, tools
from special_instructions import text_instructions
from shared import Globals


def make_parts(parts_list, target_page_count=20, clean_up_temps=True):

    # Start the clock
    clock_start_time = time.time()

    # Make sure input part_list is a list for proper processing
    if not isinstance(parts_list, list):
        parts_list = [parts_list]

    # Set up text material paths relative to shared.Globals.ResourcesFolder
    audience_text_material_path = os.path.join(Globals.ResourcesFolder, 'Text Material',
                                               'audience_main_text_material.txt')
    speaker_text_material_path = os.path.join(Globals.ResourcesFolder, 'Text Material',
                                              'speaker_main_text_material.txt')
    speaker_and_instrument_material_path = os.path.join(Globals.ResourcesFolder, 'Text Material',
                                                        'speaker_and_instrument_main_text_material.txt')
    long_magnet_string_path = os.path.join(Globals.ResourcesFolder, 'Text Material', 'shared_string.txt')

    # For use in text parts
    long_shared_text_string = open(long_magnet_string_path).read()
    # The constant bounds built into the unit count weights are designed to build 20-page long (ish) parts
    # This count_multiplier allows for the weights to be adjusted proportionally to get closer to the target_page_count
    count_multiplier = target_page_count / 20.0
    audience_unit_count_weights = rand.random_weight_list(1600 * count_multiplier, 1800 * count_multiplier,
                                                                 max_possible_weights=5)
    speaker_unit_count_weights = rand.random_weight_list(1600 * count_multiplier, 1800 * count_multiplier,
                                                                max_possible_weights=5)
    instrument_unit_count_weights = rand.random_weight_list(525 * count_multiplier, 650 * count_multiplier,
                                                                   max_possible_weights=5)
    combined_unit_count_weights = rand.random_weight_list(1100 * count_multiplier, 1175 * count_multiplier,
                                                                 max_possible_weights=5)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Main part-making loop - iterate through parts_to_make, building parts accordingly
    for part_name in parts_list:

        # TODO: these four cases of part_name have a LOT in common, might be possible to collapse in a more elegant way?
        if part_name == 'Audience':
            # Audience Parts
            unit_count = rand.weighted_rand(audience_unit_count_weights, do_round=True)
            part_scribe = pdf_scribe.DynamicScribe(audience_text_material_path, instrument_name=part_name)
            part_base_pdf_path = os.path.join(Globals.ResourcesFolder, 'temp',
                                              part_name + '_base' + str(random.randint(0, 10000000)) + '.pdf')

            # Main document population
            part_scribe.populate_item_list(unit_count, True)
            # Add non-network-driven events
            # Add big text magnet in bold at a random location
            part_scribe.item_list.insert(random.randint(0, len(part_scribe.item_list)-1),
                                         nodes.Word(long_shared_text_string))
            # Add opening few words in italics
            part_scribe.item_list.insert(0, nodes.Word('^here, the leafsighaway, '))
            # Add final fermata of variable size
            final_fermata = text_instructions.draw_big_fermata_without_timecode(random.randint(30, 60))
            part_scribe.item_list.append(nodes.Image(final_fermata, 'center', 0, 0))
            # Render the part
            base_part = part_scribe.render(part_base_pdf_path)

            print(tools.part_attach_notes(os.path.realpath(base_part), part_name))

        elif part_name == 'Speaker':
            # Speaker parts #
            unit_count = rand.weighted_rand(speaker_unit_count_weights, do_round=True)
            part_scribe = pdf_scribe.DynamicScribe(speaker_text_material_path, instrument_name=part_name, allow_self_links=True)
            part_base_pdf_path = os.path.join(Globals.ResourcesFolder, 'temp',
                                              part_name + '_base' + str(random.randint(0, 10000000)) + '.pdf')

            # Main document population
            part_scribe.populate_item_list(unit_count, True)
            # Add non-network-driven events
            # Add big text magnet in bold at a random location
            part_scribe.item_list.insert(random.randint(0, len(part_scribe.item_list)-1),
                                         nodes.Word(long_shared_text_string))
            # Add opening few words in italics
            part_scribe.item_list.insert(0, nodes.Word('^here, the leafsighaway, '))
            # Add a random amount of space from the top of the page
            part_scribe.item_list.insert(0, nodes.Word('\n' *
                                rand.weighted_rand([(0, 5), (12, 6), (40, 2), (90, 0)], do_round=True)))

            # Render the part
            base_part = part_scribe.render(part_base_pdf_path)

            print(tools.part_attach_notes(os.path.realpath(base_part), part_name))

        elif part_name.endswith('& Speaker'):
            part_instrument_name = part_name[:-10]
            unit_count = rand.weighted_rand(combined_unit_count_weights, do_round=True)
            part_scribe = pdf_scribe.DynamicScribe(speaker_and_instrument_material_path,
                                                                  instrument_name=part_instrument_name,
                                                                  allow_self_links=True, merge_same_words=True)
            part_scribe.instrument.special_action_weights = [(0, 45), (1, 7), (2, 4), (3, 1)]
            part_base_pdf_path = os.path.join(Globals.ResourcesFolder, 'temp',
                                              part_name + '_and_Speaker_base' +
                                              str(random.randint(0, 10000000)) + '.pdf')

            # Main document population
            part_scribe.populate_item_list(unit_count, True)
            # Add non-network-driven events
            # Add big text magnet in bold at a random location
            part_scribe.item_list.insert(random.randint(0, len(part_scribe.item_list)-1),
                                         nodes.Word(long_shared_text_string))
            # Add opening few words in italics
            part_scribe.item_list.insert(0, nodes.Word('^here, the leafsighaway, '))
            # Add a random amount of space from the top of the page
            part_scribe.item_list.insert(0, nodes.Word('\n' *
                                rand.weighted_rand([(0, 5), (12, 6), (40, 2), (90, 0)], do_round=True)))

            # Render the part
            base_part = part_scribe.render(part_base_pdf_path)
            print(tools.part_attach_notes(os.path.realpath(base_part), part_name))

        else:
            # Instrument-only parts
            unit_count = rand.weighted_rand(instrument_unit_count_weights, do_round=True)

            part_scribe = pdf_scribe.InstrumentScribe(part_name)
            part_base_pdf_path = os.path.join(Globals.ResourcesFolder, 'temp', part_name +
                                              '_base' + str(random.randint(0, 10000000)) + '.pdf')
            base_part = part_scribe.render(unit_count, part_base_pdf_path, update_frequency=1)

            # Merge with part notes and return
            print(tools.part_attach_notes(os.path.realpath(base_part), part_name))

        # Clean up part_scribe's temporary files (.ly and .png)
        if clean_up_temps:
            # Wait a little bit so that reportlab has a second to tidy up
            time.sleep(1)
            part_scribe.clean_up_files(True, True)
            subprocess.call(['del', base_part], shell=True)

        # Print time elapsed
        time_elapsed = divmod(time.time() - clock_start_time, 60)
        print("New part built in " + str(int(time_elapsed[0])) + \
              ' minutes and ' + str(int(time_elapsed[1])) + ' seconds')
