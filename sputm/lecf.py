#!/usr/bin/env python3
import io
import os
import struct

from functools import partial

if __name__ == '__main__':
    import argparse

    from . import sputm

    parser = argparse.ArgumentParser(description='read smush file')
    parser.add_argument('filename', help='filename to read from')
    args = parser.parse_args()

    with open(args.filename, 'rb') as res:
        lecf = sputm.assert_tag('LECF', sputm.untag(res))
        assert res.read() == b''
        # chunks = (assert_tag('LFLF', chunk) for chunk in read_chunks(tlkb))
        chunks = sputm.read_chunks(lecf)
        for idx, (tag, chunk) in enumerate(chunks):
            if not tag == 'LFLF':
                continue
            print([tag for tag, _ in sputm.read_chunks(chunk)])
            for cidx, (tag, data) in enumerate(sputm.read_chunks(chunk)):
                if tag == 'SCRP':
                    os.makedirs(os.path.dirname('SCRIPTS'), exist_ok=True)
                    with open(os.path.join('SCRIPTS', f'SCRP_{cidx:04d}_{idx:04d}'), 'wb') as out:
                        out.write(sputm.mktag('SCRP', data))
                    continue
                if tag == 'DIGI':
                    os.makedirs(os.path.dirname('DIGIS'), exist_ok=True)
                    with open(os.path.join('DIGIS', f'DIGI_{cidx:04d}_{idx:04d}'), 'wb') as out:
                        out.write(sputm.mktag('DIGI', data))
                if tag == 'TLKE':
                    print(data)
                    exit(1)
                if tag == 'CHAR':
                    os.makedirs(os.path.dirname('CHARS'), exist_ok=True)
                    with open(os.path.join('CHARS', f'CHAR_{cidx:04d}_{idx:04d}'), 'wb') as out:
                        out.write(sputm.mktag('CHAR', data))
                if tag == 'RMDA':
                    os.makedirs(os.path.dirname('ROOMS'), exist_ok=True)
                    with open(os.path.join('ROOMS', f'ROOM_{cidx:04d}_{idx:04d}'), 'wb') as out:
                        out.write(sputm.mktag('ROOM', data))
            # save raw
            print('==========')