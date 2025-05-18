import pyodbc
from db_config import config
import os
import sys

def execute_sql_script(script_path, admin=True):
    """
    执行SQL脚本文件
    
    参数:
        script_path: SQL脚本文件的路径
        admin: 是否使用管理员权限连接数据库
    """
    # 获取数据库连接字符串
    connection_string = config(admin)
    
    # 连接到数据库
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        print(f"正在执行SQL脚本: {script_path}")
        
        # 读取SQL脚本文件
        with open(script_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # 分割SQL脚本为多个批处理
        batches = sql_script.split('GO')
        
        # 执行每个批处理
        for i, batch in enumerate(batches):
            if batch.strip():  # 忽略空批处理
                print(f"执行批处理 {i+1}/{len(batches)}")
                try:
                    cursor.execute(batch)
                    conn.commit()
                except Exception as e:
                    print(f"批处理 {i+1} 执行出错: {str(e)}")
                    conn.rollback()
                    raise
        
        print("SQL脚本执行成功！")
        
    except Exception as e:
        print(f"执行SQL脚本时出错: {str(e)}")
        
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    # 获取脚本路径
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
    else:
        script_path = 'SQL/create_favorite_folders.sql'
    
    # 检查文件是否存在
    if not os.path.exists(script_path):
        print(f"错误: 文件 {script_path} 不存在")
        return
    
    # 执行脚本
    execute_sql_script(script_path, admin=True)

if __name__ == "__main__":
    main() 