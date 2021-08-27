from autoconf import conf
from autoconf.tools.decorators import profile_func

class MockClass:

    def __init__(self, value):

        self._value = value

    @property
    @profile_func
    def value(self):
        return self._value

def test__profile_decorator_times_decorated_function(files_directory):

    conf.instance.push(files_directory / "profiling")

    cls = MockClass(value=1.0)
    cls.value

    assert "value" in cls._profiling_dict
