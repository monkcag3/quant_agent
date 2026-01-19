
import abc

from qa.core.meta import Trade


class Metric(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def calculate(
        self,
        buy_trade: Trade,
        sell_trade: Trade,
    ):
        raise NotImplementedError()