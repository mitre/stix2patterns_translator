from .base import DataMapper

# TODO: should this really be a class? Could be a module, made it a class
# in case we have configuration arguments at some point
class CimDataMapper(DataMapper):
    data_model_name = "CIM"
    type_name = "cim_type"

    MAPPINGS = {
      "artifact": None,
      "as": None, # Maybe network traffic
      "directory": {
        "cim_type": "endpoint",
        "fields": {
          "path": "file_path",
          "created": "file_create_time",
          "modified": "file_modify_time",
          "action": {
            "action": {
              "create": "created",
              "delete": "delete",
              "modify-metadata": "acl_modified", # acl is just one type of metadata. could also be "updated" or "modified"?
              "read": "read",
              "write": "modified" # Not sure if this should be "updated" or "modified"
            }
          }
        }
      },
      "domain-name": { # Network Traffic
        "cim_type": "flow",
        "fields": {
          "value": "dest_fqdn"
        }
      },
      "email-addr": {
        "cim_type": "email",
        "fields": {
          "value": "src_user" # this probably should be both src_user and recipient
        }
      },
      "email-message": {
        "cim_type": "email",
        "fields": {
          "body_multipart.[*].'mime-part-type'.body_raw_ref.hashes.MD5": "file_hash",
          "body_multipart.[*].'mime-part-type'.body_raw_ref.hashes.SHA-1": "file_hash",
          "body_multipart.[*].'mime-part-type'.body_raw_ref.hashes.SHA-256": "file_hash",
          "body_multipart.[*].'mime-part-type'.body_raw_ref.name": "file_name",
          "body_multipart.[*].'mime-part-type'.body_raw_ref.size": "file_size",
          "to_refs.[*].value": "recipient",
          "cc_refs.[*].value": "recipient",
          "bcc_refs.[*].value": "recipient",
          "subject": "subject",
          "sender_ref.value": "src_user",
          "from_ref.value": "src_user"
        }
      },
      "file": { # Really need to add like a bonus filter here for `object_category`
        "cim_type": "endpoint", # Don't ask...it's all part of the "change" data model
        "fields": {
          "hashes.MD5": "file_hash", # really all hashes should look in hash -- CIM isn't specific as to what hash type it is
          "hashes.SHA-1": "file_hash",
          "hashes.SHA-256": "file_hash",
          "name": "file_name",
          "created": "file_create_time",
          "modified": "file_modify_time",
          "parent_directory_ref.path": "file_path",
          "size": "file_size",
          "action": {
            "action": {
              "create": "created",
              "delete": "delete",
              "modify-metadata": "acl_modified", # acl is just one type of metadata. could also be "updated" or "modified"?
              "read": "read",
              "write": "modified" # Not sure if this should be "updated" or "modified"
            }
          }
        }
      },
      "ipv4-addr": { # Network traffic
        "cim_type": "flow",
        "fields": {
          "value": "dest_ip"
        }
      },
      "ipv6-addr": None,
      "mac-addr": { # Network traffic
        "cim_type": "flow",
        "fields": {
          "value": "mac"
        }
      },
      "mutex": None,
      "network-traffic": { # Probably need to figure out when to use web here, but not now
        "cim_type": "network",
        "fields": {
          "src_ref.value": "src", # This field is aliased to IP, MAC, domain
          "src_port": "src_port",
          "dst_ref.value": "src",
          "dst_port": "dest_port",
          "protocols[*]": "protocol",
        }
      },
      "process": {
        "cim_type": "process",
        "fields": {
          "name": "process",
          "pid": "pid", # don't see this in CIM documentation
          "creator_user_ref.account_login": "user",
          "action": { # don't see this in CIM documentation
            "action": {

            }
          }
        }
      },
      "software": None, # This could probably be "inventory". Maybe "malware" also?
      "url": {
        "cim_type": "web",
        "fields": {
          "value": "url",
        }
      },
      "user-account": { # This is where the static objects in STIX breakdown. Could either do this as a login (authentication) or create (change)
        "cim_type": "authentication",
        "fields": {
          "account_login": "user",
          "action": {
            "action": {

            }
          }
        }
      },
      "windows-registry-key": {
        "cim_type": "endpoint", # as with file, this is part of the change model
        "fields": {
          "key": "object",
          "values[*]": "result",
          "creator_user_ref.account_login": "user",
          "action": {
            "action": {
              "create": "created",
              "modify": "modified", # not sure if this should be "updated" or "modified"
              "delete": "deleted"
            }
          }
        }
      },
      "x509-certificate": { # This mapping isn't really complete, STIX splits up the actual public key, for example, into its components (for some reason)
        "cim_type": "certificate",
        "hashes.SHA-256": "ssl_hash",
        "hashes.SHA-1": "ssl_hash",
        "version": "ssl_version",
        "serial_number": "ssl_serial",
        "signature_algorithm": "ssl_signature_algorithm",
        "issuer": "ssl_issuer",
        "subject": "ssl_subject",
        "subject_public_key_algorithm": "ssl_publickey_algorithm"
      }
    }
