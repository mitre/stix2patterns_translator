import re

class ValueTransform(object):
  def __init__(self, transform_func, *field_paths):
    self.transform_func = transform_func
    self.field_paths = field_paths

  def transform(self, value):
    transformed_val = self.transform_func(value)
    if type(transformed_val) is not tuple:
      return (transformed_val,)
    else:
      return transformed_val

def split_path(path):
  fname = re.split(r'[\\/]', path)[-1]
  dirname = path[0:len(path)-len(fname)]
  return dirname, fname
