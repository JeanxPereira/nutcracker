import io
import os
import sys
from collections.abc import Iterator
from typing import IO

from parse import parse

from .element import Element, ElementTree


def findall(tag: str, root: ElementTree) -> Iterator[Element]:
    if not root:
        return
    for elem in root:
        if parse(tag, elem.tag, evaluate_result=False):
            yield elem


def find(tag: str, root: ElementTree) -> Element | None:
    return next(findall(tag, root), None)


def findpath(path: str, root: Element | None) -> Element | None:
    path = os.path.normpath(path)
    if not path or path == '.':
        return root
    dirname, basename = os.path.split(path)
    return find(basename, findpath(dirname, root))


def render(
    element: Element | None,
    level: int = 0,
    stream: IO[str] = sys.stdout,
) -> None:
    if not element:
        return
    attribs = ''.join(
        f' {key}="{value}"'
        for key, value in element.attribs.items()
        if value is not None
    )
    indent = '    ' * level
    closing = '' if element.children else ' /'
    print(f'{indent}<{element.tag}{attribs}{closing}>', file=stream)
    if element.children:
        for elem in element.children:
            render(elem, level=level + 1, stream=stream)
        print(f'{indent}</{element.tag}>', file=stream)


def renders(element: Element | None) -> str:
    with io.StringIO() as stream:
        render(element, stream=stream)
        return stream.getvalue()
