

from decimal import Decimal
from typing import Any, Dict, Optional
import abc

from qa import Pair, OrderOperation


class ExchangeOrder(metaclass=abc.ABCMeta):
    def __init__(
        self,
        operation: OrderOperation,
        pair: Pair,
        price: Optional[Decimal] = None,
        volume: Optional[Decimal] = None,
        client_order_id: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ):
        self._operation = operation
        self._pair = pair
        self._price = price
        self._volume = volume
        self._client_order_id = client_order_id
        self._kwargs = kwargs

    @abc.abstractmethod
    async def create_order(self, td_api) -> dict:
        raise NotImplementedError()
    

class MarketOrder(ExchangeOrder):
    def __init__(
        self,
        operation: OrderOperation,
        pair: Pair,
        price: Optional[Decimal] = None,
        volume: Optional[Decimal] = None,
        client_order_id: Optional[str] = None,
        **kwargs: Dict[str, Any]
    ):
        super().__init__(operation, pair, price, volume, client_order_id, **kwargs)

    async def create(self, td_api) -> dict:
        # todo: send request
        # return await td_api.create_order()
        return {}
    

class LimitOrder(ExchangeOrder):
    def __init__(
        self,
        operation: OrderOperation,
        pair: Pair,
        limit_price: Decimal,
        client_order_id: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ):
        super().__init__(operation, pair, client_order_id=client_order_id, **kwargs)
        self._limit_price = limit_price

    async def create(self, td_api) -> dict:
        ## todo: send request
        # return await td_api.create_order()
        return {}
    

class StopLimitOrder(ExchangeOrder):
    def __init__(
        self,
        operation: OrderOperation,
        pair: Pair,
        stop_price: Decimal,
        limit_price: Decimal,
        client_order_id: Optional[str],
        **kwargs: Dict[str, Any]
    ):
        super().__init__(operation, pair, client_order_id=client_order_id, **kwargs)
        self._stop_price = stop_price
        self._limit_price = limit_price

    async def create(self, td_api) -> dict:
        ## todo: send request
        # return await td_api.create_order()
        return {}

class CancelOrder(ExchangeOrder):
    def __init__(
        self,
        operation: OrderOperation,
        pair: Pair,
        client_order_id: str,
        **kwargs: Dict[str, Any],
    ):
        super().__init__(operation, pair, client_order_id=client_order_id, **kwargs)

    async def create(self, td_api) -> dict:
        ## todo: send request
        # return await td_api.create_order()
        return {}