import bpy, bmesh
from blender_to_math.path_functions import *

def bmesh_to_piecewise_linears(bm, **kwargs):
  vert_lists = bmesh_to_vert_lists(bm)
  piecewise_list = []
  for vert_list in vert_lists:
    options = { 'vert_list': vert_list }
    piecewise = PiecewiseLinear(**{**kwargs, **options})
    piecewise_list.append(piecewise)
  return piecewise_list

def bmesh_to_piecewise_linear(bm, **kwargs):
  vert_list = bmesh_to_vert_list(bm)
  options = { 'vert_list': vert_list }
  if not vert_list: return None
  return PiecewiseLinear(**{**kwargs, **options})

def bmesh_to_piecewise_cubics(bm, **kwargs):
  vert_lists = bmesh_to_vert_lists(bm)
  piecewise_list = []
  for vert_list in vert_lists:
    piecewise = PiecewiseCubic(vert_list, **kwargs)
    piecewise_list.append(piecewise)
  return piecewise_list

def bmesh_to_piecewise_cubic(bm, **kwargs):
  vert_list = bmesh_to_vert_list(bm)
  if not vert_list: return None
  return PiecewiseCubic(vert_list, **kwargs)

def bmesh_to_spline_revolutions(bm, **kwargs):
  splines = bmesh_to_splines(bm, **kwargs)
  if not splines: return None
  spline_revolutions = []
  for spline in splines:
    spline_revolutions.append(SplineRevolution(spline, **kwargs))
  return spline_revolutions

def bmesh_to_spline_revolution(bm, **kwargs):
  spline = bmesh_to_spline(bm, **kwargs)
  if not spline: return None
  return SplineRevolution(spline, **kwargs)

def curve_to_bmesh(f, **kwargs):
  t_num = kwargs.get('t_num')
  if t_num == None or t_num < 2: raise ValueError('Need t_num')
  t1 = kwargs.get('t1')
  if t1 == None: raise ValueError('Need t1')
  t2 = kwargs.get('t2')
  if t2 == None: raise ValueError('Need t2')

  cyclic = kwargs.get('cyclic') or False
  bm = bmesh.new()
  t = t1
  v1 = v_last = v = None
  t_inc = t2 - t1
  if cyclic: t_inc /= t_num
  else: t_inc /= (t_num - 1)
  for i in range(t_num):
    xyz = f(t)
    v_last = v
    v = bm.verts.new(xyz)
    if not v1: v1 = v
    t += t_inc
    if i > 0:
      edge = bm.edges.new((v_last, v))
  if cyclic:
    edge = bm.edges.new((v, v1))
  return bm
