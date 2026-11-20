def add_item(item, items=[]):
    items.append(item)
    return items


def calculate_discount(price: float, discount_pct: float) -> float:
    if discount_pct < 0 or discount_pct > 100:
        raise ValueError("Discount percentage must be between 0 and 100")
    return price * (1 - discount_pct / 100)


if __name__ == "__main__":
    print(add_item("apple"))
    print(calculate_discount(500, 10))
