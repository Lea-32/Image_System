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

@main_bp.route('/my_images')
def my_images():
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login.login'))
        
    user_id = session['user_id']
    connection_string = config(session.get('admin', False))
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    # 获取用户上传的所有图片
    cursor.execute("""
        SELECT img_id, img_name, img_path, img_format, img_upload_time
        FROM Image 
        WHERE user_id = ?
        ORDER BY img_upload_time DESC
    """, user_id)
    
    # 将查询结果转换为字典列表
    columns = [column[0] for column in cursor.description]
    images = []
    for row in cursor.fetchall():
        image_dict = dict(zip(columns, row))
        images.append(image_dict)
    
    # 获取每张图片的收藏状态
    image_favorited_status = {}
    for image in images:
        img_id = image['img_id']
        image_favorited_status[img_id] = is_image_like(user_id, img_id, cursor)

    cn.close()
    
    return render_template('my_images.html', 
                         images=images,
                         image_favorited_status=image_favorited_status)