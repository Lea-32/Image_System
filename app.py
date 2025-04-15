from flask import Flask
#路由函数
from routes.login import register_bp, login_bp, check_login_bp, logout_bp
from routes.main import main_bp
from routes.show_img import img_bp
from routes.upload import upload_bp
from routes.favorite import favorite_bp,like_bp, check_like_bp
from routes.comment import add_comment_bp
from routes.search import search_bp
from routes.delete_img import delete_img_bp
from routes.recommend import recommend_bp
from utils.scheduler import start_scheduler

app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'key'  # 用于 session 的密钥

#注册蓝图
app.register_blueprint(main_bp)
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(check_login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(img_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(favorite_bp)
app.register_blueprint(check_like_bp)
app.register_blueprint(like_bp)

app.register_blueprint(add_comment_bp)

app.register_blueprint(search_bp)

app.register_blueprint(delete_img_bp)

app.register_blueprint(recommend_bp)

if __name__ == '__main__':
    # 启动定时任务
    start_scheduler()
    # 启动应用
    app.run(debug=True)
