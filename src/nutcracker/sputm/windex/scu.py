from collections.abc import Callable, Iterable, Iterator
from typing import IO

from nutcracker.kernel2.element import Element
from nutcracker.sputm.script.bytecode import script_map


def get_global_scripts(root: Iterable[Element]) -> Iterator[Element]:
    for elem in root:
        if elem.tag in {'LECF', 'LFLF', 'OBCD', *script_map}:
            if elem.tag in {*script_map}:
                yield elem
            else:
                yield from get_global_scripts(elem.children())


def get_room_scripts(root: Iterable[Element]) -> Iterator[Element]:
    for elem in root:
        if elem.tag in {'LECF', 'LFLF', 'RMDA', 'ROOM', 'OBCD', *script_map}:
            if elem.tag == 'SCRP':
                assert 'ROOM' not in elem.attribs['path'], elem
                assert 'RMDA' not in elem.attribs['path'], elem
                continue
            elif elem.tag in {*script_map, 'OBCD'}:
                yield elem
            else:
                yield from get_room_scripts(elem.children())


def dump_script_file(
    room_no: str,
    room: Element,
    decompile: Callable[[Element], Iterator[str]],
    outfile: IO[str],
) -> None:
    children = list(room.children())
    for elem in get_global_scripts(children):
        for line in decompile(elem):
            print(line, file=outfile)
        print('', file=outfile)  # end with new line
    print(f'room {room_no}', '{', file=outfile)
    for elem in get_room_scripts(children):
        print('', file=outfile)  # end with new line
        for line in decompile(elem):
            print(
                line if line.endswith(']:') or not line else f'\t{line}',
                file=outfile,
            )
    print('}', file=outfile)
    print('', file=outfile)  # end with new line
