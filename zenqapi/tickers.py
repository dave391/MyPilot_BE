class Ticker:
    def __init__(self, ticker_id, ticker_name=""):
        self.ticker_id = ticker_id
        self.ticker_name = ticker_name


AAVEUSDT = Ticker(33853, 'AAVEUSDT')
ADAUSDC = Ticker(35176, 'ADAUSDC')
ADAUSDT = Ticker(33049, 'ADAUSDT')
ALGOUSDC = Ticker(40886, 'ALGOUSDC')
ATOMUSDC = Ticker(35130, 'ATOMUSDC')
BCHUSDC = Ticker(35167, 'BCHUSDC')
BCHUSDT = Ticker(33419, 'BCHUSDT')
BNBUSDC = Ticker(35162, 'BNBUSDC')
BNBUSDT = Ticker(32770, 'BNBUSDT')
BTCUSDC = Ticker(35182, 'BTCUSDC')
BTCUSDT = Ticker(32777, 'BTCUSDT')
DOGEUSDC = Ticker(35151, 'DOGEUSDC')
DOGEUSDT = Ticker(33316, 'DOGEUSDT')
DOTUSDC = Ticker(35139, 'DOTUSDC')
DOTUSDT = Ticker(33715, 'DOTUSDT')
INJUSDC = Ticker(35181, 'INJUSDC')
ETHUSDC = Ticker(35160, 'ETHUSDC')
ETHUSDT = Ticker(32811, 'ETHUSDT')
FTMUSDC = Ticker(35158, 'FTMUSDC')
FTMUSDT = Ticker(33289, 'FTMUSDT')
LINKUSDC = Ticker(35168, 'LINKUSDC')
LINKUSDT = Ticker(33185, 'LINKUSDT')
LTCUSDC = Ticker(35126, 'LTCUSDC')
LTCUSDT = Ticker(32845, 'LTCUSDT')
MANAUSDT = Ticker(33662, 'MANAUSDT')
MATICUSDC = Ticker(40939, 'MATICUSDC')
MATICUSDT = Ticker(33257, 'MATICUSDT')
ONTUSDC = Ticker(40914, 'ONTUSDC')
SANDUSDT = Ticker(33702, 'SANDUSDT')
SHIBUSDT = Ticker(34180, 'SHIBUSDT')
SOLUSDC = Ticker(35149, 'SOLUSDC')
SOLUSDT = Ticker(33537, 'SOLUSDT')
TRXUSDT = Ticker(33101, 'TRXUSDT')
USDCUSDT = Ticker(33176, 'USDCUSDT')
WLDUSDC = Ticker(35156, 'WLDUSDC')
XRPUSDC = Ticker(35140, 'XRPUSDC')

dct_all_ticker_info = {
    obj.ticker_id: obj
    for name, obj in globals().items()
    if isinstance(obj, Ticker)
}

dct_all_ticker_info.update({
    obj.ticker_name: obj
    for name, obj in globals().items()
    if isinstance(obj, Ticker)
})

