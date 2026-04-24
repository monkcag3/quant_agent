

import abc
from typing import Any

import qa


class TdSpi:

    @abc.abstractmethod
    async def create_market_order(
        self,
        pair: qa.Pair,
        operation: qa.OrderOperation,
        **kwargs: dict[str, Any],
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    async def create_limit_order(
        self,
        pair: qa.Pair,
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    async def create_stop_limit_order(
        self,
        pair: qa.Pair,
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    async def cancel_order(
        self,
        pair: qa.Pair,
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_account(
        self,
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_positions(
        self,
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    async def get_position(
        self,
        pair: qa.Pair
    ):
        raise NotImplementedError()
