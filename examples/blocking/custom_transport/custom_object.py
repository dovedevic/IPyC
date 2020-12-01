class CustomObject:
    def __init__(self, arg1: int, arg2: float, arg3: str, arg4: set):
        self.a1 = arg1
        self.a2 = arg2
        self.a3 = arg3
        self.a4 = arg4

    def __str__(self):
        return f"<CustomObject:a1={self.a1},a2={self.a2},a3={self.a3},a4={self.a4}>"

    # Define a serializer that returns a string/str representation of the object
    def serialize(self):
        return f"{self.a1}|{self.a2}|{self.a3}|{self.a4}"

    # Define a deserializer that undoes what the serializer did and returns the object
    @staticmethod
    def deserialize(serialization):
        a1, a2, a3, a4 = serialization.split('|')
        return CustomObject(int(a1), float(a2), str(a3), eval(a4))
