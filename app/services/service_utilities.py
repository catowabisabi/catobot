import uuid
import sqlite3

from app.models.models      import User, Api
from datetime               import datetime
from flask_login            import current_user
from app                    import db, bcrypt
from flask                  import flash

import                             traceback
import                             sys



#====================================這是一些有可能用到的功能
#====================================Common Functions
class CommonFunctions:

    def print_traceback():
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=sys.stdout)

    # return a str of uuid (生産一個UUID)
    def gen_uuid():
        #id = uuid.uuid1().bytes
        #id = uuid.uuid1().int
        #id = uuid.uuid1().hex
        #id = uuid.uuid1().version
        #id = uuid.uuid1().fields
        #id = uuid.uuid1().variant
        id = uuid.uuid4()
        #print ("The random id using uuid1() is : ",end="")
        #print (id)
        return str(id)
    
    def add_item_to_list(list_of_items: list, add_item):
        list_of_items.append(add_item)
        return list_of_items


    def connect_sqlit3_db(db_file_path):
        conn = sqlite3.connect(db_file_path)
        print("Database connected!")
        return conn
           

    def create_table_for_str_var_in_db(db_file_path, _var):
        connection = CommonFunctions.connect_sqlit3_db(db_file_path)
        # 建立一個user table
        try:
            connection.execute(f'create table {str(_var)} (id integer primary key, name varchar(99999))')
            print (f"Created table {str(_var)}")
            
        except Exception as e:
            print(f"Create Table Error: {e}")
        connection.close()

    # 插入資料同樣使用 execute(), 只是在插入資料後執行 commit():
    def insert_str_var_to_db(db_file_path, _var: str, value_str: str):
        data = [value_str]
        connection = CommonFunctions.connect_sqlit3_db(db_file_path)
        try:
            connection.execute(f"insert into {_var} (name) values (?)", data)
            connection.commit()
            print ("Created records")
        except Exception as e:
            print(f"Insert Data Error: {e}")
        connection.close()
    

    def get_data_from_db(db_file_path, db_table, db_field):
        try:
            connection = CommonFunctions.connect_sqlit3_db(db_file_path)
            cursor = connection.execute(f"SELECT id, {db_field} from {db_table}")
            data = []
            for row in cursor:
                #print (f"ID = {row[0]}, Name = {row[1]}")
                data.append(row[1])
            connection.close()
            return data
        except Exception as e:
            print(f"Get Data Error: {e}")
    
    def update_data_from_db(db_file_path, table_name:str, field_name:str, new_data:str, id):
        id = str(id)
        try:
            connection = CommonFunctions.connect_sqlit3_db(db_file_path)
            connection.execute(f"UPDATE {table_name} set {field_name} = '{new_data}' where id = {id}")
            connection.commit()
            print (f"Total number of rows updated : {connection.total_changes}")
            print ("Operation done successfully")
            connection.close()
        except Exception as e:
            print(f"Update Data Error: {e}")
    
    def delete_data_from_db(db_file_path, table_name:str, id):
        try:
            # DELETE 刪除資料
            connection = CommonFunctions.connect_sqlit3_db(db_file_path)
            connection.execute(f"DELETE from {table_name} where id = {id};")
            connection.commit()
            if connection.total_changes == 0 :
                print(f'你想要刪除的目標不存在。')
            else:
                print (f"Total number of rows deleted : {connection.total_changes}")
                print ("Operation done successfully")
            connection.close()
        except Exception as e:
            print(f"Update Data Error: {e}")
    


    def create_api_obj(api_form):
        try:
            form = api_form
            api_name        = form.api_name.data
            exchange        = form.exchange.data
            api_key         = form.api_key.data
            api_secret      = form.api_secret.data
            api_password    = form.api_password.data
            signal_password = bcrypt.generate_password_hash(form.signal_password.data)
            user_id         = current_user.id
            robot_id        = CommonFunctions.gen_uuid()  
            
            api_created_timestamp  = datetime.utcnow()
        except:
            try:
                data = api_form
                                
                api_name        = data["api_name"]
                exchange        = data["exchange"]
                api_key         = data["api_key"]
                api_secret      = data["api_secret"]
                api_password    = data["api_password"]
                signal_password = data["signal_password"]
                user            = User.query.filter_by(username = data["username"]).first()
                user_id         = user.id
                robot_id        = data["robot_id"]  
                
                api_created_timestamp  = datetime.utcnow()
            except Exception as e:
                print (e)


        #date            = int(datetime.fromtimestamp(api_created_timestamp))

        db_file_path    = "app.db"
        db_table        = "api"
        db_field        = "robot_id"
        robot_id_list   = CommonFunctions.get_data_from_db(db_file_path, db_table, db_field)

        while True: #不要有相同的ID
            if robot_id in robot_id_list:
                robot_id = CommonFunctions.gen_uuid() 

            else:
                break

        
        api       = Api(api_name = api_name, exchange = exchange, api_key =  api_key, 
                        api_secret = api_secret, api_password = api_password, 
                        signal_passpharse = signal_password, api_created_timestamp = api_created_timestamp,
                        user_id = user_id, robot_id = robot_id)
        return api

    def create_api_to_db(api, _user=None):
        if _user == None:
            user = User.query.filter_by(id = current_user.id).first()
        else:
            user = _user
        user.APIs.append(api)
        # db.session.add(api)
        db.session.commit()
        flash('新的API已經加入', category = 'success')
        
        


    
