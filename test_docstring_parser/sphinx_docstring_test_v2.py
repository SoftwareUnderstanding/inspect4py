#!/usr/bin/env python

from docstring_parser import parse
docstring = parse(
    """Return random numbers between a and b.

        :param a : Lower bound
        :type a: float
        :param b : Upper bound
        :type b: float
        :param size: size
        :type size: int
        :raises ValueError: exc desc
        :return: list of float
        :rtype: list

    """)

print(docstring.params[0].arg_name)
print(docstring.params[0].type_name)
print(docstring.returns.type_name)
print(docstring.returns.description)
print(docstring.raises[0].type_name)
print(docstring.raises[0].description)


