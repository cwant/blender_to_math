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


# Optional, for the tessagon demos
# https://github.com/cwant/tessagon
is_tessagon_loaded = False
try:
    from tessagon.types.hex_tessagon import HexTessagon  # noqa: E402
    from tessagon.adaptors.blender_adaptor import BlenderAdaptor
    is_tessagon_loaded = True
except ImportError:
    print('Could not load tessagon, some demoes skipped')

# Optional, for the wire_skin demos
# https://github.com/cwant/wire_skin
is_wire_skin_loaded = False
try:
    from wire_skin import WireSkin  # noqa: E402
    is_wire_skin_loaded = True
except ImportError:
    print('Could not load wire_skin, some demoes skipped')


def main():
    mesh = bpy.data.objects["Profile.mesh"].data
    create_profile_line(output_name='Profile.mesh.line', mesh=mesh,
                        location=(15, -15, 0))
    create_bezier_spline(output_name='Profile.mesh.curve', mesh=mesh,
                         location=(15, -30, 0))
    function = create_bezier_surface(output_name='Profile.mesh.surface',
                                     mesh=mesh,
                                     location=(15, -45, 0))

    if is_tessagon_loaded:
        mesh = create_tessagon_surface(function,
                                       output_name='Profile.mesh.tessagon',
                                       location=(15, -60, 0))
        if is_wire_skin_loaded:
            create_wireskin_shape(mesh, output_name='Profile.mesh.wire_skin',
                                  location=(15, -75, 0))

    curve = bpy.data.objects["Profile.curve"].data
    create_profile_line(output_name='Profile.curve.line', curve=curve,
                        location=(-15, -15, 0))
    create_bezier_spline(output_name='Profile.curve.curve', curve=curve,
                         location=(-15, -30, 0))
    function = create_bezier_surface(output_name='Profile.curve.surface',
                                     curve=curve,
                                     location=(-15, -45, 0))

    if is_tessagon_loaded:
        mesh = create_tessagon_surface(function,
                                       output_name='Profile.curve.tessagon',
                                       location=(-15, -60, 0))
        if is_wire_skin_loaded:
            create_wireskin_shape(mesh,
                                  output_name='Profile.curve.wire_skin',
                                  location=(-15, -75, 0))


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
    return function_2d.evaluate


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


def create_tessagon_surface(function, **kwargs):
    output_name = kwargs.get('output_name')
    options = {'u_range': [0.0, 1.0], 'u_num': 10, 'u_cyclic': False,
               'v_range': [0.0, 2*pi], 'v_num': 10, 'v_cyclic': True,
               'function': function, 'adaptor_class': BlenderAdaptor}

    tessagon = HexTessagon(**options)
    bm = tessagon.create_mesh()
    ob = get_or_create_mesh_object(output_name, **kwargs)
    me = ob.data
    bm.to_mesh(me)
    me.update()
    return me


def create_wireskin_shape(mesh, **kwargs):
    output_name = kwargs.get('output_name')
    options = {
        'width': 0.5,
        'height': 0.5,
        'inside_radius': 0.23,
        'outside_radius': 0.23,
        'dist': 0.3,
    }
    wire_skin = WireSkin(mesh, **options)
    me = wire_skin.create_mesh()

    ob = get_or_create_mesh_object(output_name, **kwargs)
    ob.data = me
