'''

=================单张图片的展示路由=================

'''

from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
import pyodbc
from db_config import config

#蓝图
img_bp = Blueprint('img', __name__)

# 添加处理img URL的路由
@img_bp.route('/img', methods=['GET', 'POST'])
@img_bp.route('/img/<int:img_id>', methods=['GET', 'POST'])
def img(img_id=None):
    if request.method == 'GET':
        cursor = None
        cn = None
        try:
            connection_string = config(session['admin'])
            cn = pyodbc.connect(connection_string)
            cursor = cn.cursor()

            # 获取图像详细信息
            cursor.execute("SELECT * from Image, Users WHERE img_id = ? AND Users.user_id=Image.user_id", img_id)
            image = cursor.fetchone()

            # 获取与图像关联的用户名称
            #print(image)
            #cursor.execute("SELECT user_name from Users WHERE user_id = ?", image[6])
            #user_name = cursor.fetchone()[0]

            # 获取图像的评论
            cursor.execute("SELECT * FROM Comment, Users WHERE img_id = ? and Comment.user_id=Users.user_id", img_id)
            comments = cursor.fetchall()

            #获取图像的标签
            cursor.execute("SELECT * FROM Tag WHERE tag_id in (Select tag_id from Tag_index Where img_id = ?)", img_id)
            tags = cursor.fetchall()
            #print(tags)

            return render_template('img.html', image=image, comments=comments,tags=tags)

        except Exception as e:
            print(f"获取图像详细信息和评论时出错: {e}")
            #return render_template('error.html', error_message="获取图像详细信息和评论失败")


        finally:
            if cursor:
                cursor.close()
            if cn:
                cn.close()