-- 删除现有的触发器（如果存在）
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'trg_FavoriteFolder_UpdateTime')
    DROP TRIGGER trg_FavoriteFolder_UpdateTime;
GO

-- 删除现有的表（如果存在）
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'ImageFavoriteFolder')
    DROP TABLE ImageFavoriteFolder;
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'FavoriteFolder')
    DROP TABLE FavoriteFolder;
GO

-- 创建收藏夹表
CREATE TABLE FavoriteFolder (
    folder_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    folder_name NVARCHAR(50) NOT NULL,
    folder_description NVARCHAR(200),
    folder_order INT DEFAULT 0,
    create_time DATETIME DEFAULT GETDATE(),
    update_time DATETIME DEFAULT GETDATE(),
    is_default BIT DEFAULT 0,  -- 是否为默认收藏夹
    is_deleted BIT DEFAULT 0,  -- 软删除标记
    last_used_time DATETIME DEFAULT GETDATE(),  -- 最后使用时间
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
GO

-- 创建图片收藏夹关联表
CREATE TABLE ImageFavoriteFolder (
    img_id INT NOT NULL,
    folder_id INT NOT NULL,
    img_order INT DEFAULT 0,
    add_time DATETIME DEFAULT GETDATE(),
    PRIMARY KEY (img_id, folder_id),
    FOREIGN KEY (img_id) REFERENCES Image(img_id) ON DELETE CASCADE,
    FOREIGN KEY (folder_id) REFERENCES FavoriteFolder(folder_id) ON DELETE CASCADE
);
GO

-- 为现有收藏添加默认收藏夹
INSERT INTO FavoriteFolder (user_id, folder_name, folder_description)
SELECT DISTINCT user_id, '默认收藏夹', '系统默认收藏夹'
FROM Favorite
WHERE NOT EXISTS (
    SELECT 1 FROM FavoriteFolder 
    WHERE FavoriteFolder.user_id = Favorite.user_id
);
GO

-- 将现有收藏移动到默认收藏夹
INSERT INTO ImageFavoriteFolder (img_id, folder_id)
SELECT f.img_id, ff.folder_id
FROM Favorite f
JOIN FavoriteFolder ff ON f.user_id = ff.user_id
WHERE ff.folder_name = '默认收藏夹'
AND NOT EXISTS (
    SELECT 1 FROM ImageFavoriteFolder 
    WHERE ImageFavoriteFolder.img_id = f.img_id
    AND ImageFavoriteFolder.folder_id = ff.folder_id
);
GO

-- 创建触发器以更新文件夹的更新时间
CREATE TRIGGER trg_FavoriteFolder_UpdateTime
ON FavoriteFolder
AFTER UPDATE
AS
BEGIN
    UPDATE FavoriteFolder
    SET update_time = GETDATE()
    FROM FavoriteFolder f
    INNER JOIN inserted i ON f.folder_id = i.folder_id
END;
GO 