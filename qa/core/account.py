
from qa.core.meta import Order, Trade, Tick


class PortfolioMetrics:
    def __init__(self, init_cash):
        self.init_capital = init_cash

        self.total_return      : float = 0.0
        self.annual_return     : float = 0.0
        self.total_return_pct  : float = 0.0
        self.annual_return_pct : float = 0.0
        self.max_drawdown      : float = 0.0
        self.max_drawdown_pct  : float = 0.0
        self.sharpe_ratio      : float = 0.0
        self.sortino_ratio     : float = 0.0
        self.win_rate          : float = 0.0

    def on_tick(self, tick: Tick):
        """计算浮动收益"""
        pass

    def on_trade(self, order: Order):
        """计算实际盈亏"""
        pass

    def summrize(self):
        print("="*50)
        print("TRADING STRATEGY PERFORMANCE REPORT")
        print("="*50)
        print("-"*30)
        print("="*50)


class QAccount:
    MULTIPLIERS = 100

    def __init__(self, init_capital=20000.0):
        self._available: int = int(init_capital * self.MULTIPLIERS)
        self._withdraw_quota: int = self._available
        self._frozen_cash: int = 0

    @property
    def available(self):
        return self._available / self.MULTIPLIERS
    
    @property
    def withdraw_quota(self):
        return self._withdraw_quota / self.MULTIPLIERS
    
    @property
    def frozen_cash(self):
        return self._frozen_cash / self.MULTIPLIERS
    def on_init(self):
        pass

    def on_rtn_account(self, acc):
        self._available = acc.available
        self._withdraw_quota = acc.withdraw_quota

    def on_rtn_position(self, pos):
        print('get position')

    def on_req_order(self, order: Order):
        amount = int(order.price * self.MULTIPLIERS) * order.volume
        if order.direction == b'buy':
            self._available -= amount
            self._frozen_cash += amount
        elif order.direction == b'sell':
            # self._frozen_cash -= amount
            pass
    
    def on_rtn_order(self, order: Order):
        # amount = order.price * order.volume
        # if order.direction == b'buy':
        #     self._available -= amount
        #     self._frozen_cash += amount
        # elif order.direction == b'sell':
        #     # self._frozen_cash -= amount
        #     pass
        # print('---', self.available, self.frozen_cash)
        pass
    
    def on_rtn_trade(self, trd: Trade):
        amount = int(trd.price * self.MULTIPLIERS) * trd.volume
        if trd.direction == b'buy':
            print(f' ----- buy {trd.symbol} {trd.price}')
            self._frozen_cash -= amount
            # todo: position op
        elif trd.direction == b'sell':
            print(f' ----- sell {trd.symbol} {trd.price}')
            self._available += amount
            # todo: position op