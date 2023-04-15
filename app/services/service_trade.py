from dateutil                       import parser
from regex import E
from varname                        import nameof

from app                            import db
from app.models.models              import User, Post, Api, Trade, Reply, Signal

from app.services.service_robot_1   import *
from app.services.service_sizer     import *
from app.services.service_ticker    import Ticker

import time
import asyncio
import ccxt.async_support as ccxt
 
from pprint import pprint
import logging
from app.services.service_utilities import CommonFunctions as cf

class InvalidJSONError(Exception):
    pass



class Signal:
    def __init__(self, recieved_msg):

        self.user                = ""
        self.my_exchange         = ""

        self.recieved_msg        = recieved_msg

        self.strategy            = recieved_msg.get("策略")
        self.side                = recieved_msg.get("交易動作")
        self.account_name        = recieved_msg.get("帳戶")
        self.remarks             = recieved_msg.get("注解")
        self.order_amount        = recieved_msg.get("每注")
        self.order_contact_size  = recieved_msg.get("交易合約量")
        self.leverage            = recieved_msg.get("倍數")
        self.interval            = recieved_msg.get("週期")
        self.robot_type          = recieved_msg.get("機器人")
        self.exchange            = recieved_msg.get("交易所")
        self.symbol              = recieved_msg.get("股票")
        self.time1               = recieved_msg.get("時間1")
        self.time2               = recieved_msg.get("時間2")
        self.price_now           = recieved_msg.get("當前下單幣數")#幣的數量
        self.close               = recieved_msg.get("收盤價")
        self.strategy_order_price= recieved_msg.get("交易入場/出場價")
        self.order_status_now    = recieved_msg.get("當前倉位狀態")
        self.prev_order_status   = recieved_msg.get("之前倉位狀態")
        self.prev_order_coin_num = recieved_msg.get("上次下單的幣數")
        self.catobot_password    = recieved_msg.get("CatoBot密碼")#<------------------
        self.trade_mode          = recieved_msg.get('倉位模式')
        self.order_unit          = recieved_msg.get("計價方式")#要加入去
        self.my_robot_id         = recieved_msg.get("你的機器人ID")
        self.order_type          = recieved_msg.get("巿價/限價")#要加入去

        self.use_perc_tp         = recieved_msg.get("是否自定義固定止盈")
        self.use_perc_sl         = recieved_msg.get("是否自定義固定止損")
        self.tp_perc             = recieved_msg.get("自定義止盈百份比")
        self.sl_perc             = recieved_msg.get("自定義止損百份比")

        if self.symbol and self.exchange:
            self.symbol          = Ticker.convert_ticker_to_OKX_format(recieved_msg.get("股票"), self.exchange)
        
        if self.time1:
            self.time1           = parser.parse(recieved_msg.get("時間1"))

        if self.time2:
            self.time2           = parser.parse(recieved_msg.get("時間2"))

        self.signal_check        = False

        if any(value is None for value in self.__dict__.values()):
            var_name = next(key for key, value in self.__dict__.items() if value is None)
            logging.error("Signal: JSON中存在空值: {}".format(var_name))
            self.signal_check = False
        else:
            self.signal_check = True

    def check_signal(self):
        return self.signal_check
       


