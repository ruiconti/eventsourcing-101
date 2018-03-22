import uuid
from typing import NamedTuple


class BasketCreated(NamedTuple):
    basket_id: uuid.UUID


def to_json(event):
    """
    All we do here is convert our named tuple to a
    dict for easy serialisation.
    Once we have a dict, we add the __name__ of the
    event type so we can use it later for deserialisation.
    """
    data = event._asdict()
    data['__event_name'] = event.__class__.__name__
    return data


def from_json(event):
    """
    Here we need to remove the __name__ that we added before
    as well as the unique _id generated by mongo.
    We use the __name__ to find an event class and then
    construct it with the remaining values.
    """
    name = event.pop('__event_name')
    del event['_id']
    cls_ = globals()[name]
    return cls_(**event)


