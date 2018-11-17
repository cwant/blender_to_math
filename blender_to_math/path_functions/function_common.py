from blender_to_math.path_functions.adaptors.mesh_adaptor import MeshAdaptor
from blender_to_math.path_functions.adaptors.curve_adaptor import CurveAdaptor
from math import floor


class FunctionCommon:
    def __init__(self, **kwargs):
        self.t1 = kwargs.get('t1')
        if self.t1 is None:
            raise ValueError('Need t1' + str(self.t1))
        self.t2 = kwargs.get('t2')
        if self.t2 is None:
            raise ValueError('Need t2')
        self.width = self.t2 - self.t1

        if kwargs.get('bmesh') or kwargs.get('mesh'):
            self.adaptor = MeshAdaptor(**kwargs)
        elif kwargs.get('curve') or kwargs.get('spline'):
            self.adaptor = CurveAdaptor(**kwargs)
        else:
            ValueError("Can't determine input type!")

        self.cyclic = self.adaptor.cyclic
        if kwargs.get('cyclic') is not None:
            self.cyclic = kwargs.get('cyclic')


class PiecewiseFunction(FunctionCommon):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.point_list = self.adaptor.point_list(**kwargs)

        self.num_points = self.get_num_points()
        self.num_pieces = self.get_num_pieces()
        self.pieces = [None] * self.num_pieces
        # Partitioning the domain
        self.partition = [None] * self.num_pieces
        self.lengths = [None] * self.num_pieces
        self.total_length = None
        self.uniform_distribution = True

        self.generate_partition()
        # self.generate_pieces defined in subclass
        self.generate_pieces(**kwargs)

    def get_num_points(self):
        return len(self.point_list)

    def get_num_pieces(self):
        if self.cyclic:
            return self.num_points
        return self.num_points - 1

    def generate_partition(self):
        # Partition the domain [t1, t2] into subdomains for each piece
        start = self.t1
        if not self.uniform_distribution:
            width = (self.t2 - self.t1) / self.num_pieces
            for i in range(self.num_pieces):
                start += width
                self.partition[i] = start
            return

        self.total_length = 0
        for i in range(self.num_pieces):
            x1 = self.point_list[i]
            x2 = self.point_list[(i+1) % self.num_points]
            self.lengths[i] = (x2 - x1).length
            self.total_length += self.lengths[i]
        scale = self.width / self.total_length
        for i in range(self.num_pieces):
            start += self.lengths[i] * scale
            self.partition[i] = start

    def get_index(self, t):
        # Which partition does t fall in?
        for i in range(self.num_pieces):
            if self.partition[i] >= t:
                return i
        return self.num_pieces - 1

    def evaluate(self, t):
        t = self.sanitize_t(t)
        index = self.get_index(t)
        return self.pieces[index].evaluate(t)

    def sanitize_t(self, t):
        # For cyclic, ensure between t1 and t2
        if not self.cyclic:
            return t
        if t >= self.t1 and t <= self.t2:
            return t
        loop = floor((t - self.t1) / self.width)
        return t - loop*self.width
