import bpy
from math import pi
import blender_to_math
from importlib import reload

reload(blender_to_math)

import blender_to_math.path_functions  # noqa: E402
reload(blender_to_math.path_functions)

from blender_to_math.path_functions.linear \
    import PiecewiseLinearFunction  # noqa: E402
from blender_to_math.path_functions.bezier \
    import BezierFunction  # noqa: E402
from blender_to_math.path_functions.revolution_function \
    import RevolutionFunction  # noqa: E402
from blender_to_math.path_functions \
    import function_1d_to_bmesh, function_2d_to_bmesh  # noqa: E402


def main():
    mesh = bpy.data.objects["Profile.mesh"].data
    create_profile_line(output_name='Profile.mesh.line', mesh=mesh,
                        location=(15, -15, 0))
    create_bezier_spline(output_name='Profile.mesh.curve', mesh=mesh,
                         location=(15, -30, 0))
    create_bezier_surface(output_name='Profile.mesh.surface', mesh=mesh,
                          location=(15, -45, 0))

    curve = bpy.data.objects["Profile.curve"].data
    create_profile_line(output_name='Profile.curve.line', curve=curve,
                        location=(-15, -15, 0))
    create_bezier_spline(output_name='Profile.curve.curve', curve=curve,
                         location=(-15, -30, 0))
    create_bezier_surface(output_name='Profile.curve.surface', curve=curve,
                          location=(-15, -45, 0))


def create_profile_line(**kwargs):
    output_name = kwargs.get('output_name')
    input_options = {'t1': 0.0, 't2': 1.0}
    output_options = {'t1': 0.0, 't2': 1.0, 't_num': 100}

    function = PiecewiseLinearFunction(**{**kwargs, **input_options})
    if function.cyclic:
        output_options['cyclic'] = True
    bm = function_1d_to_bmesh(function.evaluate, **output_options)

    ob = get_or_create_mesh_object(output_name, **kwargs)
    me = ob.data
    bm.to_mesh(me)
    me.update()


def create_bezier_spline(**kwargs):
    output_name = kwargs.get('output_name')
    input_options = {'t1': 0.0, 't2': 1.0}
    output_options = {'t1': 0.0, 't2': 1.0, 't_num': 100}

    function = BezierFunction(**{**kwargs, **input_options})
    if function.cyclic:
        output_options['cyclic'] = True

    bm = function_1d_to_bmesh(function.evaluate, **output_options)

    ob = get_or_create_mesh_object(output_name, **kwargs)
    me = ob.data
    bm.to_mesh(me)
    me.update()


def create_bezier_surface(**kwargs):
    output_name = kwargs.get('output_name')
    input_options = {'t1': 0.0, 't2': 1.0}
    output_options = {'u1': 0.0, 'u2': 1.0, 'u_num': 50,
                      'v1': 0.0, 'v2': 2*pi, 'v_num': 50, 'v_cyclic': True}

    function_1d = BezierFunction(**{**kwargs, **input_options})
    if function_1d.cyclic:
        output_options['u_cyclic'] = True
    function_2d = RevolutionFunction(function=function_1d, axis=(0, 1, 0))
    bm = function_2d_to_bmesh(function_2d.evaluate, **output_options)

    ob = get_or_create_mesh_object(output_name, **kwargs)
    me = ob.data
    bm.to_mesh(me)
    me.update()


def get_or_create_mesh_object(name, **kwargs):
    if name in bpy.data.objects:
        ob = bpy.data.objects[name]
    else:
        me = bpy.data.meshes.new(name)
        ob = bpy.data.objects.new(name, me)
        scn = bpy.context.scene
        scn.objects.link(ob)
    location = kwargs.get('location')
    if location:
        ob.location = location
    return ob
