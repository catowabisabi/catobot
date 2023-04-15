#================================================================import flask function and basic app function
from app                             import app
from flask                           import request, render_template
from flask_login                     import login_required, current_user
from app.models.models               import User, Post

#================================================================import services
from app.services.service_robot_1    import *
from app.services.service_sizer      import *
from app.services.service_follower   import Follower
from app.services.service_user_info  import UserInfo
from app.service_db.db_function      import DataBaseFunctions
from app.services.service_account_info import AccountInfo

from app.my_routes.routes_test          import *
from app.my_routes.routes_webhook       import *
from app.my_routes.routes_auth          import *
from app.my_routes.routes_user_function import *


web_title                = "CATOBOT WEBHOOK 機器人 V0.01"
user_db                  = DataBaseFunctions(current_user)
followers                = Follower(current_user)
app_supported_exchange   = ['OKX']

#===================================================== INDEX
@app.route("/", methods=['GET', 'POST'])
def index():
    web_title = "title"
    web_information   = ['OKX']
    return render_template('index.html', 
                            title           = web_title, 
                            data            = web_information, 
                            )
#===================================================== INDEX

#===================================================== INDEX
@app.route("/notification_center", methods=['GET', 'POST'])
@login_required
def notification_center():
    num_followers, num_followed = followers.get_number_of_followers()
    all_posts                   = user_db.get_all_posts()   
    return render_template('notification_center.html', 
                            title           = web_title, 
                            data            = app_supported_exchange, 
                            num_followers   = num_followers, 
                            num_followed    = num_followed, 
                            posts = all_posts)
#===================================================== INDEX

#===================================================== API PAGE
@app.route("/robots", methods=['GET', 'POST'])
@login_required
def robots():
    data  = []
    my_info = UserInfo(current_user)
    if request.method == 'POST': 
        value =  request.form.get('action')
        print (f'delete this API : {value}')
    return render_template('robots.html', title = web_title, 
                                          data  = data, 
                                          APIs  = my_info.APIs)
#===================================================== API PAGE

#===================================================用戶面頁
@app.route("/user_page/<username>")
@login_required
def user_page(username):
    user = User.query.filter_by(username = username).first()
    if user:
        page          = request.args.get('page', 1, type = int)
        posts         = Post.query.filter_by(user_id = user.id).order_by(Post.timestamp.desc()).paginate(page=page, per_page=5)
        return render_template('user_page.html', user=user, posts = posts)
    else:
        return "404"

#===================================================帳戶面頁
@app.route("/account_info_mini", methods=['GET', 'POST'])
@login_required
def account_info_mini():
    html_title= ''
    paragraph = ''
    name_of_list_html = 'my_positions_list_mini.html'
    my_trades = AccountInfo(current_user)
    my_trades = my_trades.fetch_positions()
    if my_trades:
        return render_template('common_list.html', html_title=html_title, paragraph=paragraph, name_of_list_html=name_of_list_html, my_trades = my_trades)
    else:
        return "404"

#===================================================帳戶面頁
@app.route("/account_info", methods=['GET', 'POST'])
@login_required
def account_info():
    html_title= ''
    paragraph = ''
    name_of_list_html = 'my_positions_list.html'
    my_trades = AccountInfo(current_user)
    my_trades = my_trades.fetch_positions()
    if my_trades:
        return render_template('common_list.html', html_title=html_title, paragraph=paragraph, name_of_list_html=name_of_list_html, my_trades = my_trades)
    else:
        return "404"
