from flask              import Flask
from flask_bootstrap    import Bootstrap
from flask_bcrypt       import Bcrypt
from flask_sqlalchemy   import SQLAlchemy as sqla
from flask_login        import LoginManager
from config.config             import Config
from flask_mail         import Mail




app                 = Flask(__name__)
app.config.from_object(Config)

mail                = Mail(app)

login_manager                           = LoginManager()
login_manager.init_app(app)
login_manager.login_view                = 'login'
login_manager.login_message             = '你必須登入才能顯示這面頁'
login_manager.login_message_category    = 'info'

bootstrap           = Bootstrap (app)
db                  = sqla      (app)
bcrypt              = Bcrypt    (app)




from app.routes                     import *




