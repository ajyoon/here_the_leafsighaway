from here_the_leafsighaway.instruments import wind


class Clarinet(wind.Wind):
    def __init__(self, clarinet_type='Clarinet'):
        if clarinet_type == 'Bass Clarinet':
            wind.Wind.__init__(self, 'Bass Clarinet')
        # Otherwise assume Bb
        else:
            wind.Wind.__init__(self, 'Clarinet')
