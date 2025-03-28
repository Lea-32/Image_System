'''

=================主界面=================

'''


from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
import pyodbc
from db_config import config
from routes.favorite import is_image_like

#蓝图
main_bp = Blueprint('main', __name__)

# 添加处理根URL的路由
@main_bp.route('/')
def main():
    session.pop('upload_redirect', None)
    connection_string = config(True)
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    cursor.execute("SELECT * from Image")
    images = cursor.fetchall()

    user_id = session.get('user_id')  # 获取用户ID

    # 获取每张图片的收藏状态
    image_favorited_status = {}
    if user_id:
        for image in images:
            img_id = image[0]
            image_favorited_status[img_id] = is_image_like(user_id, img_id, cursor)

    cn.close()

    return render_template('main.html', images=images, user_id=user_id, image_favorited_status=image_favorited_status)