#!/usr/bin/env python3

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import replace
from typing import Any

from .chunk import Chunk
from .element import Element
from .resource import read_chunks
from .settings import _IndexSetting


class MissingSchemaKey(Exception):
    def __init__(self, tag: str) -> None:
        super().__init__(f'Missing key in schema: {tag}')
        self.tag = tag


class MissingSchemaEntry(Exception):
    def __init__(self, ptag: str, tag: str) -> None:
        super().__init__(f'Missing entry for {tag} in {ptag} schema')
        self.ptag = ptag
        self.tag = tag


@contextmanager
def exception_ptag_context(ptag: str | None) -> Iterator[None]:
    try:
        yield
    except Exception as exc:
        if not hasattr(exc, 'ptag'):
            exc.ptag = ptag  # type: ignore
        raise exc


def check_schema(cfg: _IndexSetting, ptag: str | None, tag: str) -> None:
    try:
        if ptag and tag not in cfg.schema[ptag]:
            raise MissingSchemaEntry(ptag, tag)
        if tag not in cfg.schema:
            raise MissingSchemaKey(tag)
    except (MissingSchemaKey, MissingSchemaEntry) as exc:
        if cfg.strict:
            raise exc
        else:
            cfg.logger.warning(exc)


def create_element(offset: int, chunk: Chunk, **attrs: Any) -> Element:
    return Element(chunk, {'offset': offset, 'size': len(chunk.data), **attrs}, [])


def map_chunks(
    cfg: _IndexSetting,
    data: bytes,
    parent: Element | None = None,
    level: int = 0,
    extra: Callable[[Element | None, Chunk, int], dict[str, Any]] | None = None,
    offset: int = 0,
) -> Iterator[Element]:
    ptag = parent.tag if parent else None
    if cfg.max_depth and level >= cfg.max_depth:
        return
    if parent and not cfg.schema.get(parent.tag):
        return
    data = memoryview(data)
    with exception_ptag_context(ptag):
        for offset, chunk in read_chunks(cfg, data, offset=offset):
            check_schema(cfg, ptag, chunk.tag)

            elem = create_element(
                offset,
                chunk,
                **(extra(parent, chunk, offset) if extra else {}),
            )
            yield elem.content(
                map_chunks(
                    cfg,
                    chunk.slice(chunk.buffer),
                    parent=elem,
                    level=level + 1,
                    extra=extra,
                ),
            )


def generate_schema(cfg: _IndexSetting, data: bytes) -> dict[str, set[str]]:
    EMPTY: frozenset[str] = frozenset()
    DUMMY: frozenset[str] = frozenset(('__DUMMY__',))

    schema: dict[str, frozenset[str]] = {}

    # TODO: check if partial iterations are possible
    while True:
        cfg = replace(cfg, schema=schema, strict=True)
        try:
            # generate schema for 1 level deeper
            for _ in map_chunks(cfg, data, level=-1):
                pass
            return {ptag: set(tags) for ptag, tags in schema.items() if tags != DUMMY}
        except MissingSchemaKey as miss:
            schema[miss.tag] = DUMMY  # creates new copy
        except MissingSchemaEntry as miss:
            schema[miss.ptag] -= DUMMY
            schema[miss.ptag] |= {miss.tag}
        except Exception as exc:
            # pylint: disable=no-member
            assert hasattr(exc, 'ptag')
            if schema.get(exc.ptag) == EMPTY:  # type: ignore
                raise ValueError(
                    'Cannot create schema for given file with given configuration',
                )
            schema[exc.ptag] = EMPTY  # type: ignore
