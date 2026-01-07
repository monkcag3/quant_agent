

class QAccount:
    def __init__(self, init_capital=20000.0):
        self._available = init_capital
        self._withdraw_quota = init_capital
        self._frozen_cash = 0.0

    def on_init(self):
        pass

    def on_rtn_account(self, acc):
        self._available = acc.available
        self._withdraw_quota = acc.withdraw_quota

    def on_rtn_position(self, pos):
        print('get position')
    
    def on_rtn_order(self, order):
        amount = order.price * order.volume
        if order.direction == b'buy':
            self._available -= amount
            self._frozen_cash += amount
        elif order.direction == b'sell':
            # self._frozen_cash -= amount
            pass
    
    def on_rtn_trade(self, trd):
        amount = trd.price * trd.volume
        if trd.direction == b'buy':
            self._frozen_cash -= amount
            # todo: position op
        elif trd.direction == b'sell':
            self._available += amount
            # todo: position op