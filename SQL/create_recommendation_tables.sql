USE [image]
GO

-- 创建用户相似度表
CREATE TABLE [dbo].[UserSimilarity](
    [user_id1] [int] NOT NULL,
    [user_id2] [int] NOT NULL,
    [similarity_score] [float] NOT NULL,
    [update_time] [datetime] NOT NULL,
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES Users(user_id),
    FOREIGN KEY (user_id2) REFERENCES Users(user_id)
)
GO

-- 创建图片相似度表
CREATE TABLE [dbo].[ImageSimilarity](
    [img_id1] [int] NOT NULL,
    [img_id2] [int] NOT NULL,
    [similarity_score] [float] NOT NULL,
    [update_time] [datetime] NOT NULL,
    PRIMARY KEY (img_id1, img_id2),
    FOREIGN KEY (img_id1) REFERENCES Image(img_id),
    FOREIGN KEY (img_id2) REFERENCES Image(img_id)
)
GO

-- 创建用户推荐表
CREATE TABLE [dbo].[UserRecommendations](
    [user_id] [int] NOT NULL,
    [img_id] [int] NOT NULL,
    [score] [float] NOT NULL,
    [update_time] [datetime] NOT NULL,
    PRIMARY KEY (user_id, img_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (img_id) REFERENCES Image(img_id)
)
GO 