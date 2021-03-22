#!/usr/bin/env python

from docstring_parser import parse
docstring = parse(
    """Return random numbers between a and b.

    Parameters
    ----------
    a : float
        Lower bound.
    b : float
        Upper bound.
    size : int, optional
        Number of numbers to return. Defaults to 1.

    Returns
    -------
    ns : list of float
    """)

print(docstring.params[0].arg_name)
print(docstring.params[0].type_name)


