import pprint
from transform import transform

pprint.PrettyPrinter().pprint(transform({
  'data_model': {
    'object': 'process',
    'fields': {
      'pid': 804,
      'image_path': 'C:\\test.exe',
      'md5_hash': '0'*32,
      'parent_image_path': 'C:\\Windows\\System32\\cmd.exe'
    }
  }
}))

print('='*20)

pprint.PrettyPrinter().pprint(transform({
  'data_model': {
    'object': 'flow',
    'fields': {
      'dest_ip': '172.217.7.228',
      'dest_port': 80,
      'protocol': 'HTTP',
      'content': 'GET https://www.google.com/ HTTP/1.1'
    }
  }
}))
