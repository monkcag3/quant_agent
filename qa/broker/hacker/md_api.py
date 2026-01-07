
from qa.broker.md_api import MdApi


class HackerMdApi(MdApi):
    TYPE = 'md'
    NAME = 'hacker'

    async def run(self):
        print(f"run [{self.TYPE}.{self.NAME}]")