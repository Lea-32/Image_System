import pyodbc
from db_config import config
from datetime import datetime

def calculate_user_similarity(user_id1, user_id2, cursor):
    """计算两个用户之间的相似度"""
    # 获取两个用户的浏览历史
    cursor.execute("""
        SELECT img_id, user_id FROM View_History 
        WHERE user_id IN (?, ?)
    """, user_id1, user_id2)
    
    history = cursor.fetchall()
    user1_history = set(h[0] for h in history if h[1] == user_id1)
    user2_history = set(h[0] for h in history if h[1] == user_id2)
    
    # 获取两个用户的收藏记录
    cursor.execute("""
        SELECT img_id, user_id FROM Favorite 
        WHERE user_id IN (?, ?)
    """, user_id1, user_id2)
    
    favorites = cursor.fetchall()
    user1_favorites = set(f[0] for f in favorites if f[1] == user_id1)
    user2_favorites = set(f[0] for f in favorites if f[1] == user_id2)
    
    # 计算Jaccard相似度
    history_similarity = 0
    if user1_history or user2_history:
        history_intersection = len(user1_history & user2_history)
        history_union = len(user1_history | user2_history)
        history_similarity = history_intersection / history_union if history_union > 0 else 0
    
    favorite_similarity = 0
    if user1_favorites or user2_favorites:
        favorites_intersection = len(user1_favorites & user2_favorites)
        favorites_union = len(user1_favorites | user2_favorites)
        favorite_similarity = favorites_intersection / favorites_union if favorites_union > 0 else 0
    
    # 综合相似度（浏览历史权重0.3，收藏记录权重0.7）
    return 0.3 * history_similarity + 0.7 * favorite_similarity

def calculate_image_similarity(img_id1, img_id2, cursor):
    """计算两张图片之间的相似度"""
    # 获取两张图片的标签
    cursor.execute("""
        SELECT tag_id, img_id FROM Tag_index 
        WHERE img_id IN (?, ?)
    """, img_id1, img_id2)
    
    tags = cursor.fetchall()
    img1_tags = set(t[0] for t in tags if t[1] == img_id1)
    img2_tags = set(t[0] for t in tags if t[1] == img_id2)
    
    # 计算标签相似度
    if not img1_tags or not img2_tags:
        return 0
        
    tag_intersection = len(img1_tags & img2_tags)
    tag_union = len(img1_tags | img2_tags)
    
    return tag_intersection / tag_union

def update_similarities():
    """更新用户相似度和图片相似度矩阵"""
    print("开始更新相似度矩阵...")
    connection_string = config(True)
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()
    
    try:
        # 更新用户相似度
        cursor.execute("SELECT user_id FROM Users")
        users = [user[0] for user in cursor.fetchall()]
        
        for i, user_id1 in enumerate(users):
            for user_id2 in users[i+1:]:
                similarity = calculate_user_similarity(user_id1, user_id2, cursor)
                
                cursor.execute("""
                    MERGE INTO UserSimilarity AS target
                    USING (VALUES (?, ?, ?, ?)) AS source (user_id1, user_id2, similarity_score, update_time)
                    ON (target.user_id1 = source.user_id1 AND target.user_id2 = source.user_id2)
                    WHEN MATCHED THEN
                        UPDATE SET 
                            similarity_score = source.similarity_score,
                            update_time = source.update_time
                    WHEN NOT MATCHED THEN
                        INSERT (user_id1, user_id2, similarity_score, update_time)
                        VALUES (source.user_id1, source.user_id2, source.similarity_score, source.update_time);
                """, user_id1, user_id2, similarity, datetime.now())
                
                # 同时插入反向关系
                cursor.execute("""
                    MERGE INTO UserSimilarity AS target
                    USING (VALUES (?, ?, ?, ?)) AS source (user_id1, user_id2, similarity_score, update_time)
                    ON (target.user_id1 = source.user_id1 AND target.user_id2 = source.user_id2)
                    WHEN MATCHED THEN
                        UPDATE SET 
                            similarity_score = source.similarity_score,
                            update_time = source.update_time
                    WHEN NOT MATCHED THEN
                        INSERT (user_id1, user_id2, similarity_score, update_time)
                        VALUES (source.user_id1, source.user_id2, source.similarity_score, source.update_time);
                """, user_id2, user_id1, similarity, datetime.now())
        
        # 更新图片相似度
        cursor.execute("SELECT img_id FROM Image")
        images = [img[0] for img in cursor.fetchall()]
        
        for i, img_id1 in enumerate(images):
            for img_id2 in images[i+1:]:
                similarity = calculate_image_similarity(img_id1, img_id2, cursor)
                
                cursor.execute("""
                    MERGE INTO ImageSimilarity AS target
                    USING (VALUES (?, ?, ?, ?)) AS source (img_id1, img_id2, similarity_score, update_time)
                    ON (target.img_id1 = source.img_id1 AND target.img_id2 = source.img_id2)
                    WHEN MATCHED THEN
                        UPDATE SET 
                            similarity_score = source.similarity_score,
                            update_time = source.update_time
                    WHEN NOT MATCHED THEN
                        INSERT (img_id1, img_id2, similarity_score, update_time)
                        VALUES (source.img_id1, source.img_id2, source.similarity_score, source.update_time);
                """, img_id1, img_id2, similarity, datetime.now())
                
                # 同时插入反向关系
                cursor.execute("""
                    MERGE INTO ImageSimilarity AS target
                    USING (VALUES (?, ?, ?, ?)) AS source (img_id1, img_id2, similarity_score, update_time)
                    ON (target.img_id1 = source.img_id1 AND target.img_id2 = source.img_id2)
                    WHEN MATCHED THEN
                        UPDATE SET 
                            similarity_score = source.similarity_score,
                            update_time = source.update_time
                    WHEN NOT MATCHED THEN
                        INSERT (img_id1, img_id2, similarity_score, update_time)
                        VALUES (source.img_id1, source.img_id2, source.similarity_score, source.update_time);
                """, img_id2, img_id1, similarity, datetime.now())
        
        cn.commit()
        print("相似度矩阵更新完成")
        
    except Exception as e:
        print(f"更新相似度矩阵时出错: {str(e)}")
        cn.rollback()
    finally:
        cn.close()

