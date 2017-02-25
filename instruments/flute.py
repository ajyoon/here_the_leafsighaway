from instruments import wind


class Flute(wind.Wind):

    def __init__(self, flute_type='Flute'):
        if flute_type == 'Alto Flute':
            wind.Wind.__init__(self, instrument_name='Alto Flute')
        else:
            wind.Wind.__init__(self, instrument_name='Flute')
