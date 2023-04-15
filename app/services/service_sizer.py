from xml.etree.ElementInclude import default_loader
import ccxt
import logging

""" 具體來說，Sizer() 類主要實現以下功能：

獲取交易所的貨幣列表、交易對列表和每個交易對的最小交易量、最小交易額等基本信息。
計算每個交易對的交易手續費和最小交易額，並將其存儲在對應的變量中。
設置每個交易對的買賣價差和止損止盈等相關參數，這些參數通常是根據用戶的交易策略和風險承受能力進行設置的。 """


default_exchange = ccxt.okex5()

class Log:
    @staticmethod
    def log_init(filename):
        # ======================================================================一開始要做既野
        # 格式化日誌
        LOG_FORMAT          = "%(asctime)s - %(levelname)s - %(message)s"
        DATE_FORMAT         = "%Y/%m/%d/ %H:%M:%S %p"

        logging.basicConfig(filename=filename, level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
        logging.FileHandler(filename=filename, encoding="UTF-8")
        # ======================================================================一開始要做既野


class Sizer:
    #Log.log_init('mini_function_test2.log')
    def __init__(self, my_exchange = default_exchange):
        self.my_exchange = my_exchange

    # ======================================================================獲取公共數據，包含合約面值等訊息
    def initInstruments(self):
        c = 0
        try:
            # 獲取永續合約基礎訊息
            swapInstrumentsRes = self.my_exchange.publicGetPublicInstruments(params={"instType": "SWAP"})
            if swapInstrumentsRes['code'] == '0':
                global swapInstruments
                swapInstruments = swapInstrumentsRes['data']
                c = c + 1
        except Exception as e:
            logging.error("提取SWAP共用資料失敗: " + str(e))
        try:
            # 獲取交割合約基礎訊息
            futureInstrumentsRes = self.my_exchange.publicGetPublicInstruments(params={"instType": "FUTURES"})
            if futureInstrumentsRes['code'] == '0':
                global futureInstruments
                futureInstruments = futureInstrumentsRes['data']
                c = c + 1
        except Exception as e:
            logging.error("提取Futures共用資料失敗: " + str(e))
        
        if c >= 2:
            #print(swapInstruments[0]['instId'])
            #print("\n")
            #for item in swapInstruments:
            #    print(item['instId'])
            #print("\n")
            #for item in futureInstruments:
            #    print(item['instId'])
            #print("\n")
            return [swapInstruments, futureInstruments]
        else:
            return None

        # 得到 futureInstruments 與 swapInstruments
    # ======================================================================獲取公共數據，包含合約面值等訊息


    # ======================================================================獲取合約面值
    def getFaceValue(self, _symbol):
        swapInstruments, futureInstruments = self.initInstruments()
        isSwap          = _symbol.endswith("SWAP")
        _symbolSplit    = _symbol.split("-")

        instruments = swapInstruments if isSwap else futureInstruments
        for i in instruments:
            if i['instId'].upper() == _symbol:
                # if _symbolSplit[1] == "USDT":
                #     print(f"\n\n每張{_symbol} U本位合約的面值 : {float(i['ctVal'])} 個 {_symbolSplit[0]} 幣...")

                # if _symbolSplit[1] == "USD":
                #     print(f"\n\n每張{_symbol} 幣本位合約的面值 : {float(i['ctVal'])}  {_symbolSplit[1]} ...")

                return float(i['ctVal'])
        return False
    # ======================================================================獲取合約面值

    # ======================================================================獲取合約面值
    def getFaceValue2(self, _symbol, instruments):
        swapInstruments, futureInstruments = instruments
        isSwap          = _symbol.endswith("SWAP")
        _symbolSplit    = _symbol.split("-")

        instruments = swapInstruments if isSwap else futureInstruments
        for i in instruments:
            if i['instId'].upper() == _symbol:
                return float(i['ctVal'])
        return False
    # ======================================================================獲取合約面值

    # ======================================================================將 amount 幣數轉換為合約張數
    # 幣的數量與張數之間的轉換公式
    # 單位是保證金幣種（幣本位的幣數單位為幣，U本位的幣數單位為U）
    # 交割合約和永續合約合約乘數都是1

    

    def amountConvertToSZ(self, _symbol, coin_number, pay_usdt_price, _ordType):
        _symbol         = _symbol.upper()
        _symbolSplit    = _symbol.split("-")
        isSwap          = _symbol.endswith("SWAP")
        
        
        #================================================拎呢隻幣既面值, 姐係每一張合約係幾多個幣
        #print(_symbolSplit)
        faceValue       = self.getFaceValue(_symbol)
        #print(faceValue)
        if faceValue is False:
            raise Exception("提取不到面值資料...")
        #================================================拎呢隻幣既面值, 姐係每一張合約係幾多個幣


        #================================================拎佢宜家既 MARKET PRICE
        market_price = self.my_exchange.publicGetPublicMarkPrice(params={"instId": _symbol,"instType":("SWAP" if isSwap else "FUTURES")})['data'][0]['markPx']
        #================================================拎佢宜家既 MARKET PRICE

        if _ordType.upper() == "MARKET": 
            if _symbolSplit[1] == "USDT": # U本位合約： 合約張數 = USDT / 面值 (0.01 BTC) / 合約乘數 (1) / 標記價格 (20000)
                contract_usdt_cal = float(pay_usdt_price) / float(market_price) / faceValue # 用USDT去計幾多錢
                
                contract_coin_cal = float(coin_number) / faceValue # 用幣數去計幾多錢 (其實如果係TradeingView出既signal呢兩個數會差唔到, 或者一樣)
                trade_type = "swap"
                money_will_pay  = float(coin_number) * float(market_price)

                #self.check_print(contract_usdt_cal, pay_usdt_price, _symbolSplit, market_price, faceValue, contract_coin_cal, money_will_pay, trade_type, coin_number)

                return [int(contract_usdt_cal), int(contract_coin_cal)]
            
            #==============================================================================

            elif _symbolSplit[1] == "USD":   # 幣本位合約：合約張數 = BTC / 面值 (100USD) / 合約乘數 (1) * 標記價格 (20000
                contract_usdt_cal  = float(pay_usdt_price)  / faceValue # 用BTC去計幾多錢

                contract_coin_cal  = float(coin_number) * float(market_price) / faceValue
                trade_type = "futures"
                money_will_pay  = float(coin_number) * float(market_price)

                #self.check_print(contract_usdt_cal, pay_usdt_price, _symbolSplit, market_price, faceValue, contract_coin_cal, money_will_pay, trade_type, coin_number)
                  
                return [int(contract_usdt_cal), int(contract_coin_cal)]

            else:
                print ("轉換失敗: 幣的數量與合約張數... 請檢查貨幣對格式。")
                return None


    def check_print(self, contract_usdt_cal, pay_usdt_price, _symbolSplit, market_price, faceValue, contract_coin_cal, money_will_pay, trade_type, coin_number):
        print(f"下單合約量為: {int(contract_usdt_cal)}")

        print("\n")
        print("#===========================以USDT去計算合約量")
        print("以想買多少個USDT去計算")
        print(f"我想買 {pay_usdt_price} 美元 等值的 {_symbolSplit[0]} 幣")
        print(f"現時每個 {_symbolSplit[0]} 幣 價錢為: {market_price} 美金")
        print("\n")

        if trade_type == "swap":
            print(f"每張合約為 {faceValue} 個 {_symbolSplit[0]} 幣")
        if trade_type == "futures":
            print(f"每張合約為 {faceValue} 美金")
        
        print(f"下單合約量為: {int(contract_usdt_cal)}")
        if trade_type == "swap":
            print(f"這個交易需要 : {int(contract_usdt_cal) * float(market_price) * faceValue} 美金")

        if trade_type == "futures":
            print(f"這個交易需要 : {int(contract_usdt_cal) * faceValue} 美金")
            
        print("#===========================以USDT去計算合約量")
        print("\n")

        print("\n")
        print("#===========================以幣去計算合約量")
        print("以想買多少個幣去計算")

        print(f"我想買 {coin_number} 個 {_symbolSplit[0]} 幣")
        

        print(f"現時每個 {_symbolSplit[0]} 幣 價錢為: {market_price} 美金")
        print(f"這個交易需要 : {money_will_pay} 美金")
        print("\n")

        if trade_type == "swap":
            print(f"每張合約為 {faceValue} 個 {_symbolSplit[0]} 幣")
        if trade_type == "futures":
            print(f"每張合約為 {faceValue} 美金")
        print(f"下單合約量為: {int(contract_coin_cal)} \n---> 註: 如果在 Tradingview 發出的訊號的話, 這兩個合約量計算出來應該是差不多, 或一樣的。")
        print("#===========================以幣去計算合約量")
        print("\n")

        
    # ======================================================================將 amount 幣數轉換為合約張數




#==========================================以上是程式的本體


#==========================================以下是輸入和使用程式計算 合約數量 
# (U本位合約,  使用USDT/幣計算合約量)
# (幣本位合約, 使用USDT/幣計算合約量)
# (一共4個cases)
#coin = "BTC"
#symbol = coin + "-USDT-SWAP"

#public_data         = Sizer()
#coin_per_contact    = public_data.getFaceValue(symbol)
#print(f'每張contract的面試為 {coin_per_contact} 個{coin}幣')

#market_or_limit     = "market"

# 用USDT 計合約數量
#symbol_usdt_base        = "DOGE-USDT-SWAP" #<------------------------------------------------------------主要係改呢個
#usdt_for_this_trade     = 20000 #<-----------------------------------------------------------------------我想用咁多錢買
#payment_type_usdt       = "USDT"
#payment_type_coin       = "Coins"

# 用幣 計合約數量
#coin_number             = 10 #<--------------------------------------------------------------------------我需要買咁多個幣
#symbol_coin_base        = "DOGE-USD-SWAP"  #<------------------------------------------------------------同埋改呢個


#size_for_usdt_base1  = public_data.amountConvertToSZ(symbol_usdt_base, coin_number, usdt_for_this_trade, market_or_limit)
#size_for_usdt_base2  = public_data.amountConvertToSZ(symbol_coin_base, coin_number, usdt_for_this_trade, market_or_limit)


#print(f'U本位的下單量為: 以 {usdt_for_this_trade} 可以買 {size_for_usdt_base1[0]} 張合約')
#print(f'U本位的下單量為: 以 {coin_number} 個幣計算的話 需要買 {size_for_usdt_base1[1]} 張合約')
#print(f'幣本位的下單量為: 以 {usdt_for_this_trade} 可以買 {size_for_usdt_base2[0]} 張合約')
#print(f'幣本位的下單量為: 以 {coin_number} 個幣計算的話 需要買 {size_for_usdt_base2[1]} 張合約')

#==============================================================================使用格式
#sizer                   = Sizer()
#symbol_usdt_base        = "DOGE-USDT-SWAP"      #   ticker
#usdt_for_this_trade     = 20000                 #   USDT based order amount
#coin_number             = 6000                  #   Coin based order amount
##contract_size           = public_data.amountConvertToSZ(symbol_usdt_base, coin_number, usdt_for_this_trade, market_or_limit)
#print (contract_size)          
#==============================================================================使用格式