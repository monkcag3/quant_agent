
from ctypes import *
import struct
from datetime import datetime
from typing import List
from dataclasses import dataclass, field


@dataclass
class BaseData:
    """
    Any data object needs a gateway_name as source
    and should inherit base data.
    """

    gateway_name: str = ""

    extra: dict | None = field(default=None, init=False)



# class Order(LittleEndianStructure):
#     _pack_ = 1
#     _fields_ = [
#         ('orderid', c_char*128),
#         ('type', c_char*12),        # limit,market
#         ('direction', c_char*12),   # buy,sell
#         ('price', c_double),
#         ('volume', c_int),
#         ('traded', c_int),
#         ('status', c_char*24),
#         ('datetime', c_int64)
#     ]




class Account(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('available'     , c_double), # 可用金额
        ('withdraw_quota', c_double), # 可取金额
    ]