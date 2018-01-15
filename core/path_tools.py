from math import floor, sin, cos, pi

class OrderedVert:
  # This holds a Blender vertex, and has links to next/prev vertices
  def __init__(self, vert, **kwargs):
    self.vert = vert
    self.next = kwargs.get('next')
    self.prev = kwargs.get('prev')

  def add_next(self, vert):
    self.next = OrderedVert(vert, prev=self)
    return self.next

  def add_prev(self, vert):
    self.prev = OrderedVert(vert, next=self)
    return self.prev

class OrderedVertList:
  # A list (possibly cyclic) of ordered vertices
  def __init__(self, vert):
    self.num = 1
    self.first = OrderedVert(vert)
    self.last = None
    self.cyclic = False
    # If there are no edges at all, or any vertex has more than two edges
    self.degenerate = False

  def add_next(self):
    # Traverse linked edges looking for the next vertex to add
    ordered_vert = self.last or self.first
    vert = ordered_vert.vert
    edges = vert.link_edges
    if edges == None or len(edges) > 2:
      self.degenerate = True
      return None
    verts = [edge.other_vert(vert) for edge in edges]
    next_vert = None
    if ordered_vert.prev:
      if len(verts) == 1:
        self.last = ordered_vert
        return None
      if verts[0] == ordered_vert.prev.vert:
        next_vert = verts[1]
      else:
        next_vert = verts[0]
    else:
      next_vert = verts[0]
    if next_vert:
      # Next vert is cyclic
      if next_vert == self.first.vert:
        self.cyclic = True
        ordered_vert.next = self.first
        self.first.prev = ordered_vert
        self.last = ordered_vert
        return None
      # Next vert is not cyclic
      self.num += 1
      self.last = ordered_vert.add_next(next_vert)
      return next_vert
    # No next vert found
    self.last = ordered_vert
    return None

  def add_prev(self):
    # Traverse linked edges looking for the previous vertex to add
    ordered_vert = self.first
    vert = ordered_vert.vert
    edges = vert.link_edges
    if edges == None: raise "no linked edges"
    if len(edges) > 2: raise "too many linked edges"
    verts = [edge.other_vert(vert) for edge in edges]
    prev_vert = None
    if ordered_vert.next:
      if len(verts) == 1:
        return None
      if verts[0] == ordered_vert.next.vert:
        prev_vert = verts[1]
      else:
        prev_vert = verts[0]
    else:
      prev_vert = verts[0]
    if prev_vert:
      # Prev vert is cyclic
      if prev_vert == self.last.vert:
        self.cyclic = True
        return None
      # Prev vert is not cyclic
      self.num += 1
      self.first = ordered_vert.add_prev(prev_vert)
      return prev_vert
    # No prev vert found
    return None

  def to_list(self):
    out = []
    ordered_vert = self.first
    for i in range(self.num):
      out.append(ordered_vert.vert.co)
      ordered_vert = ordered_vert.next
    return out

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

class Mubic:
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
    self.t_diff_2 = self.t_diff**2
    self.x_diff = x2 - x1
    self.x1_prime2 = (x2 - x_prev) / self.t_diff_2
    self.x2_prime2 = (x_next - x1) / self.t_diff_2

  def evaluate(self, t):
    if not self.t_diff: return self.x1
    a = (self.t2 - t) / self.t_diff
    b = 1 - a
    c = self.t_diff_2 * (a**3 - a) / 6.0
    d = self.t_diff_2 * (b**3 - b) / 6.0
    return (self.x1 * a + self.x2 * b -
            self.x1_prime2 * c + self.x2_prime2 * d)

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
    if not self.t_diff: return self.x1
    t_diff1 = t - self.t1
    t_diff2 = self.t2 - t
    
    return ((self.x2 * t_diff1 + self.x1 * t_diff2) / self.t_diff +
            self.a1 * t_diff1**2 * t_diff2 + self.a2 * t_diff1 * t_diff2**2)

class CurveCommon:
  def __init__(self, **kwargs):
    self.t1 = kwargs.get('t1')
    if self.t1 == None: raise ValueError('Need t1' + str(self.t1))
    self.t2 = kwargs.get('t2')
    if self.t2 == None: raise ValueError('Need t2')
    self.width = self.t2 - self.t1
    self.cyclic = kwargs.get('cyclic') or False

class PiecewiseCurve(CurveCommon):
  def __init__(self, **kwargs):
    super().__init(**kwargs)

    # self.get_point_list() is defined in subclass
    self.point_list = self.get_point_list(**kwargs)

    self.num_points = len(self.point_list) 
    if not self.cyclic self.nup_points -= 1
    self.pieces = [None] * self.num_points
    # Partitioning the domain
    self.partition = [None] * self.num_points
    self.lengths = [None] * self.num_points
    self.total_length = None
    self.uniform_distribution = True

    self.generate_partition()
    # self.generate_pieces defined in subclass
    self.generate_pieces()

  def generate_partition(self):
    # Partition the domain [t1, t2] into subdomains for each piece
    start = self.t1
    if not self.uniform_distribution:
      width = (self.t2 - self.t1) / self.num_points
      for i in range(self.num_points):
        start += width
        self.partition[i] = start
      return

    self.total_length = 0
    ordered_vert = vert_list.first
    for i in range(self.num_points):
      x1 = self.point_list[i]
      x2 = self.point_list[i+1]
      self.lengths[i] = (x2 - x1).length
      self.total_length += self.lengths[i]
    scale = self.width / self.total_length
    for i in range(self.num):
      start += self.lengths[i] * scale
      self.partition[i] = start

  def get_index(self, t):
    # Which partition does t fall in?
    for i in range(self.num):
      if self.partition[i] >= t: return i
    return self.num - 1

  def evaluate(self, t):
    t = self.sanitize_t(t)    
    index = self.get_index(t)
    return self.pieces[index].evaluate(t)

  def sanitize_t(self, t):
    # For cyclic, ensure between t1 and t2
    if not self.cyclic: return t
    if t >= self.t1 and t <= self.t2: return t
    loop = floor((t - self.t1) / self.width)
    return t - loop*self.width

class PiecewiseLinear(PiecewiseCurve):
  def __init__():
    super().__init(**kwargs)

  def get_point_list(self, **kwargs):
    vert_list = kwargs.get('vert_list')
    return vert_list.to_list()

  def generate_pieces(self, vert_list):
    # Generate the individual linear parts
    start = self.t1
    ordered_vert = vert_list.first
    for i in range(self.num):
      t1 = start
      t2 = self.partition[i]
      x1 = ordered_vert.vert.co
      x2 = ordered_vert.next.vert.co
      self.pieces[i] = Linear(x1, x2, t1, t2)
      start = t2
      ordered_vert = ordered_vert.next

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

  def cubic(self, t, p0, p1, p2, p3):
    # From https://blender.stackexchange.com/a/53989/45489
    r = 1-t
    return (r*r*r*p0 +
            3*r*r*t*p1 +
            3*r*t*t*p2 +
            t*t*t*p3)

class BezierToMath(BezierInterpolator):
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


class BezierToMath2(PiecewiseCurve):
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

