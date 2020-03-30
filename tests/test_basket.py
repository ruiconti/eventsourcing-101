# pylint: disable=attribute-defined-outside-init
import uuid
from typing import Type, Union

from mongobasket.baskets import Basket
from mongobasket import events


class BasketTest:
    BASKET_ID = uuid.uuid4()
    basket = Basket()

    @property
    def event(self) -> events.Event:
        assert len(self.basket.new_events) == 1, "Should have one new event"
        return self.basket.new_events[0]

    def has_event(self, cls: Type) -> bool:
        return isinstance(self.event, cls)

    def raised_no_events(self) -> bool:
        return not any(self.basket.new_events)

    @staticmethod
    def create_basket() -> Basket:
        return Basket.create(BasketTest.BASKET_ID)


class Test_WhenCreatingNewBasket(BasketTest):
    basket = BasketTest.create_basket()

    def test_it_should_not_contain_any_products(self) -> None:
        assert self.basket.is_empty()

    def test_it_should_raise_basket_created(self) -> None:
        assert self.has_event(events.BasketCreated)
        assert self.event.basket_id == self.BASKET_ID

    def test_it_should_have_the_correct_basket_id(self) -> None:
        assert self.basket.id == self.BASKET_ID


class Test_WhenAddingANewItem(BasketTest):
    def given_an_empty_basket(self) -> None:
        self.basket = Basket([events.BasketCreated(BasketTest.BASKET_ID)])

    def add_coffe_to_basket(self) -> None:
        self.basket.add_item("coffee", qty=3)

    def test_it_should_contain_the_product(self) -> None:
        self.given_an_empty_basket()
        self.add_coffe_to_basket()
        assert self.basket.get_item("coffee") == 3, "Should contain 3 coffees"

    def test_it_should_raise_item_added(self) -> None:
        self.given_an_empty_basket()
        self.add_coffe_to_basket()
        assert isinstance(self.event, events.ItemAdded)
        assert self.event.basket_id == self.BASKET_ID
        assert self.event.product == "coffee"
        assert self.event.qty == 3

    def test_it_should_not_be_empty(self) -> None:
        self.given_an_empty_basket()
        self.add_coffe_to_basket()
        assert not self.basket.is_empty()


class Test_WhenRemovingAProduct(BasketTest):
    def given_a_basket(self) -> None:
        self.basket = Basket(
            [
                events.BasketCreated(self.BASKET_ID),
                events.ItemAdded(BasketTest.BASKET_ID, "apple", 2),
            ]
        )

    def because_we_remove_an_item(self) -> None:
        self.basket.remove("apple")

    def test_it_should_empty_the_items(self) -> None:
        self.given_a_basket()
        self.because_we_remove_an_item()
        assert self.basket.is_empty()

    def test_it_should_raise_item_removed(self) -> None:
        self.given_a_basket()
        self.because_we_remove_an_item()
        assert self.has_event(events.ItemRemoved)
        assert self.event.basket_id == self.BASKET_ID
        assert self.event.product == "apple"  # type: ignore


class Test_WhenRemovingAProductThatDoesNotExists(BasketTest):
    def given_a_basket(self) -> None:
        self.exn: Union[Exception, None] = None
        self.basket = Basket(
            [
                events.BasketCreated(self.BASKET_ID),
                events.ItemAdded(BasketTest.BASKET_ID, "apple", 1),
            ]
        )

    def because_we_remove_an_unknown_item(self) -> None:
        try:
            self.basket.remove("sausages")
        except Exception as e:
            self.exn = e

    def test_it_should_not_empty_the_items(self) -> None:
        self.given_a_basket()
        self.because_we_remove_an_unknown_item()
        assert not self.basket.is_empty()

    def test_it_should_raise_a_key_error(self) -> None:
        self.given_a_basket()
        self.because_we_remove_an_unknown_item()
        assert isinstance(self.exn, KeyError)

    def test_it_should_not_raise_any_events(self) -> None:
        self.given_a_basket()
        self.because_we_remove_an_unknown_item()
        assert self.raised_no_events()
