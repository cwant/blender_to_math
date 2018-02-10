from math import floor, sin, cos, pi

class Spline:
  def __init__(self, line, **kwargs):
    self.t1 = kwargs.get('t1')
    if self.t1 == None: raise ValueError('Need t1')
    self.t2 = kwargs.get('t2')
    if self.t2 == None: raise ValueError('Need t2')
    # Line is a piecewise linear
    self.line = line
    self.width = self.t2 - self.t1
    self.cyclic = line.cyclic
    self.num = line.num

  def evaluate(self, t):
    t = self.line.sanitize_t(t)
    t_prev = t
    t_next = t
    index = self.line.get_index(t)
    t2 = self.line.partition[index]

    val_this = self.line.pieces[index].evaluate(t)
    index_prev = index - 1
    if index_prev < 0:
      t1 = self.t1
      if self.cyclic:
        index_prev = self.line.num - 1
        t_prev = t + self.width
    else:
      t1 = self.line.partition[index_prev]

    if abs(t2 - t1) < 0.0001: return val_this
 
    scale = 1.0 / (t2 - t1)
 
    if index_prev < 0:
      val_prev = val_this
    else:
      val_prev = (val_this +
                  self.line.pieces[index_prev].evaluate(t_prev)) / 2.0
 
    index_next = index + 1
    if index_next > self.num - 1 and self.cyclic:
      index_next = 0
      t_next = t - self.width
    if index_next > self.num - 1:
      val_next = val_this
    else:
      val_next = (val_this +
                  self.line.pieces[index_next].evaluate(t_next)) / 2.0

    return (val_this + (val_prev*(t2 - t) + val_next*(t - t1)) * scale) / 2.0

class SplineRevolution:
  def __init__(self, spline, **kwargs):
    self.spline = spline
    self.radius = kwargs.get('radius')
    if self.radius == None: raise ValueError('Need radius')

  def evaluate(self, u, v):
    xyz = self.spline.evaluate(u)
    sinv = sin(2*pi*v)
    cosv = cos(2*pi*v)
    x = ((self.radius + xyz[0])*cosv + xyz[1]*sinv)
    y = ((self.radius + xyz[0])*sinv + xyz[1]*cosv)
    return [x, y, xyz[2]]

class BezierInterpolator(CurveCommon):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)


  def cubic(self, t, p0, p0_right, p1_left, p1):
    # From https://blender.stackexchange.com/a/53989/45489
    r = 1-t
    return (r*r*r*p0 +
            3*r*r*t*p0_right +
            3*r*t*t*p1_left +
            t*t*t*p1)

class BezierToMathOld(BezierInterpolator):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self.spline = kwargs.get('spline')
    if not self.spline:
      curve = kwargs.get('curve')
      if not curve:
        raise ParameterError("'spline' or 'curve' not passed as parameter")
      self.spline = curve.splines[0]
    self.num_points = len(self.spline.bezier_points)
    self.cyclic = self.spline.use_cyclic_u
    if self.cyclic: self.num_points += 1

  def interpolate_bezier(self, t, bp1, bp2):
    return self.cubic(t, bp1.co, bp1.handle_right, bp2.handle_left, bp2.co)

  def evaluate(self, t):
    u = (t - self.t1) / (self.t2 - self.t1)
    u1 = u * (self.num_points - 1)
    i1 = floor(u1)
    if i1 < 0: i1 = 0
    if i1 > self.num_points - 2: i1 = self.num_points - 2
    if self.cyclic and i1 == self.num_points - 2:
      i2 = 0
    else:
      i2 = i1 + 1
    bp1 = self.spline.bezier_points[i1]
    bp2 = self.spline.bezier_points[i2]

    u2 = u1 - i1
    return self.interpolate_bezier(u2, bp1, bp2)

class MeshToMath(BezierInterpolator, PiecewiseCurve):
  def __init__(self, **kwargs):
    super(PiecewiseCurve).__init__(**kwargs)

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


