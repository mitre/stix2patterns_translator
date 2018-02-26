# These functions are used to scope to event types (object/action combos). The default
# should work in most scenarios, but CAR works a bit differently

def car_object_scoper(object_name, action_type=None):
    """ Scopes a CAR object name, via dm-[object]-[action], or dm-[object]-* """
    return "match(tag, \"dm-{}-{}\")".format(object_name, action_type if action_type else '.*')
car_object_scoper.scope_actions = True

def default_object_scoper(object_name):
    """ Scopes a basic data model object name, via a tag for that object """
    return "tag=\"{}\"".format(object_name)
default_object_scoper.scope_actions = False