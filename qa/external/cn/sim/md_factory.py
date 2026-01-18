
from typing import Dict

import qa
# from .. import csv
from qa.external.common import csv


def get_tick_channel(
    pair: qa.Pair,
):
    return f"{str(pair)}@tick"


class MdFactory:
    def __init__(
        self,
        zone: qa.Zone,
    ):
        self._zone = zone
        self._event_sources: Dict[str, qa.EventSource] = {}

    def subscribe(
        self,
        pair: qa.Pair,
        event_handler: qa.TickEventHandler,
    ):
        event_source = self._event_sources.get(get_tick_channel(pair))
        if not event_source:
            event_source = csv.TickSource(pair, f'{pair.base_symbol}.u.csv')
        self._zone.subscribe(event_source, event_handler)