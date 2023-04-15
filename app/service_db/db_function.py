from     werkzeug.utils                   import secure_filename
import   os
import   sqlite3
from     flask                            import request, flash, redirect, url_for, render_template
from     flask_login                      import login_user
from     sqlalchemy                       import create_engine, MetaData, Table, Column, Integer, String
from     app.models.models                import Post, User
from     app                              import db, bcrypt

from app.services.service_email           import send_reset_password_token

from app.services.service_gen_signal      import GenSignalJson
 

sqlite_file_location = 'sqlite:///app.db'


class RawSQLFunctions:
   def create_table():
      engine = create_engine(sqlite_file_location, echo = True)
      meta = MetaData()
      gensignal = Table(
            'gensignal',  meta, 
            Column('id',         Integer, primary_key = True), 
            Column('robot_uid',  String), 
            Column('signal',     String),
         )
      meta.create_all(engine)


   def add_column(database_name, table_name, column_name, data_type):

      # database_name  = 'app.db'
      # table_name     = 'gensignal'
      # column_name    = 'timestamp'
      # data_type      = 'String'
      # add_column(database_name, table_name, column_name, data_type)

      connection  = sqlite3.connect(database_name)
      cursor      = connection.cursor()

      if data_type == "Integer":
         data_type_formatted = "INTEGER"
      elif data_type == "String":
         data_type_formatted = "VARCHAR(100)"

      base_command = ("ALTER TABLE '{table_name}' ADD column '{column_name}' '{data_type}'")
      sql_command = base_command.format(table_name=table_name, column_name=column_name, data_type=data_type_formatted)

      print (sql_command)

      cursor.execute(sql_command)
      connection.commit()
      connection.close()

   def add_foreign_key(database_name, child_table, column_name, parent_table, parent_table_id):

      connection  = sqlite3.connect(database_name)
      cursor      = connection.cursor()

      base_command = ("ALTER TABLE {child_table} ADD COLUMN {column_name} INTEGER REFERENCES {parent_table}({parent_table_id})")
      sql_command  = base_command.format( child_table     = child_table, 
                                          column_name     = column_name, 
                                          parent_table    = parent_table, 
                                          parent_table_id = parent_table_id)

      print (sql_command)

      cursor.execute(sql_command)
      connection.commit()
      connection.close()


   database_name     = "app.db" 
   child_table       = "gensignal"
   column_name       = "user_id" 
   parent_table      = "user" 
   parent_table_id   = "id"
   #add_foreign_key(database_name, child_table, column_name, parent_table, parent_table_id)

# database_name  = 'app.db'
# table_name     = 'gen_signal'
# column_name    = 'strategy'
# data_type      = 'String'
# RawSQLFunctions.add_column(database_name, table_name, column_name, data_type)
#======================================================================================

