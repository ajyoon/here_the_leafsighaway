from instruments import wind


class Bassoon(wind.Wind):
    def __init__(self):
        wind.Wind.__init__(self, 'Bassoon')
