# from abc import abstractmethod


class HueWrapperBase:
    """
    An abstract baseclass providing the most important functions for interacting
    with th phillips hue smart lightbulbs

    Please do change this class. Extend it by deriving from it.
    """

    def __init__(self):
        """
        empty init
        """
        pass

    # @abstractmethod
    def set_mode(self, mode):
        """
        set lamp in a specific mode. available modes are
            0 - off
            1 - on
            2 - flash (stroboscope)
            3 - dance mode

        Arguments
        ---------
        mode (int): the mode, see modes above

        Returns
        -------
        void
        """
        pass

    # @abstractmethod
    def toggle_on_off(self):
        """
        switch the hue on if it is off and vice versa

        Arguments
        ---------
        void

        Returns
        -------
        bool: status of lamp, True=on, False=off
        """
        pass

    # @abstractmethod
    def set_color(self, r, g, b):
        """
        set the color to a rgb color

        Arguments
        ---------
        r (int): red value of color between 0 and 255
        g (int): green value of color between 0 and 255
        b (int): blue value of color between 0 and 255

        Returns
        -------
        void
        """
        pass
