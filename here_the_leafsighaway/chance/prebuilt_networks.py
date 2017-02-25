from here_the_leafsighaway.chance.nodes import Scalar, Vector
from here_the_leafsighaway.chance.network import Network


def indenter():
    """
    Builds and returns a network which controls behavior for indentation values (either left- or right- indentation)
    :return: instance of chance.network.Network
    """

    network = Network()

    n1 = Scalar(0)
    n2 = Vector('Shift Right', [(3, 6), (11, 1)])
    n3 = Vector('Shift Left', [(-3, 6), (-11, 1)])
    n4 = Vector('Jump Right', [(14, 0), (85, 20), (110, 1), (170, 10)])
    n5 = Vector('Jump Left', [(-14, 0), (-85, 20), (-110, 1), (-170, 10)])

    n1.add_link(n1, 40)
    n1.add_link(n2, 3)
    n1.add_link(n3, 3)
    n1.add_link(n4, 20)
    n1.add_link(n5, 20)
    n2.add_link(n1, 60)
    n2.add_link(n2, 100)
    n2.add_link(n3, 50)
    n3.add_link(n1, 60)
    n3.add_link(n3, 100)
    n3.add_link(n2, 30)
    n3.add_link(n4, 20)
    n4.add_link(n1, 10)
    n5.add_link(n1, 30)
    network.add_node([n1, n2, n3, n4, n5])
    return network


def indenter_erratic():
    """
    Does the same thing as indenter() but with a stronger bias toward jumping left and right.
    Builds and returns a network which controls behavior for indentation values (either left- or right- indentation)
    :return: instance of chance.network.Network
    """

    network = Network()

    n1 = Scalar(0)
    n2 = Vector('Shift Right', [(3, 6), (11, 1)])
    n3 = Vector('Shift Left', [(-3, 6), (-11, 1)])
    n4 = Vector('Jump Right', [(14, 0), (85, 20), (110, 1), (170, 10)])
    n5 = Vector('Jump Left', [(-14, 0), (-85, 20), (-110, 1), (-170, 10)])

    n1.add_link(n1, 40)
    n1.add_link(n2, 3)
    n1.add_link(n3, 3)
    n1.add_link(n4, 30)
    n1.add_link(n5, 30)
    n2.add_link(n1, 60)
    n2.add_link(n2, 100)
    n2.add_link(n3, 50)
    n3.add_link(n1, 60)
    n3.add_link(n3, 100)
    n3.add_link(n2, 30)
    n3.add_link(n4, 20)
    n4.add_link(n1, 10)
    n5.add_link(n1, 30)
    network.add_node([n1, n2, n3, n4, n5])
    return network


def instrument_indenter():
    """
    Builds and returns a network which controls behavior for indentation values (either left- or right- indentation)
    Network values specialized for instrument indentation
    :return: instance of chance.network.Network
    """

    network = Network()
    n1 = Scalar(0)
    n2 = Vector('Shift Right', [(3, 6), (11, 1)])
    n3 = Vector('Shift Left', [(-3, 6), (-11, 1)])
    n4 = Vector('Jump Right', [(14, 0), (85, 20), (110, 1), (170, 10)])
    n5 = Vector('Jump Left', [(-14, 0), (-85, 20), (-110, 1), (-170, 10)])

    n1.add_link(n1, 70)
    n1.add_link(n2, 3)
    n1.add_link(n3, 3)
    n1.add_link(n4, 20)
    n1.add_link(n5, 20)

    n2.add_link(n1, 60)
    n2.add_link(n2, 100)
    n2.add_link(n3, 50)
    n2.add_link(n5, 60)

    n3.add_link(n1, 60)
    n3.add_link(n3, 100)
    n3.add_link(n2, 30)
    n3.add_link(n4, 20)

    n4.add_link(n1, 10)

    n5.add_link(n1, 30)

    network.add_node([n1, n2, n3, n4, n5])
    return network


def instrument_pause_or_play():
    """
    Constructs and returns a network with two states: 1 (play) and 0 (don't play)
    Designed so that, when passed to document_tools.pdf_scribe, 'don't play' results in a space equal to the
    global font size (config.FontSize)
    :return: instance of chance.network.Network
    """
    network = Network()
    dense_play = Scalar(1)
    play = Scalar(1)
    light_play = Scalar(1)
    light_rest = Scalar(0)
    rest = Scalar(0)
    dense_rest = Scalar(0)

    dense_play.add_link(dense_play, 14)
    dense_play.add_link(light_play, 3)
    dense_play.add_link(dense_rest, 1)

    play.add_link(dense_play, 1)
    play.add_link(play, 3)
    play.add_link(light_play, 4)
    play.add_link(light_rest, 12)
    play.add_link(rest, 4)

    light_play.add_link(play, 2)
    light_play.add_link(light_rest, 7)

    light_rest.add_link(rest, 3)
    light_rest.add_link(dense_rest, 1)
    light_rest.add_link(light_rest, 2)
    light_rest.add_link(light_play, 1)

    rest.add_link(rest, 4)
    rest.add_link(dense_rest, 3)
    rest.add_link(light_play, 1)

    dense_rest.add_link(dense_rest, 10)
    dense_rest.add_link(rest, 2)
    dense_rest.add_link(light_play, 1)

    network.add_node([dense_play, play, light_play, light_rest, rest, dense_rest])
    return network

def text_pause_or_write():
    """
    Constructs and returns a network with two states: 1 (write) and 0 (don't write)
    Designed so that, when passed to document_tools.pdf_scribe, 'don't write' results in a space equal to the
    global font size (config.FontSize)
    :return: instance of chance.network.Network
    """
    network = Network()
    dense_write = Scalar(1)
    write = Scalar(1)
    light_write = Scalar(1)
    light_rest = Scalar(0)
    rest = Scalar(0)
    dense_rest = Scalar(0)

    dense_write.add_link(dense_write, 600)
    dense_write.add_link(light_write, 30)
    dense_write.add_link(light_rest, 1)

    write.add_link(dense_write, 20)
    write.add_link(write, 110)
    write.add_link(light_write, 4)
    write.add_link(light_rest, 12)

    light_write.add_link(write, 5)
    light_write.add_link(light_write, 16)
    light_write.add_link(light_rest, 4)

    light_rest.add_link(dense_rest, 1)
    light_rest.add_link(light_rest, 5)
    light_rest.add_link(light_write, 14)

    rest.add_link(rest, 3)
    rest.add_link(dense_rest, 1)
    rest.add_link(light_write, 30)

    dense_rest.add_link(dense_rest, 10)
    dense_rest.add_link(rest, 2)
    dense_rest.add_link(light_write, 2)

    network.add_node([dense_write, write, light_write, light_rest, rest, dense_rest])
    return network
