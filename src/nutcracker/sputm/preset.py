from nutcracker.kernel2.chunk import IFFChunkHeader
from nutcracker.kernel2.preset import Preset

from .schema import SCHEMA

sputm = Preset(
    header_dtype=IFFChunkHeader,
    alignment=1,
    inclheader=True,
    skip_byte=0x80,
    schema=SCHEMA,
    errors='ignore',
)
