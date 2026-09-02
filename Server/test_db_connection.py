import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库配置
db_host = os.getenv('DB_HOST', 'localhost')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'root')
db_name = os.getenv('DB_NAME', 'exam_system')

print(f"数据库配置:")
print(f"  Host: {db_host}")
print(f"  User: {db_user}")
print(f"  Password: {'***' if db_password else '空'}")
print(f"  Database: {db_name}")
print("=" * 50)

try:
    # 尝试连接到MySQL服务器
    print("尝试连接到MySQL服务器...")
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password
    )
    
    if conn.is_connected():
        print("成功连接到MySQL服务器")
        cursor = conn.cursor()
        
        # 检查服务器版本
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MySQL版本: {version[0]}")
        
        # 检查数据库是否存在
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        if cursor.fetchone():
            print(f"数据库 {db_name} 已存在")
            # 尝试切换到指定数据库
            try:
                conn.database = db_name
                print(f"成功切换到数据库 {db_name}")
                
                # 检查users表是否存在
                cursor.execute("SHOW TABLES LIKE 'users'")
                if cursor.fetchone():
                    print("users表已存在")
                else:
                    print("users表不存在")
                    
            except Error as e:
                print(f"切换到数据库 {db_name} 失败: {e}")
        else:
            print(f"数据库 {db_name} 不存在")
            
        cursor.close()
        conn.close()
        
except Error as e:
    print(f"数据库连接失败: {e}")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误代码: {e.errno}")
    print(f"SQL状态: {e.sqlstate}")