#======================================================Function Demo 功能展示

#==================================================================================create uuid
#uuid_str = CommonFunctions.gen_uuid()
#print(uuid_list)
#print("\n")
#uuid_str = str(uuid_str)
#==================================================================================create uuid


#==================================================================================db variable
#var_name = "uuid"
#db_file_path = "./database/saved_variables.db"
#db_field = "name"
#==================================================================================db variable


#==================================================================================create table
#CommonFunctions.create_table_for_str_var_in_db(db_file_path, var_name)
#==================================================================================create table


#==================================================================================insert data
#CommonFunctions.insert_str_var_to_db(db_file_path, var_name, str(uuid_str))  
#==================================================================================insert data


#==================================================================================update data
#uuid_list = CommonFunctions.get_data_from_db(db_file_path, var_name, db_field)
#print(uuid_list)

#CommonFunctions.update_data_from_db(db_file_path,var_name, db_field, uuid_str, 2)

#uuid_list = CommonFunctions.get_data_from_db(db_file_path, var_name, db_field)
#print(uuid_list)
#==================================================================================update data


#==================================================================================delete data
# uuid_list = CommonFunctions.get_data_from_db(db_file_path, var_name, db_field)
# print(f'\n{uuid_list}\n')

# CommonFunctions.delete_data_from_db(db_file_path, var_name, 3)

# uuid_list = CommonFunctions.get_data_from_db(db_file_path, var_name, db_field)
# print(f'\n{uuid_list}\n')
#==================================================================================delete data
    
class Demo:
    def __init__(self):
        pass


    # 建立一個database file
    def db_ops_demo():
        db_file_path = "./database/test.db"
        connection = CommonFunctions.connect_sqlit3_db(db_file_path)

        # 建立一個user table
        try:
            connection.execute('create table user (id varchar(20) primary key, name varchar(20), email varchar(50))')
            print ("Created table user")
        except Exception as e:
            print(f"Create Table Error: {e}")
            

        # 插入資料同樣使用 execute(), 只是在插入資料後執行 commit():
        try:
            connection.execute("insert into user values (1, 'member1', 'member1@email.tld')")
            connection.execute("insert into user values (2, 'member2', 'member2@email.tld')")
            connection.execute("insert into user values (3, 'member3', 'member3@email.tld')")
            connection.commit()
            print ("Created records")
        except Exception as e:
            print(f"Insert Data Error: {e}")

        #以下是在 Sqlite 資料庫讀取資料的寫法:
        cursor = connection.execute("SELECT id, name, email from user")
        for row in cursor:
            print (f"ID = {row[0]}", row[0])
            print (f"Name = {row[1]}", row[1])
            print (f"Email = {row[2]}", row[2])

        # UPDATE 更新資料
        connection.execute("UPDATE user set name = 'new-name' where id = 1")
        connection.commit()
        print (f"Total number of rows updated : {connection.total_changes}")
        print ("Operation done successfully")

        # DELETE 刪除資料
        connection.execute("DELETE from user where id = 2;")
        connection.commit()
        print (f"Total number of rows deleted : {connection.total_changes}")
        print ("Operation done successfully")

        connection.close()