class TradeService:

    def __init__(self, recieved_msg):

        self.user                = ""
        self.my_exchange         = ""

        self.recieved_msg        = recieved_msg

        self.strategy            = recieved_msg.get("策略")
        self.side                = recieved_msg.get("交易動作")
        self.account_name        = recieved_msg.get("帳戶")
        self.remarks             = recieved_msg.get("注解")
        self.order_amount        = recieved_msg.get("每注")
        self.order_contact_size  = recieved_msg.get("交易合約量")
        self.leverage            = recieved_msg.get("倍數")
        self.interval            = recieved_msg.get("週期")
        self.robot_type          = recieved_msg.get("機器人")
        self.exchange            = recieved_msg.get("交易所")
        self.symbol              = Ticker.convert_ticker_to_OKX_format(recieved_msg.get("股票"), self.exchange)
        self.time1               = parser.parse(recieved_msg.get("時間1"))
        self.time2               = parser.parse(recieved_msg.get("時間2"))
        self.price_now           = recieved_msg.get("當前下單幣數")#幣的數量
        self.close               = recieved_msg.get("收盤價")
        self.strategy_order_price= recieved_msg.get("交易入場/出場價")
        self.order_status_now    = recieved_msg.get("當前倉位狀態")
        self.prev_order_status   = recieved_msg.get("之前倉位狀態")
        self.prev_order_coin_num = recieved_msg.get("上次下單的幣數")
        self.catobot_password    = recieved_msg.get("CatoBot密碼")#<------------------
        self.trade_mode          = recieved_msg.get('倉位模式')
        self.order_unit          = recieved_msg.get("計價方式")#要加入去
        self.my_robot_id         = recieved_msg.get("你的機器人ID")
        self.order_type          = recieved_msg.get("巿價/限價")#要加入去

        self.use_perc_tp         = recieved_msg.get("是否自定義固定止盈")
        self.use_perc_sl         = recieved_msg.get("是否自定義固定止損")
        self.tp_perc             = recieved_msg.get("自定義止盈百份比")
        self.sl_perc             = recieved_msg.get("自定義止損百份比")

        self.password_match = False

        

        # 检查是否存在任何空值，如果存在则抛出异常
        try: 
            if any(value is None for value in self.__dict__.values()):
                var_name = next(key for key, value in self.__dict__.items() if value is None)
                logging.error("Signal: JSON中存在空值: {}".format(var_name))
                raise ValueError("Signal: JSON中存在空值: {}".format(var_name))
        except ValueError as e:
            logging.error("Signal: JSON检查失败")
            cf.print_traceback()
        
        try:   
            self.api                    = Api.query.filter_by(robot_id          = self.my_robot_id)     .first()
            if not self.api:
                self.password_match = None
                print(f"API Robot ID 或密碼 錯誤...")
                return

        except Exception as e:
            print(f"API Robot ID 或密碼 錯誤: {e}")
            self.api = None
            return

        self.password_match = str(self.catobot_password) == str(self.api.signal_passpharse)

        if not self.password_match:
            print(f"API Robot ID 或密碼 錯誤...")
            return

        if self.api and self.password_match:
            self.user            = self.api.user
            self.my_exchange     = Robot.get_exchange(self.api)
        else:
            self.user            = None
            self.my_exchange     = None
            print(f"API 錯誤...")
            return
            


        self.order_id            = 0
        self.last_order_id       = 0
        self.last_algo_order_id  = 0


        self.order_contract_num  = 0



        self.tdMode              = "cross" if self.trade_mode != "逐倉" else "isolated"
        self.amount              = int(self.price_now) # 呢個amount要再check check
        self.prev_side           = self.prev_order_status
        self.order_time          = self.time1
        self.price               = self.close
        self.order_price         = self.strategy_order_price


        if self.order_type:
            if self.order_type   == "巿價":
                self.order_type   = "market"
            elif self.order_type == "限價":
                self.order_type   = "limit"
            else:
                self.order_type   = "market"
        else:
            self.order_type       = "market"

    def print_signal(self):
        print("\n================ 接收到買賣訊號, 訊號內容如下:=================\n")
        print(f"策略名字: {self.strategy}\n")
        print(f"Ticker: {self.symbol}\n")
        print(self.recieved_msg)
        print("\n================ 接收到買賣訊號, 訊號內容如上:=================\n")
    
    def save_signal_to_DB(self):
        print("\n================ 接收到買賣訊號, 訊號發正在記錄在 DATABASE:=================\n")
        rec_signal             = Signal(strategy = self.strategy, side = self.side, symbol = self.symbol, account_name = self.account_name, remarks = self.remarks,
                                    order_amount = self.order_amount, order_contact_size = self.order_contact_size, leverage = self.leverage, interval = self.interval,
                                    robot_type = self.robot_type, exchange = self.exchange, time1 = self.time1, time2 = self.time2, price_now = self.price_now, close = self.close, 
                                    strategy_order_price = self.strategy_order_price, order_status_now = self.order_status_now, prev_order_status = self.prev_order_status,
                                    prev_order_coin_num = self.prev_order_coin_num, catobot_password = self.catobot_password, my_robot_id = self.my_robot_id, trade_mode = self.trade_mode)

        user = User.query.filter_by(id = self.my_robot_id).first()
        user.signals.append(rec_signal)
        # db.session.add(api)
        db.session.commit()




    # =============================================================================================================如果係U本位, 就拎個合約下單數
    def get_contract_number(self):
        isSwap          = self.symbol.endswith("SWAP")
        if isSwap:
            if self.order_unit.upper() == "USDT":
                get_value_response = Sizer.amountConvertToSZ(_symbol = self.symbol, _amount = self.amount, 
                _price = self.order_price, _ordType = self.order_type, exchange = self.my_exchange, close = self.close, lever= self.leverage)
                print(get_value_response) # 這個是OKX的下單合約數
                return get_value_response
        else:
            print("不是U本位") # 如果唔係
            return None
            # ==========================================再計一次合約下單數?
            # ==========================================再計一次合約下單數?
    # =============================================================================================================如果係U本位, 就拎個合約下單數
    
    # =============================================================================================================check 下D 輸出係乜
    def pre_order_data_check(self):
        get_value_response = self.get_contract_number()
        if get_value_response:
            print("\n以下是發出的ORDER的資料: \n")
            Robot.send_order(side = self.side, quantity = get_value_response, symbol=self.symbol, 
            order_type = self.order_type, prev_side = self.prev_side, order_time = self.order_time, tdmode = self.tdMode, price = self.price)
        else:
            print("提取不到 合約面值")
            logging.error("提取不到 合約面值")
    # =============================================================================================================check 下D 輸出係乜

    ##prev side係咪要check?
    def chech_previous_side_of_this_symbol(self):
        check_symbol = self.symbol
        pass


