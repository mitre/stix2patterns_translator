from stix_shifter.src.json_to_stix import json_to_stix_translator
from stix_shifter.src import transformers


class TestTransform(object):
    @staticmethod
    def get_first(itr, constraint):
        return next(
            (obj for obj in itr if constraint(obj)),
            None
        )

    def test_common_prop(self):
        datasource = {'id': '123', 'name': 'sourcename'}
        map_data = {"time": {
            "key": "created",
            "cybox": False
        }}
        transformer = None
        options = {}
        data = {"time": "2018-03-20T13:54:59.952Z"}
        x = json_to_stix_translator.DataSourceObjToStixObj(
            datasource, map_data, transformer, options)
        result = x.transform(data)
        assert(result is not None)
        assert('created' in result)
        assert(result['created'] == data["time"])
        assert(result['type'] == "observed-data")
        assert('x_com_ibm_uds_datasource' in result)
        assert(result['x_com_ibm_uds_datasource']
               ['id'] == datasource['id'])
        assert(result['x_com_ibm_uds_datasource']
               ['name'] == datasource['name'])

    def test_observation_prop(self):
        datasource = {'id': '123', 'name': 'sourcename'}
        map_data = {"time": {
            "key": "first_observed",
            "cybox": False
        }}
        transformer = None
        options = {}
        data = {"time": "2018-03-20T13:54:59.952Z"}
        x = json_to_stix_translator.DataSourceObjToStixObj(
            datasource, map_data, transformer, options)
        result = x.transform(data)
        assert(result is not None)
        assert('first_observed' in result)
        assert(result['first_observed'] == data["time"])
        assert(result['type'] == "observed-data")
        assert('x_com_ibm_uds_datasource' in result)
        assert(result['x_com_ibm_uds_datasource']
               ['id'] == datasource['id'])
        assert(result['x_com_ibm_uds_datasource']
               ['name'] == datasource['name'])

    def test_simple_props(self):
        datasource = {'id': '123', 'name': 'sourcename'}
        map_data = {"ip": {
            "key": "ipv4-addr.value"
        }, "url": {"key": "url.value"},
            "domain": {
            "key": "domain-name.value"
        }, "payload": {
            "key": "artifact.payload_bin"
        }
        }
        transformer = None
        options = {}
        payload = "SomeBase64Payload"
        url = "https://example.com"
        domain = "example.com"
        ip_address = "127.0.0.1"
        data = {"ip": ip_address, "url": url,
                "domain": domain, "payload": payload}
        x = json_to_stix_translator.DataSourceObjToStixObj(
            datasource, map_data, transformer, options)
        result = x.transform(data)
        assert(result is not None)
        assert('objects' in result)
        objects = result['objects']
        assert(objects.keys() == {'0', '1', '2', '3'})

        vals = objects.values()

        curr_obj = TestTransform.get_first(vals,
            lambda o: o.get('type') == 'ipv4-addr')
        assert(curr_obj)
        assert(curr_obj['value'] == ip_address)

        curr_obj = TestTransform.get_first(vals,
            lambda o: o.get('type') == 'url')
        assert(curr_obj)
        assert(curr_obj['value'] == url)

        curr_obj = TestTransform.get_first(vals,
            lambda o: o.get('type') == 'domain-name')
        assert(curr_obj)
        assert(curr_obj['value'] == domain)

        curr_obj = TestTransform.get_first(vals,
            lambda o: o.get('type') == 'artifact')
        assert(curr_obj)
        assert(curr_obj['payload_bin'] == payload)


    def test_custom_props(self):
        datasource = {'id': '123', 'name': 'sourcename'}
        map_data = {"protocolid": {
            "key": "x_com_ibm_ariel.protocol_id",
            "cybox": False
        }, "logsourceid": {
            "key": "x_com_ibm_ariel.log_source_id",
            "cybox": False
        }, "qid": {
            "key": "x_com_ibm_ariel.qid",
            "cybox": False
        }, "magnitude": {
            "key": "x_com_ibm_ariel.magnitude",
            "cybox": False
        }, "identityip": {
            "key": "x_com_ibm_ariel.identity_ip",
            "cybox": False
        }, "test_linked_value_1": {
            "key": "x_com_ibm_test_linked_value.value_one",
            "cybox": False
        }, "test_linked_value_2": {
            "key": "x_com_ibm_test_linked_value.value_two",
            "cybox": False
        }}
        transformer = None
        options = {}
        data = {"protocolid": 255, "logsourceid": 126, "qid": 55500004,
                "identityip": "0.0.0.0", "magnitude": 4, "test_linked_value_1": 1, "test_linked_value_2": 2}
        x = json_to_stix_translator.DataSourceObjToStixObj(
            datasource, map_data, transformer, options)
        result = x.transform(data)
        assert(result is not None)
        assert('x_com_ibm_ariel' in result)
        attributes = result['x_com_ibm_ariel']
        assert(attributes['identity_ip'] == '0.0.0.0')
        assert(attributes['log_source_id'] == 126)
        assert(attributes['qid'] == 55500004)
        assert(attributes['magnitude'] == 4)
        assert(attributes['protocol_id'] == 255)

        assert('x_com_ibm_test_linked_value' in result)
        attributes = result['x_com_ibm_test_linked_value']
        assert(attributes['value_one'] == 1)
        assert(attributes['value_two'] == 2)

    def test_to_integer_transformer(self):
        datasource = {'id': '123', 'name': 'sourcename'}
        map_data = {
            "eventCount": {
                "key": "number_observed",
                "transformer": "ToInteger",
                "cybox": False
            },
        }
        options = {}
        data = [{"eventCount": "5"}]
        result = json_to_stix_translator.convert_to_stix(
            datasource, map_data, data, transformers.get_all_transformers(), options)[0]
        assert(result is not None)
        assert('objects' in result)
        objects = result['objects']
        assert(len(objects) == 0)
        assert('number_observed' in result)
        assert(result['number_observed'] == 5)

    def test_to_integer_transformer_error(self):
        datasource = {'id': '123', 'name': 'sourcename'}
        map_data = {
            "eventCount": {
                "key": "number_observed",
                "transformer": "ToInteger",
                "cybox": False
            },
        }
        options = {}
        data = [{"eventCount": "notaValidNumber"}]
        result = json_to_stix_translator.convert_to_stix(
            datasource, map_data, data, transformers.get_all_transformers(), options)[0]
        assert(result is not None)
        print (result)
        assert('number_observed' not in result)

    def test_to_string_transformer(self):
        datasource = {'id': '123', 'name': 'sourcename'}
        map_data = {
            "destinationip": [
                {
                    "key": "ipv4-addr.value",
                    "object": "dst_ip"
                },
                {
                    "key": "ipv6-addr.value",
                    "object": "dst_ip"
                },
                {
                    "key": "network-traffic.dst_ref",
                    "references": "dst_ip",
                    "object": "nt"
                }
            ],
            "sourceip": [
                {
                    "key": "ipv4-addr.value",
                    "object": "src_ip"
                },
                {
                    "key": "ipv6-addr.value",
                    "object": "src_ip"
                },
                {
                    "key": "network-traffic.src_ref",
                    "references": "src_ip",
                    "object": "nt"
                }
            ]
        }
        options = {}
        data = [{"sourceip": "1.1.1.1", "destinationip": "2.2.2.2"}]
        result = json_to_stix_translator.convert_to_stix(
            datasource, map_data, data, transformers.get_all_transformers(), options)[0]
        assert(result is not None)
        assert('objects' in result)
        objects = result['objects']
        assert(objects.keys() == {'0', '1', '2'})

        nt_object = TestTransform.get_first(objects.values(),
            lambda obj: obj.get('type') == 'network-traffic')
        assert(nt_object)
        assert(nt_object.get('dst_ref'))
        assert(nt_object.get('src_ref'))

        ip_ref = nt_object.get('dst_ref')
        assert(ip_ref in objects)  # destinationip
        ip_obj = objects[ip_ref]
        assert(ip_obj['type'] == 'ipv4-addr')
        assert(ip_obj['value'] == "2.2.2.2")

        ip_ref = nt_object.get('src_ref')
        assert(ip_ref in objects)  # sourceip
        ip_obj = objects[ip_ref]
        assert(ip_obj['type'] == 'ipv4-addr')
        assert(ip_obj['value'] == "1.1.1.1")

    def test_to_array_transformer(self):
        data_source = {'id': '123', 'name': 'sourcename'}
        map_data = {
            "destinationport": {
                "key": "network-traffic.dst_port",
                "cybox": "true",
                "object": "nt"
            },
            "sourceport": {
                "key": "network-traffic.src_port",
                "cybox": "true",
                "object": "nt"
            },
            "protocol": {
                "key": "network-traffic.protocols",
                "cybox": "true",
                "object": "nt",
                "transformer": "ToArray"
            }
        }
        test_data = [
            {"protocol": "TCP", "sourceport": 1, "destinationport": 2}]
        options = {}
        result = json_to_stix_translator.convert_to_stix(data_source, map_data, test_data,
                                                         transformers.get_all_transformers(), options)[0]

        assert(result is not None)
        assert('objects' in result)
        objects = result['objects']

        assert('0' in objects)
        network_traffic = objects['0']
        assert(network_traffic['src_port'] == 1)
        assert(network_traffic['dst_port'] == 2)
        assert(isinstance(network_traffic['protocols'], list))
        assert(network_traffic['protocols'][0] == 'tcp')
