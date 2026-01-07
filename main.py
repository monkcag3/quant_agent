
import asyncio
from qa.core.zone import QAZone
from qa.gallary.ma_strategy import MAStrategy


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


if __name__ == "__main__":
    strategy = MAStrategy()

    fin = QAZone()
    fin.add_strategy(strategy)
    fin.invoke()



