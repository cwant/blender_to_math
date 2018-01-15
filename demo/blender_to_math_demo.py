import bpy, bmesh
from blender_to_math import *

def main():
  me = bpy.data.objects["Profile"].data
  bm = bmesh.new()
  bm.from_mesh(me)

  curve = bpy.data.objects["BezierCurve"].data
  create_bezier_spline(curve)

def create_profile_spline(bm):
  options = { 't1': 0.0, 't2': 1.0, 't_num': 100, 'cyclic': False}
  surface = bmesh_to_piecewise_cubic(bm, **options)
  if 'Profile.curve' in bpy.data.objects:
    ob = bpy.data.objects['Profile.curve']
    me = ob.data
  else:
    me = bpy.data.meshes.new('Profile.curve')
    ob = bpy.data.objects.new('Profile.curve', me)
    scn = bpy.context.scene
    scn.objects.link(ob)

  bm = curve_to_bmesh(surface.evaluate, **options)
  bm.to_mesh(me)
  me.update()

def create_bezier_spline(curve):
  options = { 'curve': curve, 't1': 0.0, 't2': 1.0, 't_num': 100,
              'cyclic': False}
  surface = BezierToMath(**options)
  if 'Profile.curve' in bpy.data.objects:
    ob = bpy.data.objects['Profile.curve']
    me = ob.data
  else:
    me = bpy.data.meshes.new('Profile.curve')
    ob = bpy.data.objects.new('Profile.curve', me)
    scn = bpy.context.scene
    scn.objects.link(ob)

  bm = curve_to_bmesh(surface.evaluate, **options)
  bm.to_mesh(me)
  me.update()
