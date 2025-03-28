from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify
import pyodbc
from db_config import config

# 检查图片是否已被当前用户收藏的函数
def is_image_like(user_id, img_id, cursor):
    cursor.execute("SELECT * FROM Favorite WHERE user_id=? AND img_id=?", user_id, img_id)
    existing_favorite = cursor.fetchone()
    return existing_favorite is not None


#蓝图
favorite_bp = Blueprint('favorite', __name__)
like_bp = Blueprint('like', __name__)
check_like_bp = Blueprint('check_like', __name__)

# 收藏路由
@favorite_bp.route('/favorite', methods=['GET', 'POST'])
def favorite():
    if request.method == 'GET':
        user_id = session['user_id']
        connection_string = config(session['admin'])
        cn = pyodbc.connect(connection_string)
        cursor = cn.cursor()
        # 使用JOIN语句一次性获取用户收藏的图片信息
        cursor.execute("""
                        SELECT Image.* 
                        FROM Favorite
                        JOIN Image ON Favorite.img_id = Image.img_id
                        WHERE Favorite.user_id=?
                    """, user_id)
        imgs = cursor.fetchall()
        cn.close()

        return render_template('favorite.html', imgs=imgs)

'''    connection_string = config('root')
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    cursor.execute("")
     = cursor.fetchall()
     #cursor.close()
    cn.close()'''

# 检查用户是否已收藏某张图片
@check_like_bp.route('/check_like/<int:img_id>', methods=['GET'])
def check_like(img_id):
    user_id = session['user_id']  # 假设用户 ID 存在 session 中

    connection_string = config(session['admin'])
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    # 查询是否已收藏
    existing_favorite = is_image_like(user_id, img_id, cursor)

    cn.close()

    return jsonify({'favorited': existing_favorite})

# 收藏图片路由
@like_bp.route('/like/<int:img_id>', methods=['POST'])
def like(img_id):
    user_id = session['user_id']

    connection_string = config(session['admin'])
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    # 检查用户是否已经收藏过这张图片
    existing_favorite = is_image_like(user_id, img_id, cursor)

    if existing_favorite:
        # 用户已经收藏过，取消收藏
        cursor.execute("DELETE FROM favorite WHERE user_id=? AND img_id=?", user_id, img_id)
        cn.commit()
        status = '取消收藏'
    else:
        cursor.execute("SELECT count(*) from Favorite")
        favorite_num = cursor.fetchone()[0]
        # 用户还未收藏，添加新的收藏记录
        cursor.execute("INSERT INTO Favorite (favorite_id, user_id, img_id) VALUES (?, ?, ?)", favorite_num+1, user_id, img_id)
        cn.commit()
        status = '已收藏'
    cn.close()
    return jsonify({'status': status})