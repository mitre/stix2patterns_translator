from data_models.car import CAR_OBJECT_MAP, CAR_FIELD_MAP
from data_models.base import ValueTransform
from collections import abc, defaultdict
from copy import deepcopy
import re
import sys
from ipdb import set_trace as st

ROOT_OBJECT_ID = 'root'

def transform(car_event):
  data_model = car_event['data_model']
  obj_type = data_model['object']

  result = {}

  if obj_type in CAR_OBJECT_MAP:
    result[ROOT_OBJECT_ID] = { 'type': CAR_OBJECT_MAP.get(obj_type) }
  else:
    print(f"WARNING: STIX type for CAR type '{obj_type}' not found. Continuing anyway.", file=sys.stderr)

  if obj_type not in CAR_FIELD_MAP:
    print(f"WARNING: Field map does not contain CAR type '{obj_type}'. Returning result as-is.", file=sys.stderr)
    return result

  for field in data_model['fields']:
    if field not in CAR_FIELD_MAP[obj_type]['fields']:
      print(f"WARNING: Field {field} not found in field map. Skipping field.", file=sys.stderr)
      continue

    field_mapping = CAR_FIELD_MAP[obj_type]['fields'][field]
    field_value = data_model['fields'][field]

    if type(field_mapping) is ValueTransform:
      value_parts = field_mapping.transform(field_value)
      if len(value_parts) != len(field_mapping.field_paths):
        print(f"WARNING: Field value '{field_value}' partitioned into different number of parts than expected. Continuing anyway.", file=sys.stderr)
      values = list(zip(field_mapping.field_paths, value_parts))
    else:
      values = [ (field_mapping, field_value) ]
    
    for field_path, value in values:
      transformed_field = transform_field(field_path, value)

      result = merge_dict(
        result,
        transformed_field
      )

  return result

def split_field_and_type(field):
  extraction = re.search('^(.*)\((.*)\)$', field)

  # this is just plain old 'fieldname'
  if extraction is None:
    return { 'field': field }

  groups = extraction.groups()

  # this is a hit on 'fieldname(type)'
  return { 'field': groups[0], 'type': groups[1] }

def compute_ref_key(current_id, field_key):
  return '.'.join([current_id, field_key])

def add_field_value(sub_result, field, value):
  extraction = split_field_and_type(field)
  field_key = extraction['field']
  if len(extraction) == 2:
    print(f"WARNING: Non-reference property '{field}' should not have type. Ignoring type.", file=sys.stderr)
  sub_result[field_key] = value

def add_field_ref(result, sub_result, result_key, field):
  extraction = split_field_and_type(field)
  field_key = extraction['field']
  ref_key = compute_ref_key(result_key, field_key)
  sub_result[field_key] = ref_key
  if ref_key not in result:
    result[ref_key] = {}
  if len(extraction) == 2:
    result[ref_key]['type'] = extraction['type']
  else:
    print(f"WARNING: Reference property '{field}' should have object type. Continuing anyway with type omitted.", file=sys.stderr)

def transform_field(field_path, value):
  field_components = field_path.split('.')

  current_id = ROOT_OBJECT_ID
  result = { current_id: {} }
  sub_result = result[current_id]

  for field_comp in field_components[:-1]:
    extraction = split_field_and_type(field_comp)
    field_key = extraction['field']
    if field_key.endswith('ref'):
      add_field_ref(result, sub_result, current_id, field_comp)
      current_id = compute_ref_key(current_id, field_key)
      sub_result = result[current_id]
    else:
      sub_result[field_key] = {}
      sub_result = sub_result[field_key]
      current_id = compute_ref_key(current_id, field_key)

  add_field_value(sub_result, field_components[-1], value)

  return result

# deepcopy may be excessive, not sure how much cost it adds.
# in the event of non-merged collision, the value in d2 overrides the value in d1
def merge_dict(d1, d2, depth=-1):
  result = deepcopy(d1)
  for k,v in d2.items():
    if (
      k not in result or
      depth == 0 or
      not isinstance(v, abc.Mapping) or
      not isinstance(result[k], abc.Mapping)
    ):
      result[k] = deepcopy(v)
    else:
      result[k] = merge_dict(result[k], v, depth=depth-1)
  return result
