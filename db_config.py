# 设置数据库连接参数
def config(is_admin):
    driver = 'ODBC Driver 17 for SQL Server'#'SQL Server'
    server = 'localhost'
    port = '1433'
    database = 'image'

    if is_admin:
        # 管理员账号
        username = 'sa'
        password = '123456'

    else:#普通用户账号
        username = 'user'
        password = '123456'

    connection_string = f'DRIVER={driver};SERVER={server}; PORT={port}; DATABASE={database}; UID={username}; PWD={password};Trusted_Connection=no;'
    print(connection_string)
    return connection_string
