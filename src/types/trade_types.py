from enum import Enum
from typing import Literal


class TradePairSymbols(Enum):
    BTCUSDT = 'BTCUSDT'

class Positions(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

TradePairSymbolsLiteral = Literal['BTCUSDT']
PositionsLiteral = Literal['BUY', 'SELL']