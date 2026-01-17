
import asyncio

import qa
from qa.gallary import rsi
# from qa.external.sim import csv
# from qa.external.sim.account import QAccount
from qa.external.cn import csv
from qa.external.cn.account import QAccount
from qa.external.cn.sim import SimMd, SimTd

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



async def main():
    zone = qa.QAZone()
    pair = qa.Pair('600000', 'SSE')
    
    strategy = rsi.Strategy(zone, 7, 30, 70)

    # 行情
    # md = csv.TickFactory(zone)
    md = SimMd(zone)
    md.subscribe(pair, strategy.on_tick_event)

    # 交易
    # td = csv.TradeFactory(zone)
    td = SimTd(zone)
    account = QAccount(td_api=td)
    md.subscribe(pair, account.on_tick)
    strategy.subscribe_to_trading_signals(account.on_trading_singal)
    td.subscribe_to_order(pair, account.on_rtn_order)
    td.subscribe_to_trade(pair, account.on_rtn_trade)

    await zone.run()


if __name__ == "__main__":
    asyncio.run(main())