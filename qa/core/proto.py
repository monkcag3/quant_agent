
from ctypes import *


class Tick(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('datetime'   , c_uint64),
        ('symbol'     , c_char*12),
        ('open'       , c_double),
        ('high'       , c_double),
        ('low'        , c_double),
        ('close'      , c_double),
        ('volume'     ,c_uint64),
        ('amount'     , c_double),
        ('ask_price'  , c_double*10),
        ('ask_volume' , c_uint64*10),
        ('bid_price'  , c_double*10),
        ('bid_volume' , c_uint64*10),
    ]

class Bar(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('datetime'   , c_uint64),
        ('symbol'     , c_char*12),
        ('open'       , c_double),
        ('high'       , c_double),
        ('low'        , c_double),
        ('close'      , c_double),
        ('volume'     ,c_uint64),
        ('amount'     , c_double),
    ]

class Order(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('orderid'   , c_char*128),
        ('type'      , c_char*12),  # limit or market
        ('direction' , c_char*12),  # buy or sell
        ('symbol'    , c_char*12),
        ('price'     , c_double),
        ('volume'    , c_int),
        ('traded'    , c_int),
        ('status'    , c_char*24),
        ('datetime'  , c_int64),
    ]

class Account(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('available'     , c_double), # 可用金额
        ('withdraw_quota', c_double), # 可取金额
    ]
