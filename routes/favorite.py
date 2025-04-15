from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify
import pyodbc
from db_config import config


# 检查图片是否已被当前用户收藏的函数
def is_image_like(user_id, img_id, cursor):
    cursor.execute("SELECT * FROM Favorite WHERE user_id=? AND img_id=?", user_id, img_id)
    existing_favorite = cursor.fetchone()
    return existing_favorite is not None


# 蓝图
favorite_bp = Blueprint('favorite', __name__)
like_bp = Blueprint('like', __name__)
check_like_bp = Blueprint('check_like', __name__)


@favorite_bp.route('/favorite', methods=['GET', 'POST'])
def favorite():
    if request.method == 'GET':
        user_id = session['user_id']
        folder_filter = request.args.get('folder')  # 获取收藏夹筛选参数

        connection_string = config(session['admin'])
        cn = pyodbc.connect(connection_string)
        cursor = cn.cursor()

        # 1. 获取用户的收藏夹列表
        cursor.execute("""
            SELECT folder_id, folder_name 
            FROM FavoriteFolder 
            WHERE user_id=? AND is_deleted=0 
            ORDER BY folder_order, create_time DESC
        """, user_id)
        folders = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

        # 2. 获取用户收藏的图片信息
        # 基础查询
        sql = """
            SELECT i.img_id, i.img_name, i.img_path, i.img_format, 
                   i.img_description, i.img_upload_time, i.view_count
            FROM Favorite f
            JOIN Image i ON f.img_id = i.img_id
            WHERE f.user_id = ?
        """
        params = [user_id]

        # 添加收藏夹筛选条件
        if folder_filter and folder_filter != 'all':
            sql += """
                AND EXISTS (
                    SELECT 1 FROM ImageFavoriteFolder iff
                    JOIN FavoriteFolder ff ON iff.folder_id = ff.folder_id
                    WHERE iff.img_id = i.img_id 
                    AND ff.folder_name = ?
                    AND ff.user_id = ?
                )
            """
            params.extend([folder_filter, user_id])

        cursor.execute(sql, params)
        imgs = [dict(zip([column[0] for column in cursor.description], row))
                for row in cursor.fetchall()]

        # 3. 获取每张图片的收藏夹信息(批量查询提高效率)
        if imgs:
            img_ids = [str(img['img_id']) for img in imgs]
            cursor.execute(f"""
                SELECT iff.img_id, ff.folder_name
                FROM ImageFavoriteFolder iff
                JOIN FavoriteFolder ff ON iff.folder_id = ff.folder_id
                WHERE iff.img_id IN ({','.join(['?'] * len(img_ids))})
                AND ff.user_id = ?
                ORDER BY iff.img_id, ff.folder_name
            """, *img_ids, user_id)

            # 构建图片ID到收藏夹的映射
            img_folders = {}
            for row in cursor.fetchall():
                img_id = row[0]
                if img_id not in img_folders:
                    img_folders[img_id] = []
                img_folders[img_id].append(row[1])

            # 将收藏夹信息添加到图片数据中
            for img in imgs:
                img['folder_names'] = img_folders.get(img['img_id'], [])

        cn.close()
        return render_template('favorite.html',
                               imgs=imgs,
                               folders=folders,
                               current_folder=folder_filter if folder_filter else 'all')
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

    try:
        # 检查用户是否已经收藏过这张图片
        existing_favorite = is_image_like(user_id, img_id, cursor)

        if existing_favorite:
            # 用户已经收藏过，取消收藏
            cursor.execute("DELETE FROM Favorite WHERE user_id=? AND img_id=?", user_id, img_id)
            cursor.execute("DELETE FROM ImageFavoriteFolder WHERE img_id=?", img_id)
            cn.commit()
            status = '取消收藏'
        else:
            # 获取或创建默认收藏夹
            cursor.execute("""
                SELECT folder_id FROM FavoriteFolder 
                WHERE user_id=? AND is_default=1
            """, user_id)
            default_folder = cursor.fetchone()

            if not default_folder:
                # 创建默认收藏夹
                cursor.execute("""
                    INSERT INTO FavoriteFolder (user_id, folder_name, is_default, create_time, update_time)
                    VALUES (?, '默认收藏', 1, GETDATE(), GETDATE())
                """, user_id)
                cn.commit()

                cursor.execute("SELECT @@IDENTITY")
                default_folder_id = cursor.fetchone()[0]
            else:
                default_folder_id = default_folder[0]

            # 添加收藏记录
            cursor.execute("SELECT count(*) from Favorite")
            favorite_num = cursor.fetchone()[0]
            cursor.execute("""
                INSERT INTO Favorite (favorite_id, user_id, img_id) 
                VALUES (?, ?, ?)
            """, favorite_num + 1, user_id, img_id)

            # 添加到默认收藏夹
            cursor.execute("""
                INSERT INTO ImageFavoriteFolder (img_id, folder_id, add_time)
                VALUES (?, ?, GETDATE())
            """, img_id, default_folder_id)

            cn.commit()
            status = '已收藏'

        return jsonify({'status': status})
    except Exception as e:
        cn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cn.close()


