# -*- coding: utf-8 -*-
import      configparser
import      logging
import      json
import      os 
from        datetime            import datetime
import      ccxt
import      pandas              as      pd

from        app.models.models   import User, Api
from        math                import log10 , floor


class Robot:

    def round_it(x, sig):
        #return round(x, sig-int(floor(log10(abs(x))))-1)
        return round(x, sig)

    def datetime_string_to_datetime(datetime_string):
        datetime_obj = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        return(datetime_obj)

    def datetime_formater(date_time):
        date_time = date_time.strftime("%m/%d/%Y, %H:%M:%S")
        return date_time

    def get_user_by_user_id(username):
        user = User.query.filter_by(username = username).first()
        return user

    def get_api_by_user(user):
        api = Api.query.filter_by(user = user).first()
        return api

    def check_trade_by_order_id(order_id, exchange, _symbol = "BTC-USDT-SWAP", start_time = '2020-08-24T00:00:00Z'):

        print("\n\n=============fetchHistoryTrades=============")
        d = exchange.parse8601(start_time)
        symbol = _symbol
        fetchTrades = exchange.fetchMyTrades(symbol = symbol, since = d, limit = 100, params={'order': 'asc',})
        
        #print(fetchTrades[0]["info"]['ordId'])
        search_order_id = order_id #'479835518780473391'

        traget_trade = next((trade for trade in fetchTrades if trade["info"]['ordId'] == search_order_id), None)
        

        df                  = pd.DataFrame()
        df['DateTime']      = [traget_trade['datetime']]
        df['Order ID']      = [traget_trade['info']['ordId']]
        df['Bill ID']       = [traget_trade['info']['billId']]
        df['Trade ID']      = [traget_trade['info']['tradeId']]
        df['ID']            = [traget_trade['id']]

        df['股票']          = [traget_trade['info']['instId']]
        df['方向']          = [traget_trade['info']['side']]
        df['Fill Size']     = [traget_trade['info']['fillSz']]
        df['Fill Price']    = [traget_trade['info']['fillPx']]
        df['成本']          = [traget_trade['cost']]
        df['fee']           = [str(traget_trade['fee']['cost'])]
        df['fees']          = [str(traget_trade['fees'][0]['cost'])] # 其實呢度可以有好多list
        df['takerOrMaker']  = [traget_trade['takerOrMaker']]
        
        #print(df) # 出返一個表
        #print(f"traget_trade = \n\n {traget_trade}") #所有資料
        #print('Total ' + str(len(fetchTrades)) + ' rows.')
        return df

    # def set_log_format():
    #     LOG_FORMAT          = "%(asctime)s - %(levelname)s - %(message)s"
    #     DATE_FORMAT         = "%Y/%m/%d/ %H:%M:%S %p"
    #     logging.basicConfig(filename='catobot.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    #     return [LOG_FORMAT, DATE_FORMAT]
    #     # 個logging.basic Config係咪自動set左~
    
    def send_order(side, quantity, symbol, order_type, order_time, price, prev_side, tdmode):
        try:
            print(f"正在發送訂單到交易所: 方向    : {side} | 合約數量: {quantity} | 股票: {symbol} | 巿價/限價: {order_type}")
            print(f"正在發送訂單到交易所: 之前方向: {prev_side} | 倉位模式: {tdmode} | 每股價錢: {price} | 時間: {order_time}")
            #之前既方向最好去交易所拎, 
            order = "這個是一個你需要的order什麼什麼的程式"
            print (order)
        except Exception as e:
            print (f"發生錯誤 - {e}")
            return False
        return order





#===============================================================設定是次交易的交易所
    def get_exchange(api):
        exchange = ccxt.okex5(config={
                    'enableRateLimit'       : True,
                    'apiKey'                : api.api_key, 
                    'secret'                : api.api_secret,
                    'password'              : api.api_password, 
                    'verbose'               : False,  # for debug output
                    'enableRateLimit'       : True,
                    })
        return exchange
#===============================================================設定是次交易的交易所

#===============================================================設定是次交易的交易所
    def get_default_exchange():
        exchange = ccxt.okex5()
        return exchange
#===============================================================設定是次交易的交易所



