Simple demo-quality code for translating JSON objects from a given data model (CAR in this example) to STIX observables.

Execute the following to see a couple of example translations:

`python3 main.py`

The CAR objects are found in `main.py`:

```
  'data_model': {
    'object': 'process',
    'fields': {
      'pid': 804,
      'image_path': 'C:\\test.exe',
      'md5_hash': '0'*32,
      'parent_image_path': 'C:\\Windows\\System32\\cmd.exe'
    }
  }

  'data_model': {
    'object': 'flow',
    'fields': {
      'dest_ip': '172.217.7.228',
      'dest_port': 80,
      'protocol': 'HTTP',
      'content': 'GET https://www.google.com/ HTTP/1.1'
    }
  }
```

The result should look like the following:

```
{'root': {'binary_ref': 'root.binary_ref',
          'parent_ref': 'root.parent_ref',
          'pid': 804,
          'type': 'process'},
 'root.binary_ref': {'hashes': {'MD5': '00000000000000000000000000000000'},
                     'name': 'test.exe',
                     'parent_directory_ref': 'root.binary_ref.parent_directory_ref',
                     'type': 'file'},
 'root.binary_ref.parent_directory_ref': {'path': 'C:\\', 'type': 'directory'},
 'root.parent_ref': {'binary_ref': 'root.parent_ref.binary_ref',
                     'type': 'process'},
 'root.parent_ref.binary_ref': {'name': 'cmd.exe',
                                'parent_directory_ref': 'root.parent_ref.binary_ref.parent_directory_ref',
                                'type': 'file'},
 'root.parent_ref.binary_ref.parent_directory_ref': {'path': 'C:\\Windows\\System32\\',
                                                     'type': 'directory'}}
====================
{'root': {'dst_port': 80,
          'dst_ref': 'root.dst_ref',
          'protocols': ['http'],
          'src_payload_ref': 'root.src_payload_ref',
          'type': 'network-traffic'},
 'root.dst_ref': {'type': 'ipv4-addr', 'value': '172.217.7.228'},
 'root.src_payload_ref': {'payload_bin': 'R0VUIGh0dHBzOi8vd3d3Lmdvb2dsZS5jb20vIEhUVFAvMS4x',
                          'type': 'artifact'}}
```
