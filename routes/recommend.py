from flask import Blueprint, render_template, session, redirect, url_for, flash
import pyodbc
from db_config import config
from routes.favorite import is_image_like

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend')
def recommend():
    """个性化推荐页面路由"""
    # 检查用户是否登录
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('login.login'))
    
    user_id = session['user_id']
    connection_string = config(session.get('admin', False))
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()
    
    try:
        # 获取推荐图片
        cursor.execute("""
            SELECT i.*, r.score
            FROM Image i
            JOIN UserRecommendations r ON i.img_id = r.img_id
            WHERE r.user_id = ?
            ORDER BY r.score DESC
        """, user_id)
        
        images = cursor.fetchall()
        
        # 获取每张图片的收藏状态
        image_favorited_status = {}
        for image in images:
            img_id = image[0]
            image_favorited_status[img_id] = is_image_like(user_id, img_id, cursor)
        
        return render_template('recommend.html', 
                             images=images,
                             image_favorited_status=image_favorited_status)
                             
    except Exception as e:
        print(f"获取推荐列表时出错: {str(e)}")
        flash('获取推荐列表时出错')
        return redirect(url_for('main.main'))
        
    finally:
        cn.close() 