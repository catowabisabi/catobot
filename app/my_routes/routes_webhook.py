
from app                            import app
from flask                          import request
from app.models.models              import User

from app.services.service_trade     import TradeService, Signal
from app.services.service_robot_1   import Robot
import logging



@app.route("/webhook", methods=['GET', 'POST'])
def send_recieved_json_to_database():
    recieved_msg    = request.json #接收到信號

    signal          = Signal(recieved_msg)
    if (signal.check_signal()):

        trade_service   = TradeService(recieved_msg)
        if not trade_service.ready():
            trade_service.bot_action_after_received_signal()
        else:
            return {
                "code": 500,
                "msg" : '訊號錯誤: 請檢查你的訊號的 API ID 或 訊號密碼!'
                }
        return {
            "code": 200,
            "msg" : recieved_msg
        }
    else:
        print("error: Signal出錯")
        return {
            "code": 500,
            "msg" : "Signal出錯..."
        }