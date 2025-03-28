from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
import pyodbc
from db_config import config
from datetime import datetime
#蓝图
add_comment_bp = Blueprint('add_comment', __name__)
# 添加评论路由
@add_comment_bp.route('/img/add_comment', methods=['POST'])
def add_comment():
    if 'user_id' not in session:  # 用户未登录，重定向到登录页面
        return redirect('/login')

    user_id = session['user_id']
    img_id = request.form.get('imgId')
    comment_text = request.form.get('commentText')
    comment_time = datetime.now().strftime('%Y-%m-%d')

    try:
        connection_string = config(session['admin'])
        cn = pyodbc.connect(connection_string)
        cursor = cn.cursor()

        # 查询当前评论数量
        cursor.execute("SELECT count(*) FROM Comment")
        comment_num = cursor.fetchone()[0]

        cursor.execute("INSERT INTO Comment (comment_id, comment_content, comment_release_time, user_id, img_id) VALUES (?, ?, ?, ?, ?)",
                       (comment_num+1, comment_text, comment_time, user_id, img_id))
        cn.commit()

        cursor.close()
        cn.close()
        return redirect(url_for('img.img', img_id=img_id))

    except Exception as e:  # 处理数据库操作中的异常
        print(f"Error adding comment: {e}")
        return render_template('error.html', error_message="Failed to add comment")

# 回复评论的路由
@add_comment_bp.route('/img/reply_comment', methods=['POST'])
def reply_comment():
    if 'user_id' not in session:  # 用户未登录，重定向到登录页面
        return redirect('/login')

    user_id = session['user_id']
    img_id = request.form.get('imgId')
    parent_comment_id = request.form.get('parentCommentId')  # 获取父评论的ID
    reply_text = request.form.get('replyText')
    reply_time = datetime.now().strftime('%Y-%m-%d')

    try:
        connection_string = config(session['admin'])
        cn = pyodbc.connect(connection_string)
        cursor = cn.cursor()

        '''# 查询当前评论数量
        cursor.execute("SELECT count(*) FROM Comment")
        comment_num = cursor.fetchone()[0]

        # 插入回复评论
        cursor.execute("INSERT INTO Comment (comment_id, comment_content, comment_release_time, user_id, img_id, parent_comment_id) VALUES (?, ?, ?, ?, ?, ?)",
                       (comment_num + 1, reply_text, reply_time, user_id, img_id, parent_comment_id))
        cn.commit()

        cursor.close()
        cn.close()'''
        return redirect(url_for('img.img', img_id=img_id))

    except Exception as e:  # 处理数据库操作中的异常
        print(f"Error replying to comment: {e}")