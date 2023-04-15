from numpy import empty
from        app                import app
import      logging
from        config.config             import Config
from        app.services.service_sizer     import Sizer, Log

listenPort      = Config.listen_Port
listenHost      = Config.listen_Host
debugMode       = Config.debug_mode
log_filename    = Config.log_filename

Log.log_init(log_filename)

#開始 20230404
if __name__ == '__main__':
    
    try:
        logging.info("\n\n\n\n\n")
        logging.info("* CatoBot TradingView Webhook Auto Trader")
        logging.info("\n")
        logging.info("①.此程序只支持OKEX歐易交易所")
        logging.info("②.建議在有獨立IP的服務器上運行，在個人電脑腦運行需要FRP内網穿透，而且影響軟件效率")
        logging.info("③.每個帳戶的每個API設立時都會隨機生産一個 WEBHOOK 號碼以作配對, 用戶要為自己的每一個 API 設立一個密碼, API 密碼 與 帳號密碼 是獨立的, API 密碼與 WEBHOOK 號碼必需配合才能進能交易動作。")

        # 初始化交易所的貨幣基本訊息
        test_sizer = Sizer()
        if test_sizer.initInstruments() is False:
            msg = "初始化交易所的貨幣基本訊息失敗，請重試。"
            raise Exception(msg)
        # Bot Start
        if test_sizer.initInstruments() is not empty:
            print("\n\n系统接口服務啓動！服務監聽地址: localhost:{listenPort}\n".format(listenPort=listenPort, listenHost=listenHost))
        app.run(debug=debugMode, port=listenPort, host=listenHost)
        
        #app.run(debug=True, host='0.0.0.0', port=3000)
    except Exception as e:
        logging.error(e) 
        pass