def update_recommendations():
    """更新用户推荐列表"""
    print("开始更新推荐列表...")
    connection_string = config(True)
    cn = pyodbc.connect(connection_string)
    cursor = cn.cursor()
    
    try:
        # 获取所有用户
        cursor.execute("SELECT user_id FROM Users")
        users = cursor.fetchall()
        
        for user in users:
            user_id = user[0]
            
            # 获取相似用户
            cursor.execute("""
                SELECT user_id2, similarity_score 
                FROM UserSimilarity 
                WHERE user_id1 = ?
                ORDER BY similarity_score DESC
            """, user_id)
            
            similar_users = cursor.fetchall()
            
            # 获取用户已浏览和收藏的图片
            cursor.execute("""
                SELECT DISTINCT img_id 
                FROM (
                    SELECT img_id FROM View_History WHERE user_id = ?
                    UNION
                    SELECT img_id FROM Favorite WHERE user_id = ?
                ) AS user_images
            """, user_id, user_id)
            
            viewed_images = set(img[0] for img in cursor.fetchall())
            
            # 生成推荐
            recommendations = {}
            
            # 基于相似用户的推荐
            for similar_user, user_similarity in similar_users:
                cursor.execute("""
                    SELECT DISTINCT i.img_id, i.view_count
                    FROM Image i
                    LEFT JOIN Favorite f ON i.img_id = f.img_id
                    WHERE f.user_id = ?
                """, similar_user)
                
                for img_id, view_count in cursor.fetchall():
                    if img_id not in viewed_images:
                        base_score = user_similarity * 0.7  # 用户相似度权重
                        popularity_score = min(view_count / 1000, 1) * 0.3  # 热度权重
                        
                        if img_id in recommendations:
                            recommendations[img_id] += base_score + popularity_score
                        else:
                            recommendations[img_id] = base_score + popularity_score
            
            # 基于图片相似度的推荐
            if viewed_images:
                for viewed_img in viewed_images:
                    cursor.execute("""
                        SELECT img_id2, similarity_score
                        FROM ImageSimilarity
                        WHERE img_id1 = ?
                        ORDER BY similarity_score DESC
                    """, viewed_img)
                    
                    for similar_img, img_similarity in cursor.fetchall():
                        if similar_img not in viewed_images:
                            score = img_similarity * 0.3  # 图片相似度权重
                            
                            if similar_img in recommendations:
                                recommendations[similar_img] += score
                            else:
                                recommendations[similar_img] = score
            
            # 更新推荐表
            cursor.execute("DELETE FROM UserRecommendations WHERE user_id = ?", user_id)
            
            # 插入新的推荐
            for img_id, score in sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:20]:
                cursor.execute("""
                    INSERT INTO UserRecommendations (user_id, img_id, score, update_time)
                    VALUES (?, ?, ?, ?)
                """, user_id, img_id, score, datetime.now())
        
        cn.commit()
        print("推荐列表更新完成")
        
    except Exception as e:
        print(f"更新推荐列表时出错: {str(e)}")
        cn.rollback()
    finally:
        cn.close()

if __name__ == "__main__":
    # 测试更新
    update_similarities()
    update_recommendations() 