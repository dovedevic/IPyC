class CommunicationHeader:
    def __init__(self, class_name, object_size):
        self.__name = class_name
        self.__size = object_size

    @property
    def class_name(self):
        return self.__name

    @property
    def class_size(self):
        return self.__size

    def construct(self):
        return "{}-|-{}".format(self.__name, self.__size)

    @staticmethod
    def extract(header):
        if '-|-' in str(header) and str(header).count('-|-') == 1 and str(header).split('-|-')[1].isnumeric():
            name, size = str(header).split('-|-')
            return CommunicationHeader(name, int(size))
        else:
            return None
