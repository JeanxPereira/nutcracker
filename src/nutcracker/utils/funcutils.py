from collections.abc import Iterable, Iterator, Sequence
from itertools import chain, zip_longest
from typing import TypeVar

T = TypeVar('T')


def flatten(ls: Iterable[Iterable[T]]) -> Iterator[T]:
    # flatten(['ABC', 'DEF']) --> A B C D E F
    """Flatten one level of nesting."""
    return chain.from_iterable(ls)


def grouper(
    iterable: Iterable[T],
    n: int,
    fillvalue: T | None = None,
) -> Iterator[Sequence[T]]:
    """Collect data into fixed-length chunks or blocks."""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
