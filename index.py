# モジュールのインポート
import MetaTrader5 as mt5
import pandas as pd

def main():
    # 銘柄
    SYMBOL = 'USDJPY'
    
    # MT5と接続
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return
    
    # 接続できたらMT5のバージョンを表示
    print(f"MetaTrader5 package version {mt5.__version__}")
    
    # MT5でブローカーにログイン
    authorized = mt5.login(
        12345678,
        password="password",
        server="Demo",
    )
    if not authorized:
        print(f"User Authorization Failed")
        return
    
    # 口座情報を取得する
    account_info = mt5.account_info()
    if account_info is None:
        print(f"Retreiving account information failed")
        return
    print(f"Balance: {account_info.balance}")
    
    # シンボルの情報の取得
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print("Symbol not found")
        return
    
    # 時系列データの取得
    df_rates = get_rates(SYMBOL, frame=mt5.TIMEFRAME_H1, count=100)
    last_close_price = df_rates['Close'][-1]
    print(f"Close: {last_close_price}")
    
    # 注文を出す
    point = symbol_info.point
    result = post_market_order(
        SYMBOL,
        type=mt5.ORDER_TYPE_BUY,
        vol=0.1,
        price=mt5.symbol_info_tick(SYMBOL).ask,
        dev=20, 
        sl=mt5.symbol_info_tick(SYMBOL).ask - point * 100,
        tp=mt5.symbol_info_tick(SYMBOL).ask + point * 100,
    )
    
    ticket =result.order
    # ポジションの確認
    position = mt5.positions_get(ticket=ticket)
    if position is None:
        print('ポジションが存在しない')
        return
    pos = position[0]
    print(f"Open: {pos.price_open}")
    print(f"Current: {pos.price_current}")
    print(f"Swap: {pos.swap}")
    print(f"Profit: {pos.profit}")
    
    # 決済する
    ticket = result.order
    result = post_market_order(
        SYMBOL, 
        type=mt5.ORDER_TYPE_SELL, 
        vol=0.1, 
        price=mt5.symbol_info_tick(SYMBOL).bid, 
        dev=20, 
        position=ticket,
    )
    
    code = result.retcode
    if code == 10009:
        print('注文完了')
    elif code == 10013:
        print('無効なリクエスト')
    elif code == 10018:
        print('マーケットが休止中')