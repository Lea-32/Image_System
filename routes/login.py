from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify
import pyodbc
from db_config import config

#蓝图
#main_bp = Blueprint('main', __name__)
register_bp = Blueprint('register', __name__)
login_bp = Blueprint('login', __name__)
check_login_bp = Blueprint('check_login', __name__)

@register_bp.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['Name']
        password = request.form['Password']
        confirm_password = request.form['ConfirmPassword']
        email = request.form['Email']

        if password == confirm_password:
            connection_string = config(True)
            cn = pyodbc.connect(connection_string)
            cursor = cn.cursor()

            #查询当前用户数量
            cursor.execute("SELECT count(*) from Users")
            user_num = cursor.fetchone()[0]
            #插入用户信息
            cursor.execute("INSERT INTO Users (user_id, user_name, user_password, user_email,admin) VALUES (?, ?, ?, ?,?)", (user_num+1, username, password, email,False))

            cn.commit()
            cn.close()

            flash('Registration successful. Please log in.')
            return redirect(url_for('login.login'))
        else:
            flash('Password and confirm password do not match.')
            return render_template('Login_Registration.html')

    except Exception as e:
        flash(f'Error during registration: {str(e)}')
        print(f'Error during registration: {str(e)}')
        return render_template('Login_Registration.html')

# 登录页面路由
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['Name']
        password = request.form['Password']
        # 连接数据库
        connection_string = config(True)
        cn = pyodbc.connect(connection_string)
        cursor = cn.cursor()

        # 查询数据库中是否有匹配的用户
        query = "SELECT * FROM Users WHERE user_name = ? AND user_password = ?"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        # 关闭数据库连接
        cursor.close()
        cn.close()

        if user:# 如果用户存在，将其信息存储在 session 中
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['admin'] = user[4]
            return redirect(url_for('main.main'))
        else:# 如果用户不存在，显示错误信息
            #error = 'Invalid username or password. Please try again.'
            error = '用户名或密码无效，请重试。'
            flash(error, 'danger')  # 'danger' 是 Bootstrap 提示框的危险/错误类别
            return render_template('Login_Registration.html', login_failed=True)
    else:
        # 处理 GET 请求，可能是直接访问登录页面的情况
        # 可以在这里返回一个渲染登录页面的响应
        return render_template('Login_Registration.html')


# 添加用于检查登录状态的路由
@check_login_bp.route('/check_login', methods=['GET'])
def check_login():
    # 检查用户是否已登录
    if 'user_id' in session:
        return jsonify(logged_in=True)
    else:
        return jsonify(logged_in=False)

logout_bp = Blueprint('logout', __name__)


@logout_bp.route('/logout', methods=['GET'])
def logout():
    # 清除 session 中的用户信息
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('admin', None)

    # 重定向到主页
    return redirect(url_for('main.main'))