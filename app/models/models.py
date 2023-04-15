from    flask                      import current_app
from    flask_login                import UserMixin
from    app                        import db, login_manager, app
import  jwt

from    datetime                   import datetime



@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()#================================
    
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
class User(db.Model, UserMixin):
    id          = db.Column(db.Integer,     primary_key=True)
    username    = db.Column(db.String(80),  unique=True, nullable=False)
    nickname    = db.Column(db.String(80),  unique=True, nullable=False) #記得check
    password    = db.Column(db.String(80),  nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)

    avatar_img  = db.Column(db.String(120), default='/static/asset/default-avatar.png', nullable=False)

    posts       = db.relationship('Post',       backref = db.backref('author',  lazy = True))
    replies     = db.relationship('Reply',      backref = db.backref('replier', lazy = True))
    trades      = db.relationship('Trade',      backref = db.backref('trader',  lazy = True))
    APIs        = db.relationship('Api',        backref = db.backref('user',    lazy = True))
    signals     = db.relationship('Signal',     backref = db.backref('user',    lazy = True))
    gensignals  = db.relationship('GenSignal',  backref = db.backref('user',    lazy = True))


    followed    = db.relationship(
            'User', secondary   = followers,
            primaryjoin         = (followers.c.follower_id == id),
            secondaryjoin       = (followers.c.followed_id == id),
            backref             = db.backref('followers', lazy = True), lazy = True
    )

    def __repr__(self):
        return '<User %r>' % self.username
    
    def generate_reset_password_token(self):
        return jwt.encode({"id": self.id}, current_app.config["SECRET_KEY"], algorithm="HS256")#================================
    
    @staticmethod
    def check_reset_password_token(token):
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])#================================
            return User.query.filter_by(id=data['id']).first()
        except:
            return
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if  self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.count(user) > 0



class Post(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True)
    body        = db.Column(db.String(140), nullable=False, default ='')
    timestamp   = db.Column(db.DateTime, default = datetime.utcnow)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    replies     = db.relationship('Reply',  backref = db.backref('replied_post', lazy = True))


    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Reply(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True)
    body        = db.Column(db.String(140), nullable=False, default ='')
    timestamp   = db.Column(db.DateTime, default = datetime.utcnow)

    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id     = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


    def __repr__(self):
        return '<Reply {}>'.format(self.body)

class Trade(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True)
    strategy    = db.Column(db.String(140), nullable=False, default ='')
    action      = db.Column(db.String(140), nullable=False, default ='')
    exchange    = db.Column(db.String(140), nullable=False, default ='')
    symbol      = db.Column(db.String(140), nullable=False, default ='')
    trade_mode  = db.Column(db.String(30),  nullable=False, default ='')
    timestamp   = db.Column(db.DateTime, default = datetime.utcnow)

    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'),   nullable=False)
    signal_id   = db.Column(db.Integer, db.ForeignKey('signal.id'), nullable=False)

    


    def __repr__(self):
        return '<Trade {} | {} |  {} | {} | {} |>'.format(self.id, self.strategy, self.symbol, self.action, self.exchange)


class Api(db.Model, UserMixin):
    id                      = db.Column(db.Integer,     primary_key=True)

    api_name                = db.Column(db.String(140), nullable=False, default ='')
    exchange                = db.Column(db.String(140), nullable=False, default ='')
    api_key                 = db.Column(db.String(140), nullable=False, default ='')
    api_secret              = db.Column(db.String(140), nullable=False, default ='')
    api_password            = db.Column(db.String(140), nullable=False, default ='')
    signal_passpharse       = db.Column(db.String(140), nullable=False, default ='')

    api_created_timestamp   = db.Column(db.DateTime, default = datetime.utcnow)

    user_id                 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    robot_id                = db.Column(db.String(140), nullable=False, default ='')

    def __repr__(self):
        return '<API {} | {} |  {} | {} | {} | {} | >'.format(self.api_name, self.exchange, self.api_key, self.api_created_timestamp, self.signal_passpharse, self.user_id)
    


class Signal(db.Model, UserMixin):
    id                      = db.Column(db.Integer,     primary_key=True)

    strategy                = db.Column(db.String(140), nullable=True,  default ='')
    side                    = db.Column(db.String(20),  nullable=False, default ='')
    symbol                  = db.Column(db.String(30),  nullable=False, default ='')
    account_name            = db.Column(db.String(30),  nullable=True,  default ='')
    remarks                 = db.Column(db.String(300), nullable=True,  default ='')
    order_amount            = db.Column(db.Float,       nullable=True,  default =0.0)
    order_contact_size      = db.Column(db.Float,       nullable=True,  default =0.0)

    leverage                = db.Column(db.Integer,     nullable=False, default =1)
    interval                = db.Column(db.Integer,     nullable=False, default =60)
    robot_type              = db.Column(db.String(30),  nullable=True,  default ='')
    exchange                = db.Column(db.String(30),  nullable=False, default ='')
    time1                   = db.Column(db.DateTime,    nullable=False, default = datetime.utcnow)
    time2                   = db.Column(db.DateTime,    nullable=False, default = datetime.utcnow)
    price_now               = db.Column(db.Float,       nullable=False, default =0.0)
    close                   = db.Column(db.Float,       nullable=False, default =0.0)
    strategy_order_price    = db.Column(db.Float,       nullable=False, default =0.0)
    order_status_now        = db.Column(db.String(30),  nullable=True,  default ='')
    prev_order_status       = db.Column(db.String(30),  nullable=True,  default ='')
    prev_order_coin_num     = db.Column(db.Float,       nullable=True,  default =0.0)
    catobot_password        = db.Column(db.String(300), nullable=False, default ='')
    my_robot_id             = db.Column(db.Integer,     nullable=False, default =0)
    #signal_passpharse       = db.Column(db.String(140), nullable=False, default ='')
    trade_mode              = db.Column(db.String(30),  nullable=False, default ='')

    signal_rec_timestamp    = db.Column(db.DateTime, default = datetime.utcnow)

    user_id                 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trades                  = db.relationship('Trade',  backref = db.backref('signal',  lazy = True))
    


    def __repr__(self):
        return '<Signal {} | {} |  {} | >'.format(self.strategy, self.symbol, self.signal_rec_timestamp)



class GenSignal(db.Model, UserMixin):
    id                      = db.Column(db.Integer,             primary_key=True)

    strategy                = db.Column(db.String(140),         nullable=True,  default ='')
    robot_uid               = db.Column(db.String(100),         nullable=False, default ='')
    signal                  = db.Column(db.String(9999),        nullable=False, default ='')

    timestamp               = db.Column(db.DateTime,            default = datetime.utcnow)
    user_id                 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
   
    def __repr__(self):
        return '<GenSignal {} | {} |  {} | >'.format(self.strategy, self.robot_uid, self.timestamp)









#=======================flask admin import
#from flask_admin                import Admin
#from flask_admin.contrib.sqla   import ModelView
#=======================flask admin import

#admin               = Admin(app,name='CatoBog', template_mode='bootstrap3')

#=======================flask admin model view
#admin.add_view  (ModelView  (User,      db.session)  )
#admin.add_view  (ModelView  (Api,       db.session)  )
#admin.add_view  (ModelView  (Trade,     db.session)  )
#admin.add_view  (ModelView  (Post,      db.session)  )
#admin.add_view  (ModelView  (Reply,     db.session)  )
#admin.add_view  (ModelView  (Signal,    db.session)  )
#admin.add_view  (ModelView  (GenSignal, db.session)  )


#=======================flask admin model view

#===========to re-create the datebase

# from app.models import db
# db.create_all()