from pathlib import Path
from functools import reduce
import sys
import os

class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


def get_directory_structure(rootdir, ignore_set):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    dir = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
         ignore=0
         folders = path[start:].split(os.sep)
         for i in ignore_set:
             if i in folders:
                 ignore=1
             
         if not ignore:
             subdir = dict.fromkeys(files)
             subdir=  dict_clean(subdir) 
             parent = reduce(dict.get, folders[:-1], dir)
             parent[folders[-1]] = subdir
    
    return dir

def dict_clean(dict):
    result = {}
    for key, value in dict.items():
        if value is None and 'pyc' not in key:
            if '.py' in key:
                value = 'python script'
            elif '.txt' in key  or '.md' in key or 'LICENSE' in key:
                value = "text file"

            elif '.pdf' in key:
                value = 'pdf file'

            elif '.csv' in key:
                value = 'csv file'

            elif '.png' in key or '.PNG' in key or '.svg' in key or '.SVG' in key:
                 value = 'plot file'

            elif 'Dockerfile' in key:
                 value = 'docker file'

            else:
                 value = 'other type of file'
        result[key] = value
    return result