#===============================================================讀取配置文件  現時沒用
    def get_robot_config():
        config = {}
        if os.path.exists('./config.json'):
            config      = json.load(open('./config.json',encoding="UTF-8"))
            
            print  (f"\n成功讀取: config.json")
            print  (config)
            print  ("\n\n")
            return (config)

        elif os.path.exists('./config.ini'):
            conf        = configparser.ConfigParser()
            conf.read("./config.ini", encoding="UTF-8")

            for i in dict(conf._sections):
                config[i] = {}
                for j in dict(conf._sections[i]):
                    config[i][j] = conf.get(i, j)

            config['account']['enable_proxies']   = config['account']['enable_proxies']  .lower() == "true"
            config['trading']['enable_stop_loss'] = config['trading']['enable_stop_loss'].lower() == "true"
            config['trading']['enable_stop_gain'] = config['trading']['enable_stop_gain'].lower() == "true"

            print  (f"\n成功讀取: config.ini")
            print  (config)
            print  ("\n\n")
            return (config)

        else:
            logging.info("配置文件 config.json 不存在，程序即將退出")
            print       ("配置文件 config.json 不存在，程序即將退出")
            return None
            exit()
#===============================================================讀取配置文件   現時沒用

    def get_robot_config_from_database():
        config = {}
        if os.path.exists('./config.json'):
            config      = json.load(open('./config.json',encoding="UTF-8"))
            
            print  (f"\n成功讀取: config.json")
            print  (config)
            print  ("\n\n")
            return (config)

        elif os.path.exists('./config.ini'):
            conf        = configparser.ConfigParser()
            conf.read("./config.ini", encoding="UTF-8")

            for i in dict(conf._sections):
                config[i] = {}
                for j in dict(conf._sections[i]):
                    config[i][j] = conf.get(i, j)

            config['account']['enable_proxies']   = config['account']['enable_proxies']  .lower() == "true"
            config['trading']['enable_stop_loss'] = config['trading']['enable_stop_loss'].lower() == "true"
            config['trading']['enable_stop_gain'] = config['trading']['enable_stop_gain'].lower() == "true"

            print  (f"\n成功讀取: config.ini")
            print  (config)
            print  ("\n\n")
            return (config)

        else:
            logging.info("配置文件 config.json 不存在，程序即將退出")
            print       ("配置文件 config.json 不存在，程序即將退出")
            exit()
#===============================================================讀取配置文件   現時沒用


#===============================================================pretty_print    
    def pretty_print( format, *args):
        print(format.format(*args))
#===============================================================pretty_print 



#===============================================================提取: 所有交易所的 名字 
    def print_all_exchange():
        for exchange in ccxt.exchanges:
            print(exchange)
#===============================================================提取: 所有交易所的 名字 



#===============================================================提取: 指定交易所的 所有 貨幣對 
    def load_markets_in_exchange(my_exchange): # load in your ccxt.binanceus() obj
        markets = my_exchange.load_markets()
        for market in markets:
            print(market)
        return markets
#===============================================================提取: 指定交易所的 所有 貨幣對 


#===============================================================提取 你的交易所的 指定的交易對 的最新資料
    def fetch_ticker(my_exchange, my_ticker):
        format_1 = "        {:<38}:{:<18}"
        ticker = my_exchange.fetch_ticker(my_ticker)
        #print (ticker)
        print(f'\n {my_ticker}: \n')

        for index, value in ticker.items():
            if index != "info":
                Robot.pretty_print(format_1, str(index), str(value) )
                
            
        print('\n\n')
        for index, value in ticker.items():
            if index == "info":
                print('Information:\n')
                for index, value in ticker['info'].items():
                    Robot.pretty_print(format_1, str(index), str(value) )

#===============================================================提取 你的交易所的 指定的交易對 的最新資料


