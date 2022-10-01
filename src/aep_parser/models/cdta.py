class CDTA(object):
    def __init__(self, unknown01, framerate_divisor, framerate_dividend, unknown02, seconds_dividend, seconds_divisor, background_color, unknown03, width, height, unknown04, framerate):
        self.unknown01 = unknown01                    # Offset 0B
        self.framerate_divisor = framerate_divisor    # Offset 4B
        self.framerate_dividend = framerate_dividend  # Offset 8B
        self.unknown02 = unknown02                    # Offset 12B
        self.seconds_dividend = seconds_dividend      # Offset 40B
        self.seconds_divisor = seconds_divisor        # Offset 44B
        self.background_color = background_color      # Offset 48B
        self.unknown03 = unknown03                    # Offset 51B
        self.width = width                            # Offset 136B
        self.height = height                          # Offset 138B
        self.unknown04 = unknown04                    # Offset 140B
        self.framerate = framerate                    # Offset 152B

    def __repr__(self):
        return str(self.__dict__)
