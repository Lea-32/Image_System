
from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint,current_app
import pyodbc
from db_config import config
from routes.favorite import is_image_like
#创建蓝图对象
search_bp = Blueprint('search', __name__)

# 添加处理搜索的路由，支持GET和POST两种请求方式，调用search函数
@search_bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        # 获取用户输入的关键字
        search_content = request.args.get('search_content') # 用户输入的内容
        current_app.logger.info(search_content) # 写进日志

        user_id = session.get('user_id')  # 获取用户ID

        connection_string = config(session['admin'])
        cn = pyodbc.connect(connection_string)
        cursor = cn.cursor() # 创建数据库游标

        #首先搜索Image表
        cursor.execute("SELECT * from Image Where img_name LIKE ? OR img_description LIKE ?",
                       (f'%{search_content}%',f'%{search_content}%'))
        images = cursor.fetchall() # 返回符合条件的图像记录
        if images == []:#再搜索标签表，将与该标签有关的图像查询出来
            cursor.execute("SELECT * from Image Where img_id in (Select img_id from Tag_index,Tag Where Tag.tag_id=Tag_index.tag_id AND Tag_name LIKE ?)",
                       f'%{search_content}%')
            images = cursor.fetchall()


        # 获取每张图片的收藏状态
        image_favorited_status = {}
        if user_id:
            for image in images:
                img_id = image[0]
                image_favorited_status[img_id] = is_image_like(user_id, img_id, cursor)

        cn.close()
        search_result_info = f"{search_content}的搜索结果" if images else f"{search_content}的搜索结果为空"

        return render_template('search.html', images=images, user_id=user_id,
                               image_favorited_status=image_favorited_status,search_result_info=search_result_info)

    #return render_template('main.html', images=images, user_id=user_id, image_favorited_status=image_favorited_status)