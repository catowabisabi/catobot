import yaml
from  app            import app
from  flask          import request, render_template
from  flask_login    import current_user, login_required

from  app.services.service_robot_1      import Robot
from  app.services.service_sizer        import Sizer
from  app.services.service_account_info import AccountInfo
from  app.models.service_create_db_from_models import CreateNew, AppFormater

@app.route("/test", methods=['GET', 'POST'])
#@login_required
def test():
    output  = None
    
    try:
        api             = current_user.APIs[0]
        #print(api)
        my_exchange     = Robot.get_exchange(api)
    except:
        print('沒有使用者, 拿不到API, 使用Default Exchange!')
        api             = None
        my_exchange     = Robot.get_default_exchange()
 

    if request.method == 'POST':
        #print(current_user)
        #print(api)
        if request.form.get('action') == '提取: Config (Robot)':
            text_msg    = Robot.get_robot_config()
            parsed      = yaml.dump(text_msg, default_flow_style=False)
            print (parsed)

        if request.form.get('action') == '提取: 所有交易所的 名字':
            Robot.print_all_exchange()
        
        if request.form.get('action') == '提取: 指定交易所的 所有 貨幣對':
            #my_exchange     = Robot.get_default_exchange()
            output = Robot.load_markets_in_exchange(my_exchange)
            #return render_template('test.html', output = output)

        if request.form.get('action') == '提取: 你的交易所的 指定的交易對 的K線的 最新資料':
            my_ticker = "BTC/USDT"
            timeframe = '1h'
            output = Robot.get_ohlc(my_exchange, my_ticker, timeframe)
            output = output[1]
            return render_template('test.html', output = output)

        if request.form.get('action') == '提取: 你的交易所的 指定的貨幣交易對':
            
            selected_symbol = "BTC"
            output = Robot.load_markets_in_exchange_with_selected_crypto(my_exchange, selected_symbol)
            return render_template('test.html', output = output)
                
        if request.form.get('action') == '提取: 你的交易所的 指定的交易對 的OrderBook':
            ticker = "BTC/USDT"
            output = Robot.get_older_book(my_exchange, ticker) #沒有return
            return render_template('test.html', output = output) 

        if request.form.get('action') == '提取: 你的交易所的 Balance': # 可能有錯, 呢個要再check check
            coin_symbol = "USDT" #無用
            output = Robot.get_balance(my_exchange, coin_symbol) #沒有return
            return render_template('test.html', output = output) 

        if request.form.get('action') == '獲取公共數據，包含合約面值等訊息':
            sizer  = Sizer(my_exchange)
            output = sizer.initInstruments()
            return render_template('test.html', output = output) 
            #獲取公共數據，包含合約面值等訊息 
        
        if request.form.get('action') == '萬能測試':
            my_account_info = AccountInfo(user = current_user)
            my_account_info.fetch_positions()

            return render_template('test.html', output = output) 

        
        if request.form.get('action') == '重建DB':
            AppFormater.quick_format()
            
            create_new = CreateNew()
            create_new.create_user()
            create_new.create_api()
            return render_template('test.html', output = output) 


    return render_template('test.html', output = output)
    
