
import asyncio
from qa.core.broker import MdAdaptor, TdAdaptor
from qa.core.event import EventEngine


class QAZone:
    def __init__(self):
        self._event_engine = EventEngine()
        self._md_adaptor = MdAdaptor(self._event_engine)
        self._td_adaptor = TdAdaptor(self._event_engine)

    def add_strategy(self, strategy):
        self._strategy = strategy
        self._strategy.register_broker(self._md_adaptor, self._td_adaptor)

    def run(self):
        asyncio.run(self.__main__())

    async def __main__(self):

        self._event_engine.register('tick', self._strategy.on_tick)

        tasks = [
            self._event_engine.run,
            self._md_adaptor.run,
            self._td_adaptor.run,
            self.__run_strategies__
        ]
        futures = [asyncio.create_task(coroutine()) for coroutine in tasks]

        await asyncio.gather(*futures)

    async def __run_strategies__(self):
        await asyncio.sleep(0.01)
        await self._md_adaptor.subscribe(self._strategy.symbol)
