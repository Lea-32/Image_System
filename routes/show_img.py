'''

=================单张图片的展示路由=================

'''

from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
import pyodbc
from db_config import config
import os
from datetime import datetime

#蓝图
img_bp = Blueprint('img', __name__)

def get_file_size(file_path):
    """获取文件大小"""
    try:
        size = os.path.getsize(file_path)
        return size
    except:
        return 0

def row_to_dict(row):
    """将pyodbc.Row对象转换为字典"""
    return {key: row[i] for i, key in enumerate([column[0] for column in row.cursor_description])}

# 添加处理img URL的路由
@img_bp.route('/img', methods=['GET', 'POST'])
@img_bp.route('/img/<int:img_id>', methods=['GET', 'POST'])
def img(img_id=None):
    if request.method == 'GET':
        # 检查img_id是否存在
        if img_id is None:
            flash('未指定图片ID')
            return redirect(url_for('main.main'))
            
        cursor = None
        cn = None
        try:
            # 检查用户是否登录
            if 'user_id' not in session:
                flash('请先登录')
                return redirect(url_for('login.login'))
                
            # 获取数据库连接
            try:
                connection_string = config(session.get('admin', False))
                cn = pyodbc.connect(connection_string)
                cursor = cn.cursor()
            except pyodbc.Error as e:
                print(f"数据库连接错误: {e}")
                flash('数据库连接失败，请稍后重试')
                return redirect(url_for('main.main'))

            # 获取图像详细信息
            try:
                cursor.execute("SELECT * from Image, Users WHERE img_id = ? AND Users.user_id=Image.user_id", img_id)
                image_row = cursor.fetchone()
                if not image_row:
                    flash('图片不存在')
                    return redirect(url_for('main.main'))
                
                # 将Row对象转换为字典
                image = row_to_dict(image_row)
                
                # 获取图片文件路径
                img_path = os.path.join('static/images/user_upload', f"{image['img_path']}.{image['img_format']}")
                # 获取文件大小并添加到image字典
                image['file_size'] = get_file_size(img_path)
                
            except pyodbc.Error as e:
                print(f"查询图片信息错误: {e}")
                flash('获取图片信息失败')
                return redirect(url_for('main.main'))
            
            # 更新浏览数
            try:
                cursor.execute("UPDATE Image SET view_count = view_count + 1 WHERE img_id = ?", img_id)
                cn.commit()
            except pyodbc.Error as e:
                print(f"更新浏览数错误: {e}")
                # 如果更新失败，不影响显示

            # 获取图像的评论
            try:
                cursor.execute("SELECT * FROM Comment, Users WHERE img_id = ? and Comment.user_id=Users.user_id", img_id)
                comments = cursor.fetchall()
            except pyodbc.Error as e:
                print(f"查询评论错误: {e}")
                comments = []  # 如果获取评论失败，使用空列表

            #获取图像的标签
            try:
                cursor.execute("SELECT * FROM Tag WHERE tag_id in (Select tag_id from Tag_index Where img_id = ?)", img_id)
                tags = cursor.fetchall()
            except pyodbc.Error as e:
                print(f"查询标签错误: {e}")
                tags = []  # 如果获取标签失败，使用空列表

            return render_template('img.html', image=image, comments=comments, tags=tags)

        except Exception as e:
            print(f"获取图像详细信息和评论时出错: {e}")
            flash('获取图片信息失败')
            return redirect(url_for('main.main'))

        finally:
            if cursor:
                cursor.close()
            if cn:
                cn.close()
                
    return redirect(url_for('main.main'))