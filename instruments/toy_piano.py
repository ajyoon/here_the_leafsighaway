from instruments import base_instrument


class ToyPiano(base_instrument.Instrument):

    def __init__(self):
        base_instrument.Instrument.__init__(self,
                                            'Toy Piano',
                                            0, 24, 28, 60,
                                            'treble',
                                            0,
                                            sustained_playing=False)
