#!/usr/bin/env python

from docstring_parser import parse
docstring = parse(
    """Return random numbers between a and b.

    Args:
        a (float): Lower bound
        b (float): Upper bound
        size (int): size

    Returns:
        list : list of float

    """)

print(docstring.params[0].arg_name)
print(docstring.params[0].type_name)


