-- 检查view_count列是否存在
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE Name = N'view_count' 
    AND Object_ID = Object_ID(N'Image')
)
BEGIN
    -- 添加view_count列
    ALTER TABLE Image
    ADD view_count INT NOT NULL DEFAULT 0;
END
GO

-- 更新现有记录的浏览数为0
UPDATE Image
SET view_count = 0
WHERE view_count IS NULL; 