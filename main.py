
import asyncio
from qa.core.zone import QAZone
# from qa.gallary.ma_strategy import MAStrategy
from qa.core.pair import Pair
import qa.external.sim.exchange as sim_exchange
from qa.external.sim import csv
from qa.external.sim.account import QAccount
from qa.core.meta import tick
from qa.gallary import rsi


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def on_tick_event(tick_event: tick.TickEvent):
    print('--------------', tick_event.tick)
    pass

async def main():
    zone = QAZone()
    pair = Pair('600000', 'SSE')
    acc = QAccount()

    exchange = sim_exchange.Exchange(zone)
    exchange.add_md_source(csv.TickSource(pair, "600000.u.csv"))

    strategy = rsi.Strategy(zone, 7, 30, 70)
    exchange.subscribe_to_tick_event(pair, strategy.on_tick_event)
    ## 订阅交易信号
    strategy.subscribe_to_trading_signals(acc.on_trading_singal)
    ## 订阅order/trade信号（交易所返回消息）
    exchange.subscribe_to_tick_event(pair, acc.on_tick)
    exchange.subscribe_to_order(acc.on_rtn_order)
    exchange.subscribe_to_trade(acc.on_rtn_trade)

    await zone.run()


if __name__ == "__main__":
    asyncio.run(main())