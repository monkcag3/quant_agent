
from ctypes import *


class Tick(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("datetime", c_uint64),
        ("symbol",   c_char*12),
        ("open",     c_double),
        ("high",     c_double),
        ("low",      c_double),
        ("close",    c_double),
        ("volume",   c_uint64),
        ("amount",   c_double)
    ]


class Bar(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("datetime", c_uint64),
        ("symbol",   c_ubyte*12),
        ("open",     c_double),
        ("high",     c_double),
        ("low",      c_double),
        ("close",    c_double),
        ("volume",   c_uint64),
        ("amount",   c_double)
    ]