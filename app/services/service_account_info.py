from  flask_login                       import current_user
from  app.services.service_robot_1      import Robot
from  app.services.service_sizer        import Sizer
from  app.models.models                 import Api



class AccountInfo:
    # 要傳入一個exchange的obj
    def __init__(self, user):

        self.user               = user
        if self.user:
            self.default_api    = Robot.get_api_by_user(self.user)
        else:
            self.default_api    = None

        [self.my_exchange, self.my_exchange_type] = self.get_my_exchange()

        
    def get_my_exchange(self):
        try:
            my_exchange         = Robot.get_exchange(self.default_api)
            my_exchange_type    = "private"
        except:
            print('沒有使用者, 拿不到API, 使用Default Exchange!')
            my_exchange         = Robot.get_default_exchange()
            my_exchange_type    = "public"
        return [my_exchange, my_exchange_type]
    

    def fetch_positions(self):
        #markets = my_exchange.load_markets()
        #market = my_exchange.market(symbol)
        #indexed = self.my_exchange.index_by(positions, 'future')
        #position = self.my_exchange.safe_value(indexed, market['id'])
        positions = self.my_exchange.fetch_positions()

        list_of_position = []
        sizer = Sizer()
        instruments = sizer.initInstruments()
        balance = self.my_exchange.fetch_balance()["info"]["data"][0]["details"][0]["eq"]
        for position in positions:
            #print(position)
            position = Position(position, instruments, balance)
            #position.show()
            list_of_position.append(position)
        return list_of_position
        
        
  



class Position:
    def __init__(self, position, instruments, balance):
        self.sizer                              = Sizer()
        
        self.creation_time                      = position['info']['cTime']
        self.datetime                           = position['datetime']
        self.datetime                           = Robot.datetime_string_to_datetime(self.datetime)
        self.datetime_string                    = Robot.datetime_formater(self.datetime)

        self.symbol                             = position['info']['instId']
        self.position_id                        = position['info']['posId']
        self.leverage                           = Robot.round_it(float(position["leverage"]), 1)
        self.margin_mode                        = "逐倉" if position['marginMode'] == 'isolated' else '全倉'

        self.existing_position_side             = position['info']['pos']
        self.coin_number_per_contract           = self.sizer.getFaceValue2(self.symbol, instruments)

        self.total_coins_purchased              = abs(float(self.existing_position_side) * float(self.coin_number_per_contract))
        

        self.entry_price                        = abs(position['entryPrice'])
        self.entry_price_r                      = Robot.round_it(float(self.entry_price), 3)
        self.avg_price                          = position['info']['avgPx']
        self.avg_price_r                        = Robot.round_it(float(self.avg_price), 3)
        self.mark_price                         = position['info']['markPx']
        self.mark_price_r                       = Robot.round_it(float(self.mark_price), 3)
        self.mark_price_update_time             = position['info']['uTime']
        self.estimated_liquidation_price        = position['info']['liqPx']
        self.estimated_liquidation_price_r      = Robot.round_it(float(self.estimated_liquidation_price), 3)
        self.position_usdt_amount               = position['info']['notionalUsd']
        self.position_usdt_amount_r             = Robot.round_it(float(self.position_usdt_amount), 2)
        self.collateral                         = position['collateral']
        self.collateral_r                       = Robot.round_it(float(self.collateral), 3)

        self.unrealized_profit_and_loss         = position['info']['upl']
        self.unrealized_profit_and_loss_r       = Robot.round_it(float(self.unrealized_profit_and_loss), 2)
        #self.liabilities_due_to_unrealized_loss = position['uplLib']

        self.initial_margin_percentage          = position['initialMarginPercentage']
        self.initial_margin_percentage_r        = Robot.round_it(float(self.initial_margin_percentage), 2)
        self.maintenance_margin_requirement     = position['info']['mmr']
        self.maintenance_margin_requirement_r   = Robot.round_it(float(self.maintenance_margin_requirement), 2)        
        self.margin                             = position['info']['margin']
        self.margin_r                           = Robot.round_it(float(self.margin), 2)
        self.margin_ratio                       = position['info']['mgnRatio']
        self.margin_ratio_r                     = Robot.round_it(float(self.margin_ratio), 2)
        self.maintenance_margin                 = position['maintenanceMargin']
        self.maintenance_margin_r               = Robot.round_it(float(self.maintenance_margin), 3)
        self.maintenance_margin_Percentage      = position['maintenanceMarginPercentage']
        self.maintenance_margin_Percentage_r    = Robot.round_it(float(self.maintenance_margin_Percentage), 3)

        self.paid_usdt                          = abs(float(self.existing_position_side) * float(self.coin_number_per_contract) * float(self.entry_price))
        self.paid_usdt_r                        = Robot.round_it(float(self.paid_usdt), 3)

        #self.this_trade_cost                    = abs(round(((self.total_coins_purchased * float(self.entry_price)) / float(self.leverage)) , 2))
        self.used_fund_percentage               = abs(round((self.margin_r / float(balance) *100) , 2))
        self.pnl_percentage                     = round(((float(self.unrealized_profit_and_loss) / self.margin_r) * 100), 2)

        self.this_pos_to_acc_percentage         = round(self.pnl_percentage * self.used_fund_percentage / 100,2)

        self.direction = '沒有'
        
        if   float(self.existing_position_side) > 0:
            self.direction = "多"
        elif float(self.existing_position_side) < 0 :
            self.direction = "空"

    def __repr__(self):
        label = f'\n\n<Position || 下單時間 TS : {self.creation_time} | 下單時間 DT : {self.datetime} |\n\n\
交易對 : {self.symbol} | 持倉ID : {self.position_id} | 合約張數和方向 : {self.existing_position_side} |\n\
成交均價 : {self.avg_price} | 現時的標記價格 : {self.mark_price} | 訂單資訊更新時間 : {self.mark_price_update_time} |\n\
預計強平價 : {self.estimated_liquidation_price} | 本倉位現時的美金使用量 : { self.position_usdt_amount} | 抵押 : {self.collateral} |\n\
未實現盈虧 : {self.unrealized_profit_and_loss} |\n\
開始時的保証金百分比 : {self.initial_margin_percentage} | 維持保證金(美金) : {self.maintenance_margin_requirement} | 保證金餘額 : {self.margin} |\n\
保証金率 : {self.margin_ratio} | maintenanceMargin : {self.maintenance_margin} | maintenanceMarginPercentage : {self.maintenance_margin_Percentage} |>\n\n\n'
        return label
        #未實現盈虧所導致的負債 : {self.liabilities_due_to_unrealized_loss}

    def show(self):
        print(self.__repr__)