class CurveAdaptor:
  def __init__(self, **kwargs):
    self.spline = kwargs.get('spline')
    if not self.spline:
      curve = kwargs.get('curve')
      if not curve:
        raise ParameterError("'spline' or 'curve' not passed as parameter")
      self.spline = curve.splines[0]
    self.cyclic = self.spline.use_cyclic_u

  def point_list(self, **kwargs):
    return [bp.co for bp in self.spline.bezier_points]

  def left_handles(self, **kwargs):
    return [bp.handle_left for bp in self.spline.bezier_points]

  def right_handles(self, **kwargs):
    return [bp.handle_right for bp in self.spline.bezier_points]
