
from qa.broker.td_api import TdApi


class HackerTdApi(TdApi):
    TYPE = 'td'
    NAME = 'hacker'

    async def run(self):
        print(f"run [{self.TYPE}.{self.NAME}]")