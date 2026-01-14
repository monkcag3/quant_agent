
import dataclasses


@dataclasses.dataclass(frozen=True)
class Pair:
    """A trading pair.

    :param base_symbol: The base symbol. It could be a stock, a crypto currency, a currency, etc.
    :param quote_symbol: The quote symbol. It could be a stock, a crypto currency, a currency, etc.
    """

    #: The base symbol.
    base_symbol: str

    #: The quote symbol.
    quote_symbol: str

    def __str__(self):
        return "{}.{}".format(self.base_symbol, self.quote_symbol)


@dataclasses.dataclass(frozen=True)
class PairInfo:
    """Information about a trading pair.

    :param base_precision: The precision for the base symbol.
    :param quote_precision: The precision for the quote symbol.
    """

    #: The precision for the base symbol.
    base_precision: int

    #: The precision for the quote symbol.
    quote_precision: int
