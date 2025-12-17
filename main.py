
import asyncio
from quant.FinZone import FinZone
from quant.galaxy.MAStrategy import MAStrategy


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


if __name__ == "__main__":
    strategy = MAStrategy()

    fin = FinZone()
    fin.add_strategy(strategy)
    fin.invoke()



