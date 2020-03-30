import uuid
import logging

from typing import Callable, List, Optional, Type
from mongobasket.events import Event


def applies(event: Event) -> Callable:
    """
    This decorator just adds a new field to the func object
    `_handles` which describes the event type handled by
    the func
    """

    def wrapper(func: Type) -> Type:
        func._applies = event

        return func

    return wrapper


class EventRegistry(type):
    """
    Extends the `type` metaclass to add an event registry to
    classes.

    When initialising a new class, we iterate the members of
    the class looking for a _handles property and add them
    to a dict so we can do event dispatch later.
    """

    def __new__(mcs, name, bases, namespace, **_):  # type: ignore
        result = type.__new__(mcs, name, bases, dict(namespace))  # type: ignore  # noqa: E501
        result._handlers = {  # type: ignore
            value._applies: value
            for value in namespace.values()
            if hasattr(value, "_applies")  # noqa: E501
        }
        # Extend handlers with the values from the inheritance chain

        for base in bases:
            if base._handlers:
                for handler in base._handlers:
                    result._handlers[handler] = base._handlers[handler]  # type: ignore # noqa: E501

        return result


class Aggregate(metaclass=EventRegistry):
    """
    Base class for event sourced aggregates
    """

    @classmethod
    def get_stream(cls, id: uuid.UUID) -> str:
        return cls.__name__.lower() + "-" + str(id)

    def __init__(self, events: Optional[List] = None):
        self.events: List = events or []
        self.new_events: List = []
        self.replay()

    def replay(self) -> None:
        for e in self.events:
            self.apply(e)

    def apply(self, e: Event) -> None:
        handler = self._handlers.get(type(e))  # type: ignore

        if handler:
            handler(self, e)
        else:
            logging.warning(f"no handler found for event {e}")

    def raise_event(self, e: Event) -> None:
        self.events.append(e)
        self.new_events.append(e)
        self.apply(e)