#===============================================================提取 你的交易所的 指定的交易對 的K線的 最新資料
    def get_ohlc(my_exchange, ticker, timeframe, since = None, limit = None):
        print('\n\n')
        #print(f'\n\n\n資料來源: {my_exchange} || 貨幣對: {ticker} || TimeFrame: {timeframe}\n')
        
        format_2 = "      {:<4}  {:<38} {:<4}{:<18} {:<4}{:<18} {:<4}{:<18} {:<4}{:<18} {:<4}{:<18}"
        ohlc = my_exchange.fetch_ohlcv(symbol = ticker, timeframe = timeframe, since = since, limit = limit)
        count = 0 
        for candle in ohlc:
            if count%20 ==0 :
                print(f'\n\n\n資料來源: {my_exchange} || 貨幣對: {ticker} || TimeFrame: {timeframe}\n')
            bar_datetime = datetime.fromtimestamp(candle[0]/1000)
            #print(candle)
            #Robot.pretty_print(format_2, str(datetime.fromtimestamp(int(candle[0]))), candle[1], candle[2], candle[3], candle[4], candle[5])
            output = Robot.pretty_print(format_2, '時間:', str(bar_datetime),  '開巿價:',candle[1], '最高價:',candle[2], '最低價:',candle[3], '收巿價:',candle[4], '收易量:',candle[5])
            #print(type(candle[0]))
            count +=1
        return [ohlc, output]
#===============================================================提取 你的交易所的 指定的交易對 的K線的 最新資料


#===============================================================提取: 你的交易所的 指定的貨幣交易對
    def load_markets_in_exchange_with_selected_crypto(my_exchange, symbol): # load in your ccxt.binanceus() obj
        markets = my_exchange.load_markets()
        for market in markets:
            if symbol in market:
                print(market)
#===============================================================提取: 你的交易所的 指定的貨幣交易對



#===============================================================提取: 你的交易所的 指定的交易對 的OrderBook
    def get_older_book(my_exchange, ticker):
        format_1 = "        {:<38}:{:<18}"
        print('\n\n')
        print(f'\n\n\n資料來源: {my_exchange} || 貨幣對: {ticker} \n')
        
        format_2 = "      {:<4}  {:<38} {:<4}{:<18} {:<4}{:<18} {:<4}{:<18} {:<4}{:<18} {:<4}{:<18}"
        orderbook = my_exchange.fetch_order_book(symbol = ticker)
        count = 0 
        #print(orderbook)

        for index, value in orderbook.items():
            if index != "bids" and index != "asks":
                Robot.pretty_print(format_1, str(index), str(value) )
        
        print('\n\n')
        for index, value in orderbook.items():
            if index == "bids":
                print('Bids:\n')
                for index, value in orderbook['bids']:
                    Robot.pretty_print(format_1, str(index), str(value) )

        # ASKS 未寫
        # for order in orderbook:
        #     if count%20 ==0 :
        #         print(f'\n\n\n資料來源: {my_exchange} || 貨幣對: {ticker}\n')
        #     bar_datetime = datetime.fromtimestamp(order[0]/1000)
        #     Robot.pretty_print(format_2, '時間:', str(bar_datetime),  '開巿價:',order[1], '最高價:',order[2], '最低價:',order[3], '收巿價:',order[4], '收易量:',order[5])
        #     count +=1
#===============================================================提取: 你的交易所的 指定的交易對 的OrderBook


#===============================================================提取: 你的交易所的 Balance
    def get_balance(my_exchange, symbol = 'USDT'):
        #format_1 = "        {:<38}:{:<18}"
        try:
            balance = my_exchange.fetch_balance()
            balance_of_symbol = balance["info"]["data"][0]["details"][0]["eq"]
        #################################################print (balance)

        #幣安
        #print( f'\n你戶口內的{symbol}價值為: {balance["info"]["result"][symbol]["equity"]} \n\n')

        #OKX
            msg = f'\n你戶口內的{symbol}價值為: {balance["info"]["data"][0]["details"][0]["eq"]} \n\n'
            #print(msg )
            return balance_of_symbol
        except:
            print('不能登入')
        # for index, value in balance.items():
        #     if index == "info":
        #         info_dict = ast.literal_eval(str(value))
       

        # for index, value in info_dict.items():
        #     if index == "result":
        #         result_dict = ast.literal_eval(str(value))
        
        # for index, value in result_dict.items():
        #     if index == symbol:
        #         coin_info_dict = ast.literal_eval(str(value))

        #         equity = coin_info_dict.get('equity', value)
        

        #         print(f'\n你戶口內的{symbol}價值為: {equity}\n\n')
#===============================================================提取: 你的交易所的 Balance


# #===============================================================計算: Amount to Contracts 


















#===============================================================計算: Amount to Contracts 

