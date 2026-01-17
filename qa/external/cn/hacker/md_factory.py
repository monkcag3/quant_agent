
import logging
import asyncio
from typing import Dict, List, Any

import qa


logger = logging.getLogger(__name__)


def get_tick_channel(
    pair: qa.Pair,
):
    return f"{str(pair)}@tick"


class MdFactory(qa.Producer, qa.FifoQueueEventSource):
    def __init__(
        self,
        zone: qa.Zone,
        interval: int = 1
    ):
        super().__init__(self)
        self._zone = zone
        self._interval = interval
        self._event_sources: Dict[str, qa.EventSource] = {}
        
        self._quotes: Dict[str, List[qa.TickEventHandler]] = {}

        self._zone.subscribe(self, self.__handle_md__)

    def subscribe(
        self,
        pair: qa.Pair,
        event_handler: qa.TickEventHandler,
    ):
        channel = str(pair.base_symbol)
        if channel not in self._quotes.keys():
            self._quotes[channel] = [event_handler]
        else:
            self._quotes[channel].append(event_handler)

    async def main(self):
        while True:
            try:
                await self.__fetch_and_push__()
            except Exception as e:
                await self.__on_error__(e)
            await asyncio.sleep(self._interval)

    async def __fetch_and_push__(self):
        # todo: fetch data and push
        # 直接调用回调 还是 push后由zone调度？
        pass

    async def __on_error__(
        self,
        error: Any,
    ):
        logger.error(qa.logs.StructureMessage("Error on polling md", error = error))

    async def __handle_md__(
        self,
        event: qa.TickEvent,
    ):
        channel = event.tick.symbol
        handlers = self._quotes.get(channel, [])
        for handler in handlers:
            await handler(event)