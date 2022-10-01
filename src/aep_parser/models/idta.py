class IDTA(object):
    def __init__(self, type_, unknown01, id_):
        self.type_ = type_
        self.unknown01 = unknown01
        self.id_ = id_

    def __repr__(self):
        return str(self.__dict__)
