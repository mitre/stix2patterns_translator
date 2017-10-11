import argparse
import logging
from enum import Enum
from stix2patterns_translator.parser import generate_query
from stix2patterns_translator import data_models
from stix2patterns_translator import search_platforms

logger = logging.getLogger(__name__)

class SearchPlatforms(Enum):
    ELASTIC = 'elastic'
    SPLUNK = 'splunk'


class DataModels(Enum):
    CAR = 'car'
    CIM = 'cim'


class InputToEnumAction(argparse.Action):
    """ This is used to resolve user / string input into one of the types defined by the Enums above."""
    def __init__(self, option_strings, dest, **kwargs):
        self.value_to_enum_mapping = {}
        for e in (SearchPlatforms, DataModels):
            self.value_to_enum_mapping.update({c.value: c for c in e})
        super(InputToEnumAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        # print('%r %r %r' % (namespace, value, option_string))
        setattr(namespace, self.dest, self.value_to_enum_mapping[value])


STIX2SearchPlatforms = {SearchPlatforms.ELASTIC,SearchPlatforms.SPLUNK}
STIX2DataModels = {DataModels.CAR, DataModels.CIM}

def translate(pattern: str, search_platform: STIX2SearchPlatforms=SearchPlatforms.ELASTIC,
                           data_model: STIX2DataModels=DataModels.CAR) -> str:
    logger.info("Converting STIX2 Pattern to {}-{}".format(data_model, search_platform))
    query_object = generate_query(pattern)

    if data_model == DataModels.CAR:
        data_model_mapper = data_models.CarDataMapper()
    elif data_model == DataModels.CIM:
        data_model_mapper = data_models.CimDataMapper()
    else:
        raise NotImplementedError("{}".format(data_model))

    if search_platform == SearchPlatforms.ELASTIC:
        res = search_platforms.elastic_query_string.translate_pattern(query_object,
                                                                                                       data_model_mapper)
    elif search_platform == SearchPlatforms.SPLUNK:
        res = search_platforms.splunk_search.translate_pattern(query_object,
                                                                                                       data_model_mapper)
    else:
        raise NotImplementedError

    return res

def main():
    parser = argparse.ArgumentParser(description='<placeholder description>')
    parser.add_argument("--output-language", help="language of translated query", choices=[s._value_ for s in SearchPlatforms], required=True, action=InputToEnumAction)
    parser.add_argument("--output-data-model", help="Translate to this Data Model", choices=[d._value_ for d in DataModels], required=True, action=InputToEnumAction)
    parser.add_argument("pattern", help="The Query or Pattern to be translated.")
    args = parser.parse_args()
    result = translate(args.pattern, args.output_language, args.output_data_model)
    print(result)
    exit()

if __name__ == '__main__':
    main()
