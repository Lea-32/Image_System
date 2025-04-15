from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify
import pyodbc
from db_config import config
import os

delete_img_bp = Blueprint('delete_img', __name__)

@delete_img_bp.route('/delete_image/<int:img_id>', methods=['POST'])
def delete_image(img_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
        
    try:
        connection_string = config(session['admin'])
        cn = pyodbc.connect(connection_string)
        cursor = cn.cursor()

        # 首先检查图片是否存在且属于当前用户
        cursor.execute("""
            SELECT img_path, img_format, user_id 
            FROM Image 
            WHERE img_id = ?
        """, img_id)
        
        image_info = cursor.fetchone()
        
        if not image_info:
            return jsonify({'success': False, 'message': '图片不存在'})
            
        # 检查图片是否属于当前用户
        if image_info.user_id != session['user_id'] and not session['admin']:
            return jsonify({'success': False, 'message': '您没有权限删除此图片'})
            
        # 删除图片文件
        img_path = os.path.join('static/images/user_upload', f"{image_info.img_path}.{image_info.img_format}")
        if os.path.exists(img_path):
            os.remove(img_path)
            
        # 删除数据库记录
        cursor.execute("DELETE FROM Image WHERE img_id = ?", img_id)
        cn.commit()
        
        return jsonify({'success': True, 'message': '图片删除成功'})
        
    except Exception as e:
        print('Error deleting image:', e)
        return jsonify({'success': False, 'message': '删除失败，请稍后重试'})
    finally:
        if 'cn' in locals():
            cn.close()

