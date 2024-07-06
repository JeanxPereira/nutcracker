import functools
import os
from enum import Enum
from pathlib import Path

import typer

from .. import windex_v5, windex_v6
from ..preset import sputm
from ..schema import SCHEMA
from ..script.bytecode import script_map
from ..strings import RAW_ENCODING
from ..tree import narrow_schema, open_game_resource
from .scu import dump_script_file

app = typer.Typer()

SUPPORTED_VERSION = {
    '8': (8, 0),
    '7': (7, 0),
    'he101': (6, 101),
    'he100': (6, 100),
    'he99': (6, 99),
    'he98': (6, 98),
    'he90': (6, 90),
    'he80': (6, 80),
    'he73': (6, 73),
    'he72': (6, 72),
    'he71': (6, 71),
    'he70': (6, 70),
    'he60': (6, 60),
    '6': (6, 0),
    '5': (5, 0),
}

Version = Enum(  # type: ignore[misc]
    'Version',
    dict(zip(SUPPORTED_VERSION.keys(), SUPPORTED_VERSION.keys(), strict=True)),
)


@app.command('decompile')
def decompile(
    filename: Path = typer.Argument(..., help='Game resource index file'),
    gver: Version = typer.Option(
        None,
        '--game',
        '-g',
        help='Force game version',
    ),
    *,
    verbose: bool = typer.Option(False, '--verbose', help='Dump each opcode for debug'),
    chiper_key: str = typer.Option(
        None,
        '--chiper-key',
        help='XOR key for decrypting game resources',
    ),
    skip_transform: bool = typer.Option(
        False,
        '--skip-transform',
        help='Disable structure simplification',
    ),
) -> None:
    gameres = open_game_resource(
        filename,
        SUPPORTED_VERSION.get(gver.name) if gver else None,
        int(chiper_key, 16) if chiper_key else None,
    )
    basename = gameres.basename

    root = gameres.read_resources(
        schema=narrow_schema(
            SCHEMA,
            {'LECF', 'LFLF', 'RMDA', 'ROOM', 'OBCD', *script_map},
        ),
    )

    rnam = gameres.rooms
    print(gameres.game)
    print(rnam)

    script_dir = os.path.join('scripts', basename)
    os.makedirs(script_dir, exist_ok=True)

    if gameres.game.version >= 6:
        decompile = functools.partial(
            windex_v6.decompile_script,
            game=gameres.game,
            verbose=verbose,
            transform=not skip_transform,
        )
    elif gameres.game.version >= 5:
        decompile = functools.partial(
            windex_v5.decompile_script,
            transform=not skip_transform,
        )

    for disk in root:
        for room in sputm.findall('LFLF', disk):
            room_no = rnam.get(room.attribs['gid'], f"room_{room.attribs['gid']}")
            print(
                '==========================',
                room.attribs['path'],
                room_no,
            )
            fname = f"{script_dir}/{room.attribs['gid']:04d}_{room_no}.scu"

            with open(fname, 'w', **RAW_ENCODING) as script_file:
                dump_script_file(room_no, room, decompile, script_file)


if __name__ == '__main__':
    app()
