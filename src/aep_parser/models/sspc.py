class SSPC(object):
    def __init__(self, unknown01, width, height, seconds_dividend, seconds_divisor, unknown02, framerate, framerate_dividend):
        self.unknown01 = unknown01                    # Offset 0B
        self.width = width                            # Offset 30B
        self.height = height                          # Offset 34B
        self.seconds_dividend = seconds_dividend      # Offset 38B
        self.seconds_divisor = seconds_divisor        # Offset 42B
        self.unknown02 = unknown02                    # Offset 46B
        self.framerate = framerate                    # Offset 56B
        self.framerate_dividend = framerate_dividend  # Offset 60B
