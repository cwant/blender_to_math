import bpy, bmesh
from blender_to_math.path_functions import *

def function_1d_to_bmesh(f, **kwargs):
  t_num = kwargs.get('t_num')
  if t_num == None or t_num < 2: raise ValueError('Need t_num')
  t1 = kwargs.get('t1')
  if t1 == None: raise ValueError('Need t1')
  t2 = kwargs.get('t2')
  if t2 == None: raise ValueError('Need t2')

  cyclic = kwargs.get('cyclic') or False
  bm = bmesh.new()
  t = t1
  vert_first = vert_last = vert = None
  t_inc = t2 - t1
  if cyclic: t_inc /= t_num
  else: t_inc /= (t_num - 1)
  for i in range(t_num):
    xyz = f(t)
    vert_last = vert
    vert = bm.verts.new(xyz)
    if not vert_first: vert_first = vert
    t += t_inc
    if i > 0:
      edge = bm.edges.new((vert_last, vert))
  if cyclic:
    edge = bm.edges.new((vert, vert_first))
  return bm

def function_2d_to_bmesh(f, **kwargs):
  u_num = kwargs.get('u_num')
  if u_num == None or u_num < 2: raise ValueError('Need u_num')
  u1 = kwargs.get('u1')
  if u1 == None: raise ValueError('Need u1')
  u2 = kwargs.get('u2')
  if u2 == None: raise ValueError('Need u2')
  u_cyclic = kwargs.get('u_cyclic') or False

  v_num = kwargs.get('v_num')
  if v_num == None or v_num < 2: raise ValueError('Need v_num')
  v1 = kwargs.get('v1')
  if v1 == None: raise ValueError('Need v1')
  v2 = kwargs.get('v2')
  if v2 == None: raise ValueError('Need v2')
  v_cyclic = kwargs.get('v_cyclic') or False

  u_inc = u2 - u1
  if u_cyclic: u_inc /= u_num
  else: u_inc /= (u_num - 1)

  v_inc = v2 - v1
  if v_cyclic: v_inc /= v_num
  else: v_inc /= (v_num - 1)

  bm = bmesh.new()

  verts = []
  u = u1
  for i in range(u_num):
    verts.append([])
    v = v1
    for j in range(v_num):
      xyz = f(u, v)
      verts[i].append(bm.verts.new(xyz))
      v += v_inc
    u += u_inc

  faces_u = u_num
  if not u_cyclic: faces_u -= 1
  faces_v = v_num
  if not v_cyclic: faces_v -= 1

  for i in range(faces_u):
    for j in range(faces_v):
      i_next = (i + 1) % u_num
      j_next = (j + 1) % v_num
      bm.faces.new((verts[i][j], verts[i_next][j],
                    verts[i_next][j_next], verts[i][j_next]))
      
  return bm
