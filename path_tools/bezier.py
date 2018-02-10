from path_tools.curve_common import *

class BezierSegment:
  def __init__(self, x1, x1_right, x2_left, x2, t1, t2):
    self.x1 = x1
    self.x1_right = x1_right
    self.x2_left = x2_left
    self.x2 = x2
    self.t1 = t1
    self.t2 = t2

  def evaluate(self, t):
    # Adapted from https://blender.stackexchange.com/a/53989/45489
    u1 = (t - self.t1) / (self.t2 - self.t1)
    u2 = 1-u1
    return (u2*u2*u2*self.x1 +
            3*u2*u2*u1*self.x1_right +
            3*u2*u1*u1*self.x2_left +
            u1*u1*u1*self.x2)

class BezierFunction(PiecewiseCurve):

  def generate_pieces(self, **kwargs):
    self.left_handles = self.adaptor.left_handles(**kwargs)
    self.right_handles = self.adaptor.right_handles(**kwargs)
    start = self.t1
    for i in range(self.num_points):
      t1 = start
      t2 = self.partition[i]
      x1 = self.point_list[i]
      x1_right = self.right_handles[i]
      x2_left = self.left_handles[i+1]
      x2 = self.point_list[i+1]
      self.pieces[i] = BezierSegment(x1, x1_right, x2_left, x2, t1, t2)
      start = t2
