# -*- coding: utf-8 -*-
import      configparser
#import      ccxt
import      logging
#from        flask import Flask
#from        flask import request, abort
import      json
import      urllib.request
import      requests
import      os
import      _thread
import      time


class Robot_0:
#===============================================================讀取配置文件
    def get_robot_config(self):
        config = {}
        if os.path.exists('./config.json'):
            config      = json.load(open('./config.json',encoding="UTF-8"))
            
            print  ("成功讀取: config.json")
            print  (config)
            return config

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

            print  ("成功讀取: config.ini")
            print  (config)
            return config

        else:
            logging.info("配置文件 config.json 不存在，程序即將退出")
            print       ("配置文件 config.json 不存在，程序即將退出")
            exit()
#===============================================================讀取配置文件