#===============================================================交易: 買入
    def long_coin (my_exchange, buy_coin, how_many):
        order = my_exchange.create_market_buy_order(buy_coin, how_many)
        print('\n')
        print (order)
        print('\n')
 #===============================================================交易: 買入


 #===============================================================交易: 賣出       
    def short_coin (my_exchange, buy_coin, how_many):
        order = my_exchange.create_market_sell_order(buy_coin, how_many)
        print('\n')
        print (order)
        print('\n')
 #===============================================================交易: 賣出 






        

#============== 提取你的交易所的交易對 ==============
#my_exchange = ccxt.bybit()
#my_exchange = ccxt.binanceus()
#my_exchange = ccxt.okex()
# Robot.load_markets_in_exchange(my_exchange)

#============== 提取你的交易所的交易對 完結 =========

#============== 提取你的交易所的指定的交易對 的最新資料 ==============
#my_exchange = ccxt.bybit()
#my_ticker = "BTC/USDT:USDT"
#Robot.fetch_ticker(my_exchange, my_ticker)

#============== 提取你的交易所的指定的交易對 的最新資料 完結 =========


#============== 提取你的交易所的指定的交易對的K線的最新資料 ==============
#my_exchange = ccxt.binanceus()
#my_ticker = "BTC/USDT"
#timeframe = '1h'
#Robot.get_ohlc(my_exchange, my_ticker, timeframe)

#============== 提取你的交易所的指定的交易對的K線的最新資料 完結 =========




#============== 提取你的交易所的指定的貨幣交易對 ==============
#my_exchange = ccxt.binanceus()

#selected_symbol = "BTC"
#Robot.load_markets_in_exchange_with_selected_crypto(my_exchange, selected_symbol)

#============== 提取你的交易所的指定的貨幣交易對 完結 =========




#============== 提取你的交易所的指定的交易對的OrderBook ==============
#my_exchange = ccxt.coinbasepro()
#my_ticker = "BTC/USDT"
#Robot.get_older_book(my_exchange, my_ticker)

#============== 提取你的交易所的指定的交易對的OrderBook 完結 =========




#============== 提取你的交易所的Balance ==============
#my_exchange = ccxt.bybit({
#    'apiKey' : config.BYBIT_API_KEY,
#    'secret' : config.BYBIT_SECRET_KEY,
#    'timeout': 30000,
#    'enableRateLimit': True,
#
#})
#coin_symbol = "USDT"
#Robot.get_balance(my_exchange, coin_symbol)


# my_exchange     = ccxt.okex5({
#                 'apiKey' : current_user.APIs[1].api_key,
#                 'secret' : current_user.APIs[1].api_secret,
#                 'password': current_user.APIs[0].api_password,
#                 'timeout': 30000,
#         'enableRateLimit': True,}) # 沒有參數都可以
# coin_symbol = "USDT"

# coin_symbol = "USDT"
# Robot.get_balance(my_exchange, coin_symbol)

#============== 提取你的交易所的Balance 完結 =========

#============== 做多開單 ==============
# my_exchange = ccxt.bybit({
#     'apiKey' : config.BYBIT_API_KEY,
#     'secret' : config.BYBIT_SECRET_KEY,
#     'timeout': 30000,
#     'enableRateLimit': True,

# })
#buy_coin = "BTC/USDT:USDT"
#how_many = 0.001
#Robot.long_coin(my_exchange, buy_coin, how_many)

#============= 做多開單 完結 =========



#============== 做空開單 ==============
# my_exchange = ccxt.bybit({
#     'apiKey' : config.BYBIT_API_KEY,
#     'secret' : config.BYBIT_SECRET_KEY,
#     'timeout': 30000,
#     'enableRateLimit': True,

# })
#buy_coin = "BTC/USDT:USDT"
#how_many = 0.001
#Robot.short_coin(my_exchange, buy_coin, how_many)

#============= 做空開單 完結 =========


#============== 做空開單 ==============
# my_exchange = ccxt.bybit({
#     'apiKey' : config.BYBIT_API_KEY,
#     'secret' : config.BYBIT_SECRET_KEY,
#     'timeout': 30000,
#     'enableRateLimit': True,

# })
#buy_coin = "BTC/USDT:USDT"
#how_many = 0.001
#Robot.short_coin(my_exchange, buy_coin, how_many)

#============= 做空開單 完結 =========




