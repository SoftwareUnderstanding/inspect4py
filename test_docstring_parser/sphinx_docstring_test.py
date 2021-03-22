#!/usr/bin/env python

from docstring_parser import parse
docstring = parse(
    """Return random numbers between a and b.

        :param float a : Lower bound
        :param float b : Upper bound
        :param int size: size
        :raises ValueError: exc desc
        :return list : list of float

    """)

print(docstring.params[0].arg_name)
print(docstring.params[0].type_name)
print(docstring.returns.type_name)
print(docstring.returns.description)
print(docstring.raises[0].type_name)
print(docstring.raises[0].description)
