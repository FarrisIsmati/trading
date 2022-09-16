from typing import TypedDict


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