# ======================================================================TP SL 掛單
    def sltp_thread(self): # 一定要落單個時做埋, 唔係既話會無左個contract size 同 order ID
        print("\n================ 接收到買賣訊號, 正在提交止盈止損訂單:=================\n")
        print(f"===> | {self.last_order_id} | {self.symbol} | {self.order_type} | {self.tp_perc} | {self.sl_perc} | <===\n")

        privatePostTradeOrderAlgoParams = {
            "instId": self.symbol,
            "tdMode": self.tdMode,
            "side": "sell" if self.side.lower() == "buy" else "buy", #?
            "ordType": "oco",
            "sz": self.order_contract_num
        }

        while True:
            try:
                privateGetTradeOrderRes = self.my_exchange.privateGetTradeOrder(params={"ordId": self.last_order_id,"instId": self.symbol})
                #print(privateGetTradeOrderRes)

                if privateGetTradeOrderRes['data'][0]['state'] == "filled":
                    avgPx           = float(privateGetTradeOrderRes['data'][0]['avgPx']) # 去交易所拎個平均價
                    direction       = -1 if self.side.lower() == "buy" else 1 #點解人係-1

                    slTriggerPx     = (1 + (direction * float(self.sl_perc) * 0.01))    * avgPx
                    #slOrdPx         = (1 - (direction * float(self.sl_perc) * 0.01))    * avgPx

                    tpTriggerPx     = (1 - (direction * float(self.tp_perc) * 0.01))    * avgPx
                    #tpOrdPx         = (1 + (direction * float(self.tp_perc) * 0.01))    * avgPx

                    if self.use_perc_sl == "是":
                        privatePostTradeOrderAlgoParams['slTriggerPx']      = '%.12f' % slTriggerPx
                        privatePostTradeOrderAlgoParams['slOrdPx']          = -1  # -1 就是巿價

                    if self.use_perc_tp == "是":
                        privatePostTradeOrderAlgoParams['tpTriggerPx']      = '%.12f' % tpTriggerPx
                        privatePostTradeOrderAlgoParams['tpOrdPx']          = -1 # -1 就是巿價

                    if self.use_perc_sl == "是" or  self.use_perc_tp == "是":
                        print("訂單{oid}設置止盈止損...".format(oid=self.last_order_id))
                        privatePostTradeOrderAlgoRes = self.my_exchange.privatePostTradeOrderAlgo(params=privatePostTradeOrderAlgoParams)
                    else:
                        break

                    if privatePostTradeOrderAlgoRes:
                        if 'code' in privatePostTradeOrderAlgoRes and privatePostTradeOrderAlgoRes['code'] == '0':
                            self.last_algo_order_id = privatePostTradeOrderAlgoRes['data'][0]['algoId']
                            break
                        else:
                            continue
                   
                elif privateGetTradeOrderRes['data'][0]['state'] == "canceled":
                    #lastOrdType = None
                    break

            except Exception as e:
                print(e)
            time.sleep(1)

        print("訂單{oid}止盈止損單掛單结束".format(oid=self.last_order_id))
