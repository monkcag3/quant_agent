
from .tick import Tick, TickEvent, TickEventHandler
from .bar import Bar, BarEvent
from .order import Order, OrderType, OrderStatus, Direction, OrderEvent, OrderEventHandler
from .trade import Trade, TradeEvent, TradeEventHandler



import abc
from typing import Dict, Type


class Register(abc.ABCMeta, type):
    registry: Dict[str, Type] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace)
        if not namespace.get('__abstrace__', False) and name != 'Meta':
            strategy_name = namespace.get('display_name')
            desc = namespace.get("description", "")
            params = namespace.get("params")
            mcs.registry[strategy_name] = {
                "class": cls,
                "params": params,
                "desc": desc
            }
        return cls
    

class Meta(metaclass=Register):
    __abstract__ = True