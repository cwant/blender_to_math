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
