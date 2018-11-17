class ParameterMapper:
  def __init__(self, f, u_range, resolution, iterations):
    self.u_range = u_range
    self.width = (u_range[1] - u_range[0]) / (resolution - 1)
    self.resolution = resolution
    self.partition = self.make_partition(u_range, resolution)
    for i in range(iterations):
      self.warp(self.partition, f)
      
  def warp(self, partition, f):
    intervals = self.make_intervals(partition, f)
    for i in range(len(intervals) - 1):
      partition[i+1] = self.new_u(intervals[i], intervals[i+1])

  def make_partition(self, u_range, u_num):
    partition = [None]*u_num
    for i in range(u_num):
      u = (u_range[0] * (u_num - 1 - i) + u_range[1] * i) / (u_num - 1)
      partition[i] = u
    return partition

  def make_intervals(self, partition, f):
    u_num = len(partition)
    return [Interval(partition[i], partition[i+1], f) for i in range(u_num - 1)]

  def new_u(self, interval1, interval2):
    delta = interval1.delta + interval2.delta
    delta1 = interval1.ave * delta / (interval1.ave + interval2.ave)
    return interval1.u[0] + delta1

  def evaluate(self, u):
    start = self.u_range[0]
    for i in range(self.resolution):
      if start + self.width >= u:
        if i == self.resolution - 1:
          return self.partition[i]
        ratio = (u - start) / self.width
        base = self.partition[i]
        upper = self.partition[i+1]
        return base + ratio*(upper - base)
      start += self.width

class Interval:
  def __init__(self, low, high, f):
    self.u = [low, high]
    self.vals = [f(high), f(low)]
    self.delta = high - low
    self.ave = (self.vals[0] + self.vals[1]) / 2.0
