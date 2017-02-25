from instruments import brass


class Horn(brass.Brass):
    def __init__(self, instrument_name='Low Horn'):
        if not ((instrument_name == 'Low Horn') or (instrument_name == 'High Horn')):
            if instrument_name == 'Horn':
                instrument_name = 'Low Horn'
            else:
                print(('Warning: Horn instance is being created with invalid instrument_name field of: ' + str(instrument_name) +
                       ", defaulting to Low Horn"))
                instrument_name = 'Low Horn'
        brass.Brass.__init__(self, instrument_name)
