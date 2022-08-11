import re
from typing import Any


PARAM_REGEX = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")


def compile_path(
    path: str,
):
    path_regex = "^"
    path_format = ""

    idx = 0
    param_convertors = {}
    for m in PARAM_REGEX.finditer(path):
        param_name, convertor_type = m.groups("str")

        convertor = CONVERTOR_TYPES[convertor_type]

        path_regex += re.escape(path[idx: m.start()])
        path_regex += f"(?P<{param_name}>{convertor.regex})"

        path_format += path[idx: m.start()]
        path_format += f"{param_name}"

        param_convertors[param_name] = convertor

        idx = m.end()

    path_regex += re.escape(path[idx:]) + "$"
    path_format += path[idx:]

    return re.compile(path_regex), path_format, param_convertors


class Convertor:
    regex = ""

    def convert(self, value: str) -> Any:
        raise NotImplementedError


class StringConvertor(Convertor):
    regex = "[^/]+"

    def convert(self, value: str) -> Any:
        return value


class IntegerConvertor(Convertor):
    regex = "[0-9]+"

    def convert(self, value: str) -> Any:
        return int(value)


CONVERTOR_TYPES = {
    "str": StringConvertor(),
    "int": IntegerConvertor()
}
