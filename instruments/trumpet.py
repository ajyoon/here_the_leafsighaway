from instruments import brass


class Trumpet(brass.Brass):
    def __init__(self):
        brass.Brass.__init__(self, 'Trumpet')
