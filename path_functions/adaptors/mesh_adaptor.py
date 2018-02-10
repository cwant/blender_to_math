import bpy, bmesh

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

class MeshAdaptor:
  def __init__(self, **kwargs):
    self.input_bmesh = kwargs.get('bmesh')
    if not self.input_bmesh:
      mesh = kwargs.get('mesh')
      if not mesh: raise ValueError('Need a mesh!')
      self.input_bmesh = bmesh.new()
      self.input_bmesh.from_mesh(mesh)
    self.vert_list = self.bmesh_to_vert_list()
    self.points = self.vert_list.to_list()
    self.cyclic = self.vert_list.cyclic
    # For faking bezier handles
    self.diffs = None

  def bmesh_to_vert_lists(self):
    # Mesh is assumed to be a collection of one or more lines
    # (verts and connecting edges)
    # Each disconnected piece is a member of the returned list
    verts_done = [False] * len(self.input_bmesh.verts) 
    vert_lists = []

    for vert in self.input_bmesh.verts:
      if verts_done[vert.index]: continue
      vert_list = OrderedVertList(vert)
      while(True):
        vert = vert_list.add_next()
        if vert: verts_done[vert.index] = True
        else: break
      while(True):
        vert = vert_list.add_prev()
        if vert: verts_done[vert.index] = True
        else: break
      if not vert_list.degenerate: vert_lists.append(vert_list)
    return vert_lists

  def bmesh_to_vert_list(self):
    vert_lists = self.bmesh_to_vert_lists()
    if len(vert_lists) > 0: return vert_lists[0]
    raise ValueError('No vert_list could be created')

  def point_list(self, **kwargs):
    return self.points

  # Faking bezier handles
  def calculate_diffs(self):
    if len(self.points) < 2: return
    self.diffs = []
    self.diffs.append((self.points[1] - self.points[0]).normalized())
    for i in range(1, len(self.points) - 1):
      p1 = (self.points[i] - self.points[i-1]).normalized()
      p2 = (self.points[i+1] - self.points[i]).normalized()
      self.diffs.append((p2+p1).normalized())
    self.diffs.append((self.points[-1] - self.points[-2]).normalized())

  def left_handles(self, **kwargs):
    if not self.diffs: self.calculate_diffs()
    handles = [ self.points[0] ]
    for i in range(1, len(self.points)):
      scale = (self.points[i] - self.points[i-1]).length / 2.0
      handles.append(self.points[i] - self.diffs[i] * scale)
    return handles

  def right_handles(self, **kwargs):
    if not self.diffs: self.calculate_diffs()
    handles = []
    for i in range(len(self.points) - 1):
      scale = (self.points[i+1] - self.points[i]).length / 2.0
      handles.append(self.points[i] + self.diffs[i] * scale)
    handles.append(self.points[-1])
    return handles
