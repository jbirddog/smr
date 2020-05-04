
class DeepMerge(object):
    # Merges two deeply nested json-like dictionaries,
    # useful for updating things like task data.
    # I know in my heart, that this isn't completely correct.
    # But I don't want to create a dependency, and this is passing
    # all the failure points I've found so far.  So I'll just
    # keep plugging away at ti.

    @staticmethod
    def merge(a, b, path=None, update=True):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if a[key] == b[key]:
                    continue
                elif isinstance(a[key], dict) and isinstance(b[key], dict):
                    DeepMerge.merge(a[key], b[key], path + [str(key)])
                elif isinstance(a[key], list) and isinstance(b[key], list):
                    DeepMerge.merge_array(a[key], b[key], path + [str(key)])
                else:
                    raise Exception(
                        'Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    @staticmethod
    def merge_array(a, b, path=None):

        for idx, val in enumerate(b):
            if isinstance(b[idx], dict):  # Recurse back on dictionaries.
                # If lists of dictionaries get out of order, this might
                # cause us some pain.
                if len(a) > idx:
                    a[idx] = DeepMerge.merge(a[idx], b[idx], path + [str(idx)])
                else:
                    a.append(b[idx])
            else: # Just merge whatever it is back in.
                a.extend(x for x in b if x not in a)

