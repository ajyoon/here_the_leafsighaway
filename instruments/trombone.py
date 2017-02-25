from instruments import brass


class Trombone(brass.Brass):
    def __init__(self):
        brass.Brass.__init__(self, 'Tenor Trombone')
