from curve_common import PiecewiseCurve


class Cubic:
    def __init__(self, x1, x2, x_prev, x_next, t1, t2):
        if abs(t2 - t1) < 0.001:
            self.t_diff = None
            self.x1 = x1
            return

        self.t1 = t1
        self.t2 = t2
        self.x1 = x1
        self.x2 = x2
        self.t_diff = t2 - t1
        self.t_diff_3 = self.t_diff**3
        self.x_diff = x2 - x1
        self.x1_prime = None
        self.x2_prime = None
        if not x_prev and not x_next:
            x_prev = x1
            x_next = x2
        if x_prev:
            self.x1_prime = 0.5 * (x2 - x_prev) / self.t_diff
        if x_next:
            self.x2_prime = 0.5 * (x_next - x1) / self.t_diff

        if not self.x1_prime:
            self.x1_prime = self.reflect_across_x_diff(self.x2_prime)
        if not self.x2_prime:
            self.x2_prime = self.reflect_across_x_diff(self.x1_prime)

        self.a1 = (self.x_diff - self.x2_prime * self.t_diff) / self.t_diff_3
        self.a2 = (self.x1_prime * self.t_diff - self.x_diff) / self.t_diff_3

    def reflect_across_x_diff(self, v):
        n = self.x_diff.normalized()
        return (2 * (v * n) * n - v)

    def evaluate(self, t):
        if not self.t_diff:
            return self.x1
        t_diff1 = t - self.t1
        t_diff2 = self.t2 - t

        return ((self.x2 * t_diff1 + self.x1 * t_diff2) / self.t_diff +
                self.a1 * t_diff1**2 * t_diff2 +
                self.a2 * t_diff1 * t_diff2**2)


class PiecewiseCubic(PiecewiseCurve):
    def generate_pieces(self, vert_list):
        # Generate the individual linear parts
        self.generate_partition(vert_list)
        start = self.t1
        ordered_vert = vert_list.first
        for i in range(self.num):
            t1 = start
            t2 = self.partition[i]
            x1 = ordered_vert.vert.co
            if ordered_vert.prev:
                x_prev = ordered_vert.prev.vert.co
            else:
                x_prev = None
            x2 = ordered_vert.next.vert.co
            if ordered_vert.next.next:
                x_next = ordered_vert.next.next.vert.co
            else:
                x_next = None
            self.pieces[i] = Cubic(x1, x2, x_prev, x_next, t1, t2)
            start = t2
            ordered_vert = ordered_vert.next
