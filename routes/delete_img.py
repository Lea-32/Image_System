from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint
import pyodbc
from db_config import config
delete_img_bp = Blueprint('delete_img', __name__)
@delete_img_bp.route('/delete_image/<int:img_id>', methods=['POST','GET'])
def delete_image(img_id):
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('login.login'))
        elif session['admin'] == False:
            return {'success': False}
        try:

            if session['admin'] == False:
                return {'success': False}
            connection_string = config(session['admin'])
            cn = pyodbc.connect(connection_string)
            cursor = cn.cursor()

            # Perform the deletion query
            cursor.execute("DELETE FROM Image WHERE img_id=?", img_id)
            cn.commit()

            cn.close()

            return {'success': True}
        except Exception as e:
            print('Error deleting image:', e)
            return {'success': False}
    else:
        return redirect(url_for('main.main'))

