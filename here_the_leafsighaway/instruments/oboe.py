from here_the_leafsighaway.instruments import wind


class Oboe(wind.Wind):
    def __init__(self):
        wind.Wind.__init__(self, 'Oboe')
