import io
import itertools

# import numpy as np
from nutcracker.codex import base, bomp


def encode1(bmap):
    return bomp.encode_image(bmap)


PARAMS = [
    # SAMNMAX/ROOMS-BOMP, COMI/ROOMS-BOMP, FT/ROOMS-BOMP, DIG/ROOMS-BOMP  # FT/ICONS2.NUT
    (3, False, 1, None),
    # FT/ROOMS-BOMP(*)
    (3, False, 0, None),
    # FT/ICONS.NUT, FT/BENCUT.NUT, FT/BENSGOGG.NUT
    (4, True, 1, None),
    # MORTIMER/F_GATE_H.NUT
    (3, False, 0, b'\x00'),
]


def decode1(width, height, f, verify=False):
    # BG = 39

    # print(mat)
    mat = bomp.decode_image(f, width, height)

    if verify:
        with io.BytesIO(f) as stream:
            lines = [base.unwrap_uint16le(stream) for _ in range(height)]
        print([list(bomp.iter_decode(line)) for line in lines])

        print()

        g = [[list(group) for c, group in itertools.groupby(line)] for line in mat]

        encs = []

        for limit, carry, end_limit, seps in PARAMS:
            encs.append(
                bomp.encode_image(
                    mat,
                    limit=limit,
                    carry=carry,
                    end_limit=end_limit,
                    seps=seps,
                ),
            )
            print(
                list(
                    list(
                        bomp.encode_groups(
                            l,
                            limit=limit,
                            carry=carry,
                            end_limit=end_limit,
                            seps=seps,
                        ),
                    )
                    for l in g
                ),
            )

        assert any(x == f[: len(x)] for x in encs), (encs, f)

    # mat = np.where(mat==0, BG, mat)
    return mat
