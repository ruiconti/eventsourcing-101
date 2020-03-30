from mongobasket.baskets import Basket


def print_basket(basket: Basket) -> str:

    item_list = "\n".join(
        (f"\t* {product}: {qty}" for product, qty in basket.items.items())
    )  # noqa: E501
    event_list = "\n".join((f"\t* {e}" for e in basket.events))

    return (
        f"Basket {basket.id}:\n\n"
        f"{len(basket.events)} Events:\n\n"
        f"{event_list}\n\n"
        "Items:\n"
        f"{item_list}\n"
    )
