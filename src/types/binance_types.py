from enum import Enum
from typing import Literal, TypedDict


class BinanceFill(TypedDict):
    price: float
    qty: float
    commission: float
    commissionAsset: str # Enum 'BTC'
    tradeId: int

class BinanceOrder(TypedDict):
    symbol: str
    orderId: int
    orderListId: int
    clientOrderId: str
    transactTime: int
    price: float
    origQty: float
    executedQty: float
    cummulativeQuoteQty: float
    status: str # Enum 'FILLED'
    timeInForce: str # Enum 'GTC'
    type: str # Enum 'MARKET'
    side: str # Enum 'BUY'
    fills: list[BinanceFill]

class BinanceCurrency(Enum):
    BTC = 1
    UDST = 6

BinanceCurrencyLiteral = Literal[1,6]