class LDTA(object):
    def __init__(self, unknown01, quality, unknown02, layer_attr_bits, source_id):
        self.unknown01 = unknown01              # Offset 0B
        self.quality = quality                  # Offset 4B
        self.unknown02 = unknown02              # Offset 6B
        self.layer_attr_bits = layer_attr_bits  # Offset 37B
        self.source_id = source_id              # Offset 40B

    def __repr__(self):
        return str(self.__dict__)
