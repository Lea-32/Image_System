from Img_System.routes.config import config
import pyodbc

connection_string = config('root')
cn = pyodbc.connect(connection_string)
cursor = cn.cursor()
'''
#查询当前用户数量
img_id = 2
cursor.execute("SELECT * from Image ")
rows = cursor.fetchall()#捕捉一行结果
#rows = cursor.fetchall()#捕捉所有行结果，构成一个列表

user_id = 3  # 用实际的用户ID替代
cursor.execute("SELECT * from Users Where user_id = ?", user_id)
user = cursor.fetchone()
print(rows)
print(user)
#print(str(int(time.time())))'''


# 定义触发器
#sql_query = '''
#CREATE TRIGGER renumber_favorite_id
#ON Favorite
#AFTER DELETE
#AS
#BEGIN
#    UPDATE Favorite
#    SET favorite_id = favorite_id - 1
#    WHERE favorite_id > (SELECT MIN(favorite_id) FROM DELETED);
#END;
#'''

#修改级联
sql_query = """
ALTER TABLE Tag_index
ADD CONSTRAINT FK_Tag_index_Image
FOREIGN KEY (img_id) REFERENCES Image(img_id) ON DELETE CASCADE;
    """



#赋予权限
database = 'Image_System'
cursor.execute("CREATE LOGIN common_user WITH PASSWORD = '123456';")
cursor.execute("CREATE USER common_user FOR LOGIN common_user;")
cursor.execute("USE Image_System;")
cursor.execute("GRANT SELECT ON OBJECT::Users TO common_user;")
cursor.execute("GRANT SELECT, INSERT, UPDATE ON OBJECT::Image TO common_user;")
cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::Comment TO common_user;")
cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::Tag TO common_user;")
cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::Tag_index TO common_user;")
cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::Favorite TO common_user;")



# 执行 SQL 语句
cursor.execute(sql_query)
#print(cursor.fetchall())

# 提交更改
#cn.commit()

# 关闭连接
cn.close()