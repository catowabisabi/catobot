

import logging
from app.services.service_utilities import CommonFunctions as cf
class InvalidJSONError(Exception):
    pass
class Ticker():


    def check_is_contract_pair(ticker):
        return (ticker[-4:].lower()=="swap" or ticker[-4:].lower()=="perp") and len(ticker) > 7

    def change_perp_to_swap(ticker):
        if ticker[-4:].lower()=="perp":
            length = len(ticker)
            ticker = ticker[:length - 4]
            ticker = ticker + "swap"
        return ticker

    def remove_last_letters(str_to_delete_last_letters, number = 1):
        length = len(str_to_delete_last_letters)
        ticker = str_to_delete_last_letters[:length - number]
        return ticker
    
    def remove_first_letters(str_to_delete_fast_letters, number = 1):
        _ticker = str_to_delete_fast_letters.replace(str_to_delete_fast_letters[:number], '')
        return _ticker


    def remove_hyphen_from_ticker(ticker):
        ticker = ticker.split("-")
        ticker_without_hyphen = ""
        for symbol in ticker:
            ticker_without_hyphen = ticker_without_hyphen + symbol
        return ticker_without_hyphen

    def check_usdt_base(ticker_str):
        return ticker_str[-8:].lower() == "usdtswap"

    def convert_ticker_to_OKX_format(ticker, exchange):
        
        
        try: 
            if not exchange :
                raise ValueError("交易所不能為空")
        except ValueError as e:
            logging.error("Signal: 沒有交易所")
            cf.print_traceback()

        if exchange.upper() == "OKX":
            if Ticker.check_is_contract_pair(ticker):
                print("這有可能是合約 Tickers, 現進行分析...")
                ticker1 = Ticker.change_perp_to_swap(ticker)
                _ticker = Ticker.remove_hyphen_from_ticker(ticker1)
                _ticker = _ticker.upper()

                if Ticker.check_usdt_base(_ticker):
                    print("U本位合約")
                    symbol_list = ["","",""]
                    symbol_list[2] = _ticker[-4:]
                    symbol_list[1] = _ticker[-8:-4]
                    symbol_list[0] = Ticker.remove_last_letters(_ticker,8)
                
                else:
                    print("幣本位合約")
                    symbol_list = ["","",""]
                    symbol_list[2] = _ticker[-4:]
                    symbol_list[0] = _ticker[:4]
                    symbol_list[1] = _ticker[4:][:-4]
                    
                _ticker = symbol_list[0] + "-" + symbol_list[1] + "-"+symbol_list[2]
                _ticker = _ticker.upper()   
                return _ticker
                
        
            else:
                print(f"'{ticker}' 不是本機器人支持的格式。")
                return
        else:
            print(f"本機器人只能在OKX 使用, 暫不支時 {exchange} 交易所。請你檢查你的訊號源是否出錯。")

# test_string1 = "BTCUSDTPREP"
# test_string1 = "ETH-USDT-SWAP"
# test_string1 = "SHUBBBUSDTPREP"
# test_string1 = "Doge-Usdt-prep"
# test_string1 = "USDT-OXXxxxxxxxx-swap"



# Ticker.convert_ticker_to_OKX_format(test_string1)