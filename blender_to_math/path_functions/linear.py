from blender_to_math.path_functions.function_common import *

class Linear:
  def __init__(self, x1, x2, t1, t2):
    if abs(t2 - t1) < 0.001:
      self.a = 0.0
      self.b = x1
    else:
      scale = 1.0 / (t2 - t1)
      # linear term
      self.a = (x2 - x1) * scale
      # affine term
      self.b = (x1*t2 - x2*t1) * scale

  def evaluate(self, t):
    return self.a * t + self.b

class PiecewiseLinearFunction(PiecewiseFunction):
  def generate_pieces(self, **kwargs):
    # Generate the individual linear parts
    start = self.t1
    for i in range(self.num_pieces):
      t1 = start
      t2 = self.partition[i]
      x1 = self.point_list[i]
      x2 = self.point_list[(i+1) % self.num_points]
      self.pieces[i] = Linear(x1, x2, t1, t2)
      start = t2

