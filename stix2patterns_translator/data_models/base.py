class DataMappingException(Exception):
    pass

class DataMapper(object):
    # TODO:
    # This mapping is not super straightforward. It could use the following improvements:
    # * Registry keys need to pull the path apart from the key name, I believe. Need to investigate with Splunk
    # * Need to validate that the src and dest aliases are working
    # * Need to add in the static attributes, like the `object_category` field
    # * Need to verify "software" == "inventory"
    # * Need to figure out network traffic when it's for web URLs
    # * Hashes are kind of hacky, just hardcoded. Probably needs to be a regex
    def map_object(self, stix_object_name):
        if stix_object_name in self.MAPPINGS and self.MAPPINGS[stix_object_name] != None:
            return self.MAPPINGS[stix_object_name][self.type_name]
        else:
            raise DataMappingException("Unable to map object `{}` into {}".format(stix_object_name, self.data_model_name))

    def map_field(self, stix_object_name, stix_property_name):
        if stix_object_name in self.MAPPINGS and stix_property_name in self.MAPPINGS[stix_object_name]["fields"]:
            mapping = self.MAPPINGS[stix_object_name]["fields"][stix_property_name]
            if isinstance(mapping, dict):
              return list(mapping.keys())[0]
            elif isinstance(mapping, str):
              return mapping
        else:
            raise DataMappingException("Unable to map property `{}:{}` into {}".format(stix_object_name, stix_property_name, self.data_model_name))

    def map_value(self, stix_object_name, stix_property_name, stix_property_value):
        if stix_object_name in self.MAPPINGS and stix_property_name in self.MAPPINGS[stix_object_name]["fields"]:
            mapping = self.MAPPINGS[stix_object_name]["fields"][stix_property_name]
            if isinstance(mapping, dict):
              value_mappings = list(mapping.values())[0]
              if stix_property_value in value_mappings:
                return value_mappings[stix_property_value]
            elif isinstance(mapping, str):
                return stix_property_value
        raise DataMappingException("Unable to map property value `{}:{} = {}` into {}".format(stix_object_name, stix_property_name, stix_property_value, self.data_model_name))