# 获取用户的收藏夹列表
@favorite_bp.route('/get_folders', methods=['GET'])
def get_folders():
    user_id = session['user_id']
    connection_string = config(session['admin'])
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    cursor.execute("""
        SELECT folder_id, folder_name 
        FROM FavoriteFolder 
        WHERE user_id=? AND is_deleted=0 
        ORDER BY folder_order, create_time DESC
    """, user_id)

    folders = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    cn.close()

    return jsonify(folders)


# 创建新的收藏夹
@favorite_bp.route('/create_folder', methods=['POST'])
def create_folder():
    user_id = session['user_id']
    data = request.get_json()
    folder_name = data.get('folder_name')

    if not folder_name:
        return jsonify({'success': False, 'message': '收藏夹名称不能为空'})

    connection_string = config(session['admin'])
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    try:
        # 获取当前最大的folder_order
        cursor.execute("SELECT MAX(folder_order) FROM FavoriteFolder WHERE user_id=?", user_id)
        max_order = cursor.fetchone()[0] or 0

        # 插入新收藏夹
        cursor.execute("""
            INSERT INTO FavoriteFolder (user_id, folder_name, folder_order, create_time, update_time)
            VALUES (?, ?, ?, GETDATE(), GETDATE())
        """, user_id, folder_name, max_order + 1)

        cn.commit()
        return jsonify({'success': True})
    except Exception as e:
        cn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cn.close()


# 将图片添加到收藏夹
@favorite_bp.route('/add_to_folders', methods=['POST'])
def add_to_folders():
    user_id = session['user_id']
    data = request.get_json()
    image_id = data.get('image_id')
    folder_ids = data.get('folder_ids', [])

    if not image_id or not folder_ids:
        return jsonify({'success': False, 'message': '参数错误'})

    connection_string = config(session['admin'])
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    try:
        # 检查是否是用户的图片和收藏夹
        cursor.execute("""
            SELECT COUNT(*) FROM FavoriteFolder 
            WHERE folder_id IN ({}) AND user_id=?
        """.format(','.join('?' * len(folder_ids))), *folder_ids, user_id)

        if cursor.fetchone()[0] != len(folder_ids):
            return jsonify({'success': False, 'message': '无效的收藏夹'})

        # 删除之前的关联
        cursor.execute("DELETE FROM ImageFavoriteFolder WHERE img_id=?", image_id)

        # 添加新的关联
        for folder_id in folder_ids:
            cursor.execute("""
                INSERT INTO ImageFavoriteFolder (img_id, folder_id, add_time)
                VALUES (?, ?, GETDATE())
            """, image_id, folder_id)

        cn.commit()
        return jsonify({'success': True})
    except Exception as e:
        cn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cn.close()
@favorite_bp.route('/get_images_by_folder/<int:folder_id>', methods=['GET'])
def get_images_by_folder(folder_id):
    user_id = session['user_id']
    connection_string = config(session['admin'])
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    try:
        # 获取该用户在该收藏夹下的所有图片
        cursor.execute("""
            SELECT Image.* 
            FROM ImageFavoriteFolder 
            JOIN Favorite ON ImageFavoriteFolder.img_id = Favorite.img_id
            JOIN Image ON Favorite.img_id = Image.img_id
            WHERE ImageFavoriteFolder.folder_id=? AND Favorite.user_id=?
        """, folder_id, user_id)

        imgs = cursor.fetchall()

        # 转为 JSON 可序列化对象
        result = []
        for row in imgs:
            result.append({
                'img_id': row.img_id,
                'img_name': row.img_name,
                'img_path': row.img_path,
                'img_format': row.img_format,
                'img_label': row.img_label
            })

        return jsonify({'success': True, 'images': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cn.close()

@favorite_bp.route('/check_image_folders/<int:img_id>', methods=['GET'])
def check_image_folders(img_id):
    user_id = session['user_id']
    connection_string = config(session['admin'])
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()

    try:
        # 获取图片所在的所有收藏夹ID
        cursor.execute("""
            SELECT DISTINCT f.folder_id
            FROM ImageFavoriteFolder iff
            JOIN FavoriteFolder f ON iff.folder_id = f.folder_id
            WHERE iff.img_id = ? AND f.user_id = ?
        """, img_id, user_id)
        
        folder_ids = [row[0] for row in cursor.fetchall()]
        return jsonify({'success': True, 'folder_ids': folder_ids})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cn.close()