class DataBaseFunctions:
   def __init__ (self, user):
      self.user = user
   
   def get_all_posts(self):
      page                        = request.args.get('page', 1, type = int)
      all_posts                   = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=5)
      return all_posts

   def send_msg (self, form):
      #print(form.body.data)
      print(f"由{self.user.username} 發出: \'{form.body.data}\'")
      body = form.body.data
      post = Post(body = body)
      user = User.query.filter_by(id = self.user.id).first()
      user.posts.append(post)
      db.session.commit()

   def reg_new_user(form):
      username    = form.username.data
      nickname    = form.username.data
      email       = form.email.data
      password    = bcrypt.generate_password_hash(form.password.data)
      user        = User(username = username, email = email, password =  password, nickname = nickname)
      db.session.add(user)
      db.session.commit()
      return [username, email, nickname]
   
   def login(form):
      username    = form.username.data
      password    = form.password.data
      remember_me = form.remember_me.data
      # Check if user is exists and password matched
      user        = User.query.filter_by(username = username).first()
      pw_matched  = False
      if user:
         pw_matched  = bcrypt.check_password_hash(pw_hash= user.password, password= password)

      if user and pw_matched:
         login_user(user, remember=remember_me)
         flash(f'登入成功! 歡迎使用Catobot交易機器人, {username} !', category='info')
         print (f"\n 用戶登入: \n{username}, {password}\n")
         
         # 如果有next就去下一頁而不是index
         if request.args.get('next'):
            print('login stop1')
            next_page = request.args.get('next')
            return redirect(next_page)
         else:
            print('login stop2')
            return redirect(url_for('index'))
      else:
         print('login stop3')
         print (f"\n 用戶ID 或密碼錯誤 \n")
         flash('用戶ID 或密碼錯誤', category='danger')
   
   def login_re(username, password, remember_me):
      # Check if user is exists and password matched
      user        = User.query.filter_by(username = username).first()
      pw_matched  = False
      if user:
         pw_matched  = bcrypt.check_password_hash(pw_hash= user.password, password= password)

      if user and pw_matched:
         login_user(user, remember=remember_me)
         flash(f'登入成功! 歡迎使用Catobot交易機器人, {username} !', category='info')
         print (f"\n 用戶登入: \n{username}, {password}\n")
         
         # 如果有next就去下一頁而不是index
         if request.args.get('next'):
            print('login stop1')
            next_page = request.args.get('next')
            return redirect(next_page)
         else:
            print('login stop2')
            return redirect(url_for('index'))
      else:
         print('login stop3')
         print (f"\n 用戶ID 或密碼錯誤 \n")
         flash('用戶ID 或密碼錯誤', category='danger')
   
   def reset_password(form):
      email           = form.email.data
      # Check if email is exists
      user           = User.query.filter_by(email = email).first()
      token          = user.generate_reset_password_token()
      db.session.commit()
      send_reset_password_token(user, token)
      print(user.username, user.email)
      flash('已發送重置密碼電郵! 請檢查一下你的郵箱。', category = 'Info')
   
   def actually_change_password(form, token):
      user = User.check_reset_password_token(token) # 返回user
      if user:
         user.password = bcrypt.generate_password_hash(form.password.data)
         db.session.commit()

         flash('你的密碼已經被重置! 請重新登入。', category = 'info')
         return redirect(url_for('login'))

      else: 
         flash('沒有這個用戶')
         return redirect(url_for('login'))
   
   def follow_user(self, username):
      user = User.query.filter_by(username = username).first()
      if user:
         self.user.follow(user)
         db.session.commit()
         page          = request.args.get('page', 1, type = int)
         posts         = Post.query.filter_by(user_id = user.id).order_by(Post.timestamp.desc()).paginate(page=page, per_page=5)
         return render_template('user_page.html', user=user, posts = posts)
      else:
         return "404"
   
   def unfollow_user(self, username):
      user = User.query.filter_by(username = username).first()
      if user:
         self.user.unfollow(user)
         db.session.commit()
         page          = request.args.get('page', 1, type = int)
         posts         = Post.query.filter_by(user_id = user.id).order_by(Post.timestamp.desc()).paginate(page=page, per_page=5)
         return render_template('user_page.html', user=user, posts = posts)
      else:
         return "404"
   
   def allowed_file(filename):
      ALLOWED_EXTENSION = {'jpg', 'jpeg', 'png', 'gif'}
      return '.' in filename and \
                  filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION
   
   def change_avatar(self, form):
      f = form.photo.data
      if f.filename == '':
         flash('沒有選擇圖片', catagory = 'danger')
      if f and self.allowed_file(f.filename):
         filename = secure_filename(f.filename)
         f.save(os.path.join('app', 'static', 'asset', filename))
         self.user.avatar_img = '/static/asset/' + filename
         db.session.commit()
         return redirect(url_for('user_page', username = self.user.username))
   
   def edit_nickname(self, edit_profile_form):
      nickname = edit_profile_form.nickname.data
      if nickname == '':
         flash('不能留空', catagory = 'danger')
      if nickname:
         self.user.nickname = nickname
         db.session.commit()
         return redirect(url_for('user_page', username = self.user.username))
   
   def gen_api(self, form):
        if self.user.is_authenticated:
         user = User.query.filter_by(id = self.user.id).first()
         print(f"\n\n由{user.nickname} ({user.nickname}) 生産 Tradingview Webhook 訊號 (策略: {form.strategy.data})\n")
         my_gen_signal   = GenSignalJson(data = form)
         signal_json     = my_gen_signal.input_to_json()
         print(signal_json)
         my_gen_signal.save_json_to_db(user = user)
         
         #{json.dumps(signal_json, separators=(',', ':')).encode('utf8')}
         flash(f"請把這訊號字串貼到 TradingView 警報 的訊號欄 : \n{signal_json}", category = 'success')

        else:
         print(f"你沒有登入")
         flash(f"你沒有登入")
