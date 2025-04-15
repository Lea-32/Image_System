from apscheduler.schedulers.background import BackgroundScheduler
from utils.recommender import update_similarities, update_recommendations

def start_scheduler():
    """启动定时任务调度器"""
    scheduler = BackgroundScheduler()
    
    # 每天凌晨2点更新相似度矩阵
    scheduler.add_job(update_similarities, 'cron', hour=2)
    
    # 每6小时更新一次推荐列表
    scheduler.add_job(update_recommendations, 'interval', hours=6)
    
    # 启动调度器
    try:
        scheduler.start()
        print("定时任务调度器已启动")
    except Exception as e:
        print(f"启动定时任务调度器时出错: {str(e)}")

if __name__ == "__main__":
    start_scheduler() 