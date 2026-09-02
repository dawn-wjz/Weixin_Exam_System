import mysql.connector  # 导入mysql.connector库，用于数据库连接
from mysql.connector import Error  # 从mysql.connector中导入Error类，用于捕获数据库错误
import os  # 导入os模块，用于操作环境变量和系统功能
from dotenv import load_dotenv  # 从dotenv库导入load_dotenv函数，用于加载环境变量配置

# 加载环境变量
load_dotenv()  # 加载.env文件中的环境变量配置

# # 获取数据库配置
# db_host = os.getenv('DB_HOST', 'localhost')  # 从环境变量获取数据库主机地址，默认localhost
# db_user = os.getenv('DB_USER', 'root')  # 从环境变量获取数据库用户名，默认root
# db_password = os.getenv('DB_PASSWORD', 'root')  # 从环境变量获取数据库密码，默认root
# db_name = os.getenv('DB_NAME', 'exam_system')  # 从环境变量获取数据库名称，默认exam_system

class Database:  # 定义Database数据库操作类
    def __init__(self):  # 类的构造函数
        self.host = os.getenv('DB_HOST', 'localhost')  # 从环境变量获取数据库主机地址，默认localhost
        self.user = os.getenv('DB_USER', 'root')  # 从环境变量获取数据库用户名，默认root
        self.password = os.getenv('DB_PASSWORD', 'root')  # 从环境变量获取数据库密码，默认root
        self.database = os.getenv('DB_NAME', 'exam_system')  # 从环境变量获取数据库名称，默认exam_system
        self.connection = None  # 初始化数据库连接对象
        self.cursor = None  # 初始化数据库游标对象

    def connect(self):  # 定义数据库连接方法
        """建立数据库连接"""
        try:  # 尝试执行代码块
            print(f"尝试连接数据库: host={self.host}, user={self.user}, password={self.password}, database={self.database}")  # 打印数据库连接参数
            self.connection = mysql.connector.connect(  # 创建数据库连接
                host=self.host,  # 设置数据库主机地址
                user=self.user,  # 设置数据库用户名
                password=self.password,  # 设置数据库密码
                database=self.database  # 设置数据库名称
            )
            self.cursor = self.connection.cursor(dictionary=True)  # 创建字典格式结果的游标
            print("数据库连接成功！")  # 打印连接成功信息
            return True  # 返回连接成功状态
        except Error as e:  # 捕获数据库连接错误
            print(f"连接数据库失败: {e}")  # 打印错误信息
            print(f"错误代码: {e.errno}")  # 打印错误代码
            print(f"SQL状态: {e.sqlstate}")  # 打印SQL状态码
            return False  # 返回连接失败状态

    def disconnect(self):  # 定义关闭数据库连接方法
        """关闭数据库连接"""
        if self.cursor:  # 如果游标存在
            self.cursor.close()  # 关闭游标
        if self.connection and self.connection.is_connected():  # 如果连接存在且已连接
            self.connection.close()  # 关闭数据库连接

    def execute_query(self, query, params=None):  # 定义执行查询语句方法（SELECT）
        """执行查询语句（SELECT）"""
        try:  # 尝试执行代码块
            if not self.connection or not self.connection.is_connected():  # 如果连接不存在或已断开
                if not self.connect():  # 尝试重新连接数据库
                    return None  # 连接失败则返回None

            self.cursor.execute(query, params or ())  # 执行SQL查询语句
            return self.cursor.fetchall()  # 返回所有查询结果
        except Error as e:  # 捕获执行错误
            print(f"执行查询失败: {e}")  # 打印错误信息
            return None  # 返回None表示失败

    def execute_non_query(self, query, params=None):  # 定义执行非查询语句方法（INSERT, UPDATE, DELETE等）
        """执行非查询语句（INSERT, UPDATE, DELETE等）"""
        try:  # 尝试执行代码块
            if not self.connection or not self.connection.is_connected():  # 如果连接不存在或已断开
                print("数据库连接不存在或已断开，尝试重新连接...")  # 打印重连提示
                if not self.connect():  # 尝试重新连接数据库
                    print("数据库重连失败")  # 打印重连失败信息
                    return False, None  # 返回失败状态和None

            print(f"执行SQL: {query}")  # 打印执行的SQL语句
            print(f"参数: {params}")  # 打印SQL参数
            self.cursor.execute(query, params or ())  # 执行SQL非查询语句
            self.connection.commit()  # 提交事务
            print(f"执行成功，最后插入ID: {self.cursor.lastrowid}")  # 打印执行成功信息和最后插入的ID
            return True, self.cursor.lastrowid  # 返回操作结果和最后插入的ID
        except Error as e:  # 捕获执行错误
            print(f"执行非查询语句失败: {e}")  # 打印错误信息
            print(f"错误类型: {type(e).__name__}")  # 打印错误类型
            if self.connection:  # 如果连接存在
                self.connection.rollback()  # 回滚事务
            return False, None  # 返回失败状态和None

    # 用户相关操作
    def create_user(self, username, password, name, avatar_url, gender, birthday, role, class_name=None):  # 定义创建新用户方法
        """创建新用户"""
        query = """  # 定义插入用户的SQL语句
        INSERT INTO users (username, password, name, avatar_url, gender, birthday, role, class_name)  # SQL语句主体
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)  # 占位符参数
        """
        params = (username, password, name, avatar_url, gender, birthday, role, class_name)  # 组装SQL参数
        return self.execute_non_query(query, params)  # 调用execute_non_query执行SQL

    def get_user_by_username(self, username):  # 定义根据用户名获取用户信息方法
        """根据用户名获取用户信息"""
        query = "SELECT * FROM users WHERE username = %s"  # 定义查询用户的SQL语句
        result = self.execute_query(query, (username,))  # 执行查询并获取结果
        return result[0] if result else None  # 如果结果存在则返回第一条，否则返回None

    def get_user_by_id(self, user_id):  # 定义根据用户ID获取用户信息方法
        """根据用户ID获取用户信息"""
        query = "SELECT * FROM users WHERE id = %s"  # 定义查询用户的SQL语句
        result = self.execute_query(query, (user_id,))  # 执行查询并获取结果
        return result[0] if result else None  # 如果结果存在则返回第一条，否则返回None

    def verify_user_login(self, username, password):  # 定义验证用户登录方法
        """验证用户登录"""
        query = "SELECT * FROM users WHERE username = %s AND password = %s"  # 定义登录验证的SQL语句
        result = self.execute_query(query, (username, password))  # 执行查询并获取结果
        return result[0] if result else None  # 如果结果存在则返回第一条，否则返回None

    def update_user(self, user_id, name=None, avatar_url=None, gender=None, birthday=None, role=None, class_name=None):  # 定义更新用户信息方法
        """更新用户信息"""
        # 构建更新字段
        update_fields = []  # 初始化更新字段列表
        params = []  # 初始化参数列表

        if name:  # 如果提供了name参数
            update_fields.append("name = %s")  # 添加name更新字段到列表
            params.append(name)  # 添加name参数到列表
        if avatar_url:  # 如果提供了avatar_url参数
            update_fields.append("avatar_url = %s")  # 添加avatar_url更新字段到列表
            params.append(avatar_url)  # 添加avatar_url参数到列表
        if gender:  # 如果提供了gender参数
            update_fields.append("gender = %s")  # 添加gender更新字段到列表
            params.append(gender)  # 添加gender参数到列表
        if birthday:  # 如果提供了birthday参数
            update_fields.append("birthday = %s")  # 添加birthday更新字段到列表
            params.append(birthday)  # 添加birthday参数到列表
        if role:  # 如果提供了role参数
            update_fields.append("role = %s")  # 添加role更新字段到列表
            params.append(role)  # 添加role参数到列表
        if class_name:  # 如果提供了class_name参数
            update_fields.append("class_name = %s")  # 添加class_name更新字段到列表
            params.append(class_name)  # 添加class_name参数到列表

        if not update_fields:  # 如果没有需要更新的字段
            return False, None  # 没有需要更新的字段

        params.append(user_id)  # 添加用户ID到参数列表
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"  # 组装更新用户的SQL语句

        return self.execute_non_query(query, params)  # 调用execute_non_query执行SQL

    def update_password(self, user_id, new_password):  # 定义更新用户密码方法
        """更新用户密码"""
        query = "UPDATE users SET password = %s WHERE id = %s"  # 定义更新密码的SQL语句
        return self.execute_non_query(query, (new_password, user_id))  # 调用execute_non_query执行SQL

    def delete_user(self, user_id):  # 定义删除用户方法
        """删除用户"""
        query = "DELETE FROM users WHERE id = %s"  # 定义删除用户的SQL语句
        return self.execute_non_query(query, (user_id,))  # 调用execute_non_query执行SQL

    # 学生相关操作
    def create_student(self, user_id, student_id):  # 定义创建学生信息方法
        """创建学生信息"""
        query = "INSERT INTO students (user_id, student_id) VALUES (%s, %s)"  # 定义插入学生信息的SQL语句
        return self.execute_non_query(query, (user_id, student_id))  # 调用execute_non_query执行SQL

    def get_student_by_user_id(self, user_id):  # 定义根据用户ID获取学生信息方法
        """根据用户ID获取学生信息"""
        query = "SELECT * FROM students WHERE user_id = %s"  # 定义查询学生信息的SQL语句
        result = self.execute_query(query, (user_id,))  # 执行查询并获取结果
        return result[0] if result else None  # 如果结果存在则返回第一条，否则返回None

    # 教师相关操作
    def create_teacher(self, user_id, teacher_id, department=None):  # 定义创建教师信息方法
        """创建教师信息"""
        query = "INSERT INTO teachers (user_id, teacher_id, department) VALUES (%s, %s, %s)"  # 定义插入教师信息的SQL语句
        return self.execute_non_query(query, (user_id, teacher_id, department))  # 调用execute_non_query执行SQL

    def get_teacher_by_user_id(self, user_id):  # 定义根据用户ID获取教师信息方法
        """根据用户ID获取教师信息"""
        query = "SELECT * FROM teachers WHERE user_id = %s"  # 定义查询教师信息的SQL语句
        result = self.execute_query(query, (user_id,))  # 执行查询并获取结果
        return result[0] if result else None  # 如果结果存在则返回第一条，否则返回None

# 示例用法
if __name__ == "__main__":  # 当模块作为主程序运行时执行
    db = Database()  # 创建Database实例
    if db.connect():  # 如果数据库连接成功
        print("数据库连接成功")  # 打印连接成功信息

        # 创建示例用户（仅用于测试）
        # success, user_id = db.create_user(
        #     username="testuser",
        #     password="testpassword",
        #     name="测试用户",
        #     avatar_url="/images/个人.png",
        #     gender="male",
        #     birthday="2000-01-01",
        #     role="student",
        #     class_name="软件工程3班"
        # )
        #
        # if success:
        #     print(f"创建用户成功，用户ID: {user_id}")
        #     # 如果是学生，创建学生信息
        #     db.create_student(user_id, "20210001")

        # 获取用户信息
        # user = db.get_user_by_username("testuser")
        # if user:
        #     print(f"用户信息: {user}")
        #     # 如果是学生，获取学生信息
        #     if user['role'] == "student":
        #         student = db.get_student_by_user_id(user['id'])
        #         if student:
        #             print(f"学生信息: {student}")

        db.disconnect()  # 关闭数据库连接
    else:  # 如果数据库连接失败
        print("数据库连接失败")