# ======================================================================TP SL 掛單

    # 如果止盈止损
    #if config['trading']['enable_stop_loss'] or config['trading']['enable_stop_gain']: # 呢個我都仲未有~ 但我諗係响signal個度搞?
    #    try:
    #        _thread.start_new_thread(Robot.sltpThread, (lastOrdId, _side, _symbol, _amount, _tdMode, exchange, config))
    #    except:
    #        logging.error("Error: unable to run sltpThread")
    #return True, "create order successfully"




    # =============================================================================================================試下落單先
    def create_order(self):

        print("\n================ 接收到買賣訊號, 正在下單:=================\n")
        print(f"===> | {self.exchange} | {self.symbol} | {self.amount} | {self.price} | {self.side} | <===\n")
        print(f"===> | {self.order_type} | {self.tdMode} | {self.strategy} | {datetime.now()} | <===\n")

        self.set_lever()
        usdt_for_this_trade         = float(self.amount) * float(self.price)

        public_data                 = Sizer()
        self.order_contract_num     = public_data.amountConvertToSZ(self.symbol, float(self.amount), usdt_for_this_trade, self.order_type)
        self.order_contract_num     = self.order_contract_num[1]
        
        #print(f"create order final contract number: {self.order_contract_num}[1]") # 以self.amount 幣的數量計算, 如果是以usdt計算最好是用[0]

        try:
            # 落單
            res = self.my_exchange.privatePostTradeOrder(
                # symbol 買D乜
                # amount 買幾多個幣       =======================>(要改返做合約數)
                # sz响樓上係幾多張合約, 所以有D亂
                # size 方向 sell buy
                # orderType MARKET 定 LIMIT
                # tdMode: isolated or cross

                params={"instId": self.symbol, "sz": self.order_contract_num, "px": self.price, "side": self.side, "ordType": self.order_type,
                        "tdMode": self.tdMode})

            order_id       = res['data'][0]['ordId']

            if order_id:
                print(f"完成下單, 下單號為: {order_id}")
                self.this_trade_data_df = Robot.check_trade_by_order_id(order_id = order_id, exchange = self.my_exchange, _symbol = self.symbol)
                print(self.this_trade_data_df)
                logging.info(f"完成下單, 下單號為: {order_id}")
                self.order_id       = order_id
                self.last_order_id  = order_id
                self.sltp_thread()
                self.get_order_info(order_id)
                return order_id

        except Exception as e:
            print(f"下單發生錯誤, 錯誤訊息為: {e}")
            logging.error(f"下單發生錯誤, 錯誤訊息為: {e}")
    # =============================================================================================================試下落單先

    # =============================================================================================================設定倍數
    def set_lever(self):
        print("\n================ 接收到買賣訊號, 正在設定槓桿倍數:=================\n")
        try:
            privatePostAccountSetLeverageRes = self.my_exchange.privatePostAccountSetLeverage(
                params={"instId": self.symbol, "mgnMode": self.tdMode, "lever": self.leverage})
            #logging.info(json.dumps(privatePostAccountSetLeverageRes))
            #print(f"setLever Print : {json.dumps(privatePostAccountSetLeverageRes)}")
            res = privatePostAccountSetLeverageRes["data"][0]["lever"]
            print (f"設定槓桿倍數完成, 新的槓桿倍數為: {res}")
            return True
        except Exception as e:
            print("Set Leverage Error:  " + str(e))
            logging.error("privatePostAccountSetLeverage " + str(e))
            return False
    # ======================================================================設定 Leverage

    # ======================================================================上一個訂單取消 
    def cancel_last_order(self):
        print(self.symbol, self.last_order_id)
        try:
            res = self.my_exchange.privatePostTradeCancelOrder(params={"instId": self.symbol, "ordId": self.last_order_id})
            # logging.info("privatePostTradeCancelBatchOrders " + json.dumps(res))
            print(f"privatePostTradeCancelBatchOrders + {json.dumps(res)}")
            return True
        except Exception as e:
            # logging.error("privatePostTradeCancelBatchOrders " + str(e))
            print("privatePostTradeCancelBatchOrders " + str(e))
            return False
    # ======================================================================上一個訂單取消

    # ======================================================================全部訂單以巿價平倉 
    def close_all_position(self, symbol, tdMode):
        if symbol:
            print(f"\n================ 接收到自定義訊號, 關閉所有{symbol}倉位:=================\n")
        else:
            print(f"\n================ 接收到買賣訊號, 關閉所有{self.symbol}倉位:=================\n")

        if not symbol or not tdMode:
            if not symbol:
                symbol = self.symbol
            if not tdMode:
                tdMode = self.tdMode
            print(f"關閉訂單指示: 關閉所有訊號中設定的貨幣對倉位: 貨幣對為 {symbol}, 倉位類別為 {tdMode} 。")
        else:
            print(f"關閉訂單指示: 關閉自定義的貨幣對倉位: 貨幣對為 {symbol}, 倉位類別為 {tdMode} 。")
        try:
            res = self.my_exchange.privatePostTradeClosePosition(
                params={"instId": symbol, "mgnMode": tdMode})

            print(f"關閉所有{symbol}倉位 成功: {res}")
            logging.info(f"privatePostTradeClosePosition 關閉所有訂單{symbol}完成: {json.dumps(res)}")
            return True

        except Exception as e:
            print(f"關閉所有{symbol}倉位 錯誤: {str(e)}")
            logging.error(f"privatePostTradeClosePosition 關閉所有{symbol}倉位 錯誤: {str(e)}")
            return False
