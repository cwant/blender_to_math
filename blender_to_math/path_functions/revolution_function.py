from mathutils import Vector, Quaternion


class RevolutionFunction:
    def __init__(self, **kwargs):
        self.function = kwargs.get('function')
        if not self.function:
            raise ValueError('Need function')
        self.displace = kwargs.get('displace') or (0.0, 0.0, 0.0)
        self.displace = Vector(self.displace)
        self.axis = kwargs.get('axis') or (0.0, 0.0, 1.0)
        self.axis = Vector(self.axis)

    def evaluate(self, u, v):
        # u is function value
        # v is radians of rotation
        xyz = self.function.evaluate(u) + self.displace
        quat = Quaternion(self.axis, v)
        return quat * xyz
