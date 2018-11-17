import os
import sys
import pytest

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(this_dir + '/../..')

from blender_to_math.path_functions.function_common \
    import FunctionCommon  # noqa: E402


class TestFunctionCommon(object):
    def test_experiment(self):
        with pytest.raises(ValueError):
            FunctionCommon()
