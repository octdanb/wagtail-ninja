from typing import TypeAlias
# Hacky ?
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

