import re
import logging
import uuid
from stix2validator import validate_instance, print_results
from . import observable
# convert JSON data to STIX object using map_data and transformers


def convert_to_stix(datasource, map_data, data, transformers, options):
    ds2stix = DataSourceObjToStixObj(
        datasource, map_data, transformers, options)

    # map data list to list of transformed objects
    results = list(map(ds2stix.transform, data))
    return results


class DataSourceObjToStixObj:

    def __init__(self, datasource, ds_to_stix_map, transformers, options):
        self.datasource = datasource
        self.ds_to_stix_map = ds_to_stix_map
        self.transformers = transformers

        # parse through options
        self.stix_validator = options.get('stix_validator', False)
        self.cybox_default = options.get('cybox_default', True)

        self.properties = observable.properties

    @staticmethod
    def _get_value(obj, ds_key, transformer):
        """ get value from source object, transforming if specified """
        if ds_key not in obj:
            logging.debug('{} not found in object'.format(ds_key))
            return None
        ret_val = obj[ds_key]
        if transformer is not None:
            return transformer.transform(ret_val)
        return ret_val

    @staticmethod
    def _add_property(key, obj, stix_value):
        split_key = key.split('.')
        child_obj = obj
        parent_props = split_key[0:-1]
        for prop in parent_props:
            if prop not in child_obj:
                child_obj[prop] = {}
            child_obj = child_obj[prop]
        child_obj[split_key[-1]] = stix_value

    @staticmethod
    def _handle_cybox_key_def(key_to_add, observation, stix_value, obj_name_map, obj_name):
        obj_type, obj_prop = key_to_add.split('.', 1)
        objs_dir = observation['objects']
        if obj_name in obj_name_map:
            obj = objs_dir[obj_name_map[obj_name]]
        else:
            obj = {'type': obj_type}
            obj_dir_key = str(len(objs_dir))
            objs_dir[obj_dir_key] = obj
            if obj_name is not None:
                obj_name_map[obj_name] = obj_dir_key
        DataSourceObjToStixObj._add_property(obj_prop, obj, stix_value)

    @staticmethod
    def _valid_regex(props_map, key, stix_value):
        if key in props_map and 'valid_regex' in props_map[key]:
            pattern = re.compile(props_map[key]['valid_regex'])
            if not pattern.match(str(stix_value)):
                return False
        return True

    @staticmethod
    def _valid_stix_value(props_map, key, stix_value):
        return (stix_value is not None and
                DataSourceObjToStixObj._valid_regex(props_map, key, stix_value))

    def transform(self, obj):
        """
        Transforms the given object in to a STIX observation based on the mapping file and transform functions

        :param obj: the datasource object that is being converted to stix
        :return: the input object converted to stix valid json
        """

        object_map = {}
        stix_type = 'observed-data'
        ds_map = self.ds_to_stix_map
        transformers = self.transformers
        observation = {
            'x_com_ibm_uds_datasource': {'id': self.datasource['id'], 'name': self.datasource['name']},
            'id': stix_type + '--' + str(uuid.uuid4()),
            'type': stix_type,
            'objects': {},
        }
        # create normal type objects
        for ds_key in obj:
            if ds_key not in ds_map:
                logging.debug('{} is not found in map, skipping'.format(ds_key))
                continue
            # get the stix keys that are mapped
            ds_key_def_obj = self.ds_to_stix_map[ds_key]
            ds_key_def_list = ds_key_def_obj if isinstance(ds_key_def_obj, list) else [ds_key_def_obj]
            for ds_key_def in ds_key_def_list:
                if ds_key_def is None or 'key' not in ds_key_def:
                    logging.debug('{} is not valid (None, or missing key)'.format(ds_key_def))
                    continue

                key_to_add = ds_key_def['key']
                transformer = transformers[ds_key_def['transformer']] if 'transformer' in ds_key_def else None

                if ds_key_def.get('cybox', self.cybox_default):
                    object_name = ds_key_def.get('object')
                    if 'references' in ds_key_def:
                        stix_value = object_map[ds_key_def['references']]
                    else:
                        stix_value = DataSourceObjToStixObj._get_value(obj, ds_key, transformer)
                        if not DataSourceObjToStixObj._valid_stix_value(self.properties, key_to_add, stix_value):
                            continue
                    DataSourceObjToStixObj._handle_cybox_key_def(key_to_add, observation, stix_value, object_map, object_name)
                else:
                    stix_value = DataSourceObjToStixObj._get_value(obj, ds_key, transformer)
                    if not DataSourceObjToStixObj._valid_stix_value(self.properties, key_to_add, stix_value):
                        continue
                    DataSourceObjToStixObj._add_property(key_to_add, observation, stix_value)

        # Validate each STIX object
        if self.stix_validator:
            validated_result = validate_instance(observation)
            print_results(validated_result)
        return observation
