import bpy, bmesh
import blender_to_math
from importlib import reload
reload(blender_to_math)
import blender_to_math.path_functions
reload(blender_to_math.path_functions)
from blender_to_math.path_functions.linear import *
from blender_to_math.path_functions.bezier import *
from blender_to_math import *

def main():
  mesh = bpy.data.objects["Profile"].data
  create_profile_line(mesh)

  curve = bpy.data.objects["BezierCurve"].data
  create_bezier_spline(curve)

def create_profile_line(mesh):
  output = 'Profile.line'
  input_options = { 't1': 0.0, 't2': 1.0, 'cyclic': False, 'mesh': mesh }
  output_options = { 't1': 0.0, 't2': 1.0, 't_num': 100 }

  #function = PiecewiseLinearFunction(**input_options)
  function = BezierFunction(**input_options)

  bm = curve_to_bmesh(function.evaluate, **output_options)

  ob = get_or_create_mesh_object(output)
  me = ob.data
  bm.to_mesh(me)
  me.update()

def create_bezier_spline(curve):
  output_name = 'Profile.curve'
  input_options = { 't1': 0.0, 't2': 1.0, 'cyclic': False, 'curve': curve}
  output_options = { 't1': 0.0, 't2': 1.0, 't_num': 100 }

  function = BezierFunction(**input_options)
  bm = curve_to_bmesh(function.evaluate, **output_options)

  ob = get_or_create_mesh_object(output_name)
  me = ob.data
  bm.to_mesh(me)
  me.update()

def create_profile_spline(bm):
  options = { 't1': 0.0, 't2': 1.0, 't_num': 100, 'cyclic': False}
  surface = bmesh_to_piecewise_cubic(bm, **options)

  bm = curve_to_bmesh(surface.evaluate, **options)
  bm.to_mesh(me)
  me.update()

def get_or_create_mesh_object(name):
  if name in bpy.data.objects:
    return bpy.data.objects[name]
  me = bpy.data.meshes.new(name)
  ob = bpy.data.objects.new(name, me)
  scn = bpy.context.scene
  scn.objects.link(ob)
  return ob
  
