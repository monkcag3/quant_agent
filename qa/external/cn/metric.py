
import abc


class Metric(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def calculate(self):
        raise NotImplementedError()
    


class WinRateMetric(Metric):
    
    async def calculate(self):
        pass


class TotalReturnMetric(Metric):

    async def calculate(self):
        pass


class SharpeRatioMetric(Metric):

    async def calculate(self):
        pass


class MaxDropDownMetric(Metric):

    async def calculate(self):
        pass


class AlphaMetric(Metric):

    async def calculate(self):
        pass