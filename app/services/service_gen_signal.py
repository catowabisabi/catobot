from app.models.models             import GenSignal,  Api
from app                    import db
import json



class GenSignalJson:

    # def __init__(self,  strategy:str,        account:str,     
    #                     use_perc_tp:bool,    use_perc_sl,    
    #                     tp_perc:float,       sl_perc:float,  
    #                     tdMode:str,          lever:int, 
    #                     market_or_limit:str, signal_pw:str,
    #                     robot_uid:int,       remarks:str
    #                     ):
    def __init__(self, data):
        
        self.strategy        = data.strategy.data     
                
        self.use_perc_tp     = data.use_perc_tp.data
        self.use_perc_sl     = data.use_perc_sl.data
        self.tp_perc         = data.tp_perc.data
        self.sl_perc         = data.sl_perc.data
        self.tdMode          = data.tdMode.data
        self.lever           = data.lever.data
        self.market_or_limit = data.market_or_limit.data
        #self.signal_pw       = data.signal_pw.data
        self.remarks         = data.remarks.data

        if  self.use_perc_tp == True:
            self.use_perc_tp = "是"
        elif self.use_perc_tp == False:
            self.use_perc_tp = "否"
        
        
        if  self.use_perc_sl == True:
            self.use_perc_sl = "是"
        elif self.use_perc_sl == False:
            self.use_perc_sl = "否"
        

        api = Api.query.filter_by(id = data.api_id.data).first()
        self.robot_id       = api.robot_id
        self.signal_pw      = api.signal_passpharse
        self.account        = api.api_name
        self.signal_json    = None

    def input_to_json(self):
        self.signal_json =     {
                    "策略": f"{self.strategy}",
                    "帳戶": f"{self.account}",
                    "股票": "{{ticker}}",
                    "每注": 0,
                    "倍數": self.lever,
                    "注解":f"{self.remarks}",

                    "是否自定義固定止盈": f"{self.use_perc_tp}",
                    "自定義止盈百份比": self.tp_perc,

                    "是否自定義固定止損": f"{self.use_perc_sl}",
                    "自定義止損百份比": self.sl_perc,


                    "週期": "{{interval}}",
                    "機器人": "CATOBOT",
                    "交易所": "{{exchange}}",

                    "時間1": "{{time}}",
                    "時間2": "{{timenow}}",
                    "當前下單幣數": "{{strategy.market_position_size}}",
                    "交易動作": "{{strategy.order.action}}",
                    "交易合約量": "{{strategy.order.contracts}}",
                    "交易入場/出場價": "{{strategy.order.price}}",
                    "收盤價": "{{close}}",

                    "當前倉位狀態": "{{strategy.market_position}}",
                    "之前倉位狀態": "{{strategy.prev_market_position}}",
                    "上次下單的幣數": "{{strategy.prev_market_position_size}}",
                    "CatoBot密碼" : f"{self.signal_pw}",
                    "你的機器人ID": f"{self.robot_id}", 
                    "倉位模式": f"{self.tdMode}",
                    "計價方式": "USDT",
                    "巿價/限價" : f"{self.market_or_limit}"
                        }
        self.signal_json = json.dumps(self.signal_json, indent=4, ensure_ascii=False)
        return self.signal_json

    def save_json_to_db(self, user):
        user        = user
        signal_json = str(self.input_to_json())
        
        gensignal   = GenSignal(strategy = self.strategy, robot_uid = self.robot_id, signal = signal_json)
        user.gensignals.append(gensignal)
        db.session.commit()
        return signal_json

        


