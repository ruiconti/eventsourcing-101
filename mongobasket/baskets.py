# flake8: NOQA
# pylint: disable=unused-import
import uuid
from collections import Counter
from typing import List, NamedTuple, Optional

from pymongo import MongoClient

from mongobasket.aggregate import Aggregate, applies
from mongobasket.events import Event, BasketCreated, ItemAdded, ItemRemoved

from .util import print_basket

client = MongoClient()
db = client.basket_db


class Basket(Aggregate):
    def __init__(self, events: Optional[List] = None):
        self.id = uuid.uuid4()
        # the line below overrides the need to use @applies decorator
        # because it's simples to understand
        # TODO: debug and explain EventRegistry
        self._handlers = {
            BasketCreated: Basket.on_created,
            ItemAdded: Basket.on_added,
            ItemRemoved: Basket.on_remove,
        }
        super().__init__(events)

    # Deciders: raise events (send commands)
    @classmethod
    def create(cls, basket_id: uuid.UUID) -> Basket:
        """Factory basket 'static' method"""
        basket = Basket()
        basket.raise_event(BasketCreated(basket_id))
        return basket

    def add_item(self, product: str, qty: int = 1) -> None:
        self.raise_event(ItemAdded(self.id, product, qty))

    def remove(self, product: str) -> None:
        if product not in self.items:
            raise KeyError
        self.raise_event(ItemRemoved(self.id, product))

    # Appliers aka handlers
    # @applies(events.BasketCreated)
    def on_created(self, event: BasketCreated) -> None:
        self.id = event.basket_id
        self.items: Counter = Counter()

    def on_added(self, event: ItemAdded) -> None:
        self.items[event.product] += event.qty

    def on_remove(self, event: ItemRemoved) -> None:
        del self.items[event.product]

    # View methods

    def get_item(self, product: str) -> int:
        return self.items[product]

    def is_empty(self) -> bool:
        return not any(self.items)

    def __str__(self) -> str:
        return print_basket(self)

    # Data Access
