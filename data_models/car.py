import re
from data_models.base import ValueTransform, split_path
import base64

def protocol_transform(proto):
  return [proto.lower()]

def payload_transform(ascii_data):
  return base64.b64encode(
    ascii_data.encode('ascii')
  ).decode('ascii')

CAR_OBJECT_MAP = {
  'process' : 'process',
  'flow': 'network-traffic'
}

CAR_FIELD_MAP = {
  'process' : {
    'fields': {
      'pid': ValueTransform(int,
        'pid'
      ),
      'exe': 'binary_ref(file).name',
      'current_directory': 'cwd',
      'command_line': 'command_line',
      'user': 'creator_user_ref(user-account).account_login',
      'image_path': ValueTransform(split_path,
        'binary_ref(file).parent_directory_ref(directory).path',
        'binary_ref(file).name'
      ),
      'md5_hash': 'binary_ref(file).hashes.MD5',
      'sha1_hash': 'binary_ref(file).hashes.SHA1',
      'sha256_hash': 'binary_ref(file).hashes.SHA-256',
      'parent_exe': 'parent_ref(process).binary_ref(file).file_name',
      'ppid': 'parent_ref(process).pid',
      'parent_image_path': 'parent_ref.binary_ref.parent_directory_ref.path',
      'parent_image_path': ValueTransform(split_path,
        'parent_ref(process).binary_ref(file).parent_directory_ref(directory).path',
        'parent_ref(process).binary_ref(file).name'
      ),
      'sid': 'extensions.windows-process-ext.owner_sid'
    }
  },
  'flow': {
    'fields': {
      'start_time': 'start', # TODO: transform may be needed, not sure
      'end_time': 'end', # TODO: transform may be needed, not sure
      'src_ip': 'src_ref(ipv4-addr).value',
      'dest_ip': 'dst_ref(ipv4-addr).value',
      'src_port': ValueTransform(int,
        'src_port'
      ),
      'dest_port': ValueTransform(int,
        'dst_port'
      ),
      'protocol': ValueTransform(protocol_transform,
        'protocols'
      ),
      'content': ValueTransform(payload_transform,
        'src_payload_ref(artifact).payload_bin'
      )
    }
  }
}