# ======================================================================全部訂單以巿價平倉

    def ready(self):
        return (self.password_match and self.api and self.user and self.my_exchange) 

    def confirm_signal(self):
        print (self.__dict__)

# ======================================================================ASYNC FUNCTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    async def fetch_data(self, order_id, symbol):
        order_info = self.my_exchange.fetch_order(id = order_id, symbol = symbol) 
        return order_info
    
    async def get_order_info(self, order_id, symbol):
        if self.my_exchange.has['fetchOrder']:
            print("正在提取訂單資料...")
            task = asyncio.create_task(self.fetch_data(order_id, symbol))
            order_info = await task
            #print(order_info)
            return order_info
        else:
            print('本交易所不能提取資料')
# ======================================================================ASYNC FUNCTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def save_create_order_to_db(self, order_id, symbol):
        order_info      = asyncio.run(self.get_order_info(order_id, symbol))
        order_info_obj  = OKXOrderInfo(order_info)
        order_info_obj.save_create_order_to_db()

    def print_list(self,my_list):
        count = 1
        for i in my_list:
            i = json.dumps(i, indent=4)
            print(f"\n====================\n{nameof(my_list)}清單的第 {count} 個物件為:\n====================\n{i}")
            count += 1

    def print_item(self,item):
        print(f"\n====================\n{nameof(item)}為:\n====================\n{item}")
    
    def cancel_order(self, id, symbol):
        cancelled_order = self.my_exchange.cancel_order(id = id, symbol = symbol)
        self.print_item(cancelled_order)
        return cancelled_order

    
    def create_limit_order(self, symbol, side, contract_amount, price, type = 'limit', params = {}):
        new_limit_order     = self.my_exchange.create_order(symbol = symbol, side = side, amount = contract_amount, price = price, type = type, params =  params)
        order_id            = new_limit_order['info']['ordId']
        order_symbol        = new_limit_order['symbol']
        print (json.dumps(new_limit_order, indent=4))
        self.print_item(order_id)
        self.print_item(order_symbol)
        return [order_id, order_symbol]
    
    def fetch_my_trade(self):
        if self.my_exchange.has['fetchMyTrades']:
            my_trades = self.my_exchange.fetch_my_trades(symbol=None, since=None, limit=None, params={})
            self.print_list(my_trades)
        else:
            print('交易所不能提供你的交易的資料(你所使用的交易所的API不支持本功能。)')
    



    def fetch_my_trades_by_symbol(self, symbol):
        try:
            symbol_trade_history = self.my_exchange.fetch_my_trades(symbol)
            #existing_orders      = self.my_exchange.fetch_order(symbol)
            self.print_list(symbol_trade_history)
            #self.print_list(existing_orders)
        except Exception as e:
            print(e)

        
        

        # #pos = [p for p in position if p['symbol'] == "ETHUSDT"][0]
        # i=0
        # for trade in symbol_trade_history:
        #     i+=1
        #     print(trade)
        #     # print(trade["info"]["side"])
        #     # print(trade["info"]["tradeId"])
        #     # print(trade["id"])
        #     # print(trade["info"]["fillPx"])
        #     # print(trade["info"]["ordId"])
        #     # print(trade["cost"])
        #     # print(trade["price"])
        #     print("")
        #     print("")
            
        #     print(i)

    def close_position_of_symbol(self, symbol):
        close_position = self.my_exchange.create_order(symbol=symbol, type="MARKET", side="buy", amount=amount, params={"reduceOnly": True})


    def bot_action_after_received_signal(self):
        print('/n/n/n')
        print('bot_action_after_received_signal: executed...')
        print('/n/n/n')
        
        self.print_signal()
        #self.save_signal_to_DB()
        #self.set_lever()
        #self.close_all_position(symbol=None, tdMode=None)
        #self.create_order()
        #self.confirm_signal()
        #asyncio.run(self.get_order_info(500976312438390784, "MANA-USDT-SWAP"))
        #self.save_create_order_to_db(500976312438390784, "MANA-USDT-SWAP")

        #self.fetch_position_by_symbol("MANA-USDT-SWAP")
        #self.fetch_my_trades_by_symbol("FIL-USDT-SWAP")
        #self.create_limit_order(symbol="MANA-USDT-SWAP", side='buy', contract_amount=3, price=0.1)
        #self.cancel_order(id = '501248140406849540', symbol = "MANA-USDT-SWAP")
        #self.fetch_my_trade()
        #self.fetch_positions('SOL-USDT-SWAP')


        


class OKXOrderInfo:
    def __init__(self, response):
        self.contract_number        = response['info']['accFillSz']
        self.avg_price              = response['info']['avgPx']
        self.order_timestamp        = response['info']['cTime']
        self.fee                    = response['info']['fee']
        self.fee_currency           = response['info']['feeCcy']
        self.this_fill_price        = response['info']['fillPx']
        self.this_fill_timestamp    = response['info']['fillTime']
        self.symbol                 = response['info']['instId']
        self.lever                  = response['info']['lever']
        self.order_id               = response['info']['ordId']
        self.market_or_limit        = response['info']['ordType']
        self.pnl                    = response['info']['pnl']
        self.position_side          = response['info']['posSide']
        self.position_side          = response['info']['side']
        self.trade_mode             = response['info']['tdMode']
        self.datetime               = response['datetime']
        self.total_usdt             = response['cost']
        self.status                 = response['status']
        self.trade_id               = response["info"]['tradeId']
        
    
    def print_dict(self):
        print(self.__dict__)
    
    def save_create_order_to_db(self):
        print("saving...")
        print(self.__dict__)


