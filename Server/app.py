# ============================================================
# 在线考试系统 - 后端服务器 (app.py)
# 技术栈: Flask + MySQL (通过 db.py 封装)
# 主要功能:
#   1. 文件管理: 老师上传试卷 / 学生交卷 / 下载 / 检查
#   2. 用户管理: 注册 / 登录 / 查询用户信息
#   3. 健康检查: 检测服务与数据库状态
# ============================================================

# ---- 导入所需模块 ----
from flask import Flask, request, jsonify, send_file   # Flask框架、请求对象、JSON响应、文件下载
from flask_cors import CORS                              # 跨域支持，允许前端(其他端口)访问本接口
import os                                                # 文件/目录操作
import uuid                                              # 生成唯一ID，用于文件重命名防冲突
from datetime import datetime                            # 时间处理(当前文件里暂未使用)
from db import Database                                  # 自定义的数据库操作类(封装了连接与增删改查)

# ---- 创建 Flask 应用实例 ----
app = Flask(__name__)

# ---- 根路由: 简单测试服务器是否启动 ----
@app.route('/')
def hello_world():
    return 'Hello World!'                                # 访问根路径返回这串文本

# ---- 配置跨域(解决前后端分离时的浏览器同源限制) ----
# 允许 /api/* 和 /File/* 这两类接口被任何来源的网页调用(开发方便,生产建议收紧)
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/File/*": {"origins": "*"}})

# ---- 创建全局数据库实例(整个程序共用一个) ----
db = Database()

# ---- 文件存储目录配置 ----
UPLOAD_FOLDER = 'File/upload'                            # 老师上传试卷的保存目录
SUBMIT_FOLDER = 'File/submit'                            # 学生交卷的保存目录

# 若目录不存在则自动创建
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(SUBMIT_FOLDER):
    os.makedirs(SUBMIT_FOLDER)

# 把目录配置写入 app 配置中，方便后续用 app.config['xxx'] 读取
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SUBMIT_FOLDER'] = SUBMIT_FOLDER


# ============================================================
# 辅助函数: 获取上传目录中"最新"的一个文件
# ============================================================
def get_latest_uploaded_file():
    try:
        # 获取上传目录的绝对路径
        upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
        print(f"上传目录绝对路径: {upload_dir}")

        # 列出上传目录中的所有文件名
        files = os.listdir(upload_dir)
        print(f"上传目录中的文件: {files}")

        # 目录为空则直接返回 None(表示没有文件)
        if not files:
            print("上传目录中没有文件")
            return None

        # 按文件修改时间从新到旧排序，取第一个 = 最新文件
        files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(upload_dir, x)), reverse=True)
        latest_file = files[0]
        print(f"最新上传的文件: {latest_file}")

        # 拼接出最新文件的完整绝对路径
        file_path = os.path.join(upload_dir, latest_file)
        print(f"最新文件的绝对路径: {file_path}")
        print(f"文件是否存在: {os.path.exists(file_path)}")

        # 还原原始文件名:
        # 上传时文件被保存为 "uuid_原名"，这里去掉 uuid 前缀只保留原文件名
        original_filename = latest_file.split('_', 1)[1] if '_' in latest_file else latest_file
        print(f"原始文件名: {original_filename}")

        # 返回文件名与路径，供下载/检查接口使用
        return {
            'filename': original_filename,   # 下载时展示给用户的原始名称
            'filepath': file_path            # 服务器磁盘上的实际路径
        }
    except Exception as e:
        # 任何异常都打印出来并返回 None，避免整个接口崩掉
        print(f"获取最新上传文件失败: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================
# 接口1: 健康检查  GET /api/health
# 作用: 前端用来探测后台是否运行、数据库能否连通
# ============================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        print("健康检查请求")
        # 尝试连接数据库
        if db.connect():
            print("数据库连接正常")
            db.disconnect()  # 测试完记得断开，避免占用连接
            return jsonify({'success': True, 'status': 'UP', 'database': 'connected'}), 200
        else:
            print("数据库连接失败")
            return jsonify({'success': True, 'status': 'UP', 'database': 'disconnected'}), 200
    except Exception as e:
        # 服务器本身出错，返回 500
        print(f"健康检查异常: {e}")
        return jsonify({'success': False, 'status': 'DOWN', 'error': str(e)}), 500


# ============================================================
# 接口2: 上传试卷(老师用)  POST /File/upload
# 请求: multipart 表单，字段名为 "file"
# ============================================================
@app.route('/File/upload', methods=['POST'])
def upload_file():
    global current_file   # 声明使用全局变量记录当前文件信息

    # 校验: 请求中必须包含文件字段
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    # 校验: 文件必须有名字(前端没选文件时 filename 为空串)
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 生成唯一文件名: "uuid_原名"，防止多文件重名互相覆盖
    filename = str(uuid.uuid4()) + '_' + file.filename
    # 拼出保存路径
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # 把文件写入磁盘
    file.save(filepath)

    # 更新全局变量，记录刚上传的文件
    current_file = {
        'filename': file.filename,   # 原始文件名
        'filepath': filepath         # 磁盘路径
    }

    # 返回成功及原始文件名
    return jsonify({'success': True, 'filename': file.filename}), 200


# ============================================================
# 接口3: 检查是否已有上传的试卷  GET /File/check_upload
# 作用: 前端进入页面时询问后台"有没有卷子可以下载"
# ============================================================
@app.route('/File/check_upload', methods=['GET'])
def check_upload():
    print("收到检查上传请求")
    # 找最新文件，且确认文件真实存在
    latest_file = get_latest_uploaded_file()
    if latest_file is not None and os.path.exists(latest_file['filepath']):
        print(f"检查上传返回有文件: {latest_file['filename']}")
        return jsonify({'has_file': True, 'filename': latest_file['filename']}), 200
    else:
        print("检查上传返回无文件")
        return jsonify({'has_file': False}), 200


# ============================================================
# 接口4: 下载最新试卷  GET /File/download
# ============================================================
@app.route('/File/download', methods=['GET'])
def download_file():
    print("收到下载文件请求")
    latest_file = get_latest_uploaded_file()
    # 有文件才允许下载
    if latest_file is not None and os.path.exists(latest_file['filepath']):
        print(f"开始下载文件: {latest_file['filepath']}，原始文件名: {latest_file['filename']}")
        try:
            # send_file 以"附件"形式让浏览器下载，download_name 指定显示的文件名
            return send_file(latest_file['filepath'], as_attachment=True, download_name=latest_file['filename'])
        except Exception as e:
            print(f"发送文件失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'发送文件失败: {str(e)}'}), 500
    else:
        print("没有可下载的文件")
        return jsonify({'error': 'No file available for download'}), 404


# ============================================================
# 接口5: 学生交卷  POST /File/submit
# 请求: multipart 表单，含 "file"(答卷) + "student_id"(学生学号)
# ============================================================
@app.route('/File/submit', methods=['POST'])
def submit_paper():
    # 校验文件字段
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 从表单中获取学生ID(前端上传时必须带上，否则用 "unknown")
    student_id = request.form.get('student_id', 'unknown')

    # 生成唯一文件名: "学生ID_uuid_原名"，可区分是谁交的卷
    filename = f"{student_id}_{str(uuid.uuid4())}_{file.filename}"
    filepath = os.path.join(app.config['SUBMIT_FOLDER'], filename)

    # 保存答卷到 submit 目录
    file.save(filepath)

    return jsonify({'success': True, 'filename': file.filename}), 200


# ============================================================
# 接口6: 用户注册  POST /api/register
# 作用: 学生/教师注册账号，并根据角色额外创建学生表/教师表记录
# ============================================================
@app.route('/api/register', methods=['POST'])
def register_user():
    """用户注册接口"""
    try:
        print("接收到注册请求")
        # 解析请求体中的 JSON 数据
        data = request.get_json()
        if not data:
            print("请求数据为空")
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400

        print(f"请求数据: {data}")

        # ---- 提取注册信息(注意字段名和前端约定一致) ----
        username = data.get('studentId')      # 学号/工号，当作登录用户名
        password = data.get('password', '123456')  # 密码，前端没传就默认 123456
        name = data.get('name')               # 姓名
        avatar_url = data.get('avatarUrl', '/images/个人.png')  # 头像，默认给一张
        gender = data.get('gender')           # 性别
        birthday = data.get('birthday')       # 生日
        role = data.get('identity')           # 角色: student / teacher
        class_name = data.get('selectedClass')# 班级(学生用)

        # ---- 校验必填字段(缺任何一个都注册失败) ----
        if not all([username, name, gender, birthday, role]):
            print(f"缺少必填字段: username={username}, name={name}, gender={gender}, birthday={birthday}, role={role}")
            return jsonify({'success': False, 'error': '缺少必填字段'}), 400

        # ---- 连接数据库 ----
        print(f"尝试连接数据库... 当前连接状态: {db.connection is not None and db.connection.is_connected()}")
        if not db.connect():
            print("数据库连接失败")
            return jsonify({'success': False, 'error': '数据库连接失败，请检查数据库配置'}), 500

        print("数据库连接成功")

        # ---- 查重: 用户名(学号)是否已被注册 ----
        print(f"检查用户名是否已存在: {username}")
        existing_user = db.get_user_by_username(username)
        print(f"检查结果: {existing_user}")
        if existing_user:
            print(f"用户名已存在: {username}")
            return jsonify({'success': False, 'error': '用户名已存在'}), 400

        # ---- 创建用户主记录(user 表) ----
        print("准备创建用户...")
        success, user_id = db.create_user(
            username=username,
            password=password,
            name=name,
            avatar_url=avatar_url,
            gender=gender,
            birthday=birthday,
            role=role,
            class_name=class_name
        )

        print(f"用户创建结果: success={success}, user_id={user_id}")

        # ---- 创建成功后再根据角色补充对应信息 ----
        if success and user_id:
            print(f"用户创建成功，用户ID: {user_id}")
            if role == 'student':
                # 学生 → 额外在 student 表插入一条记录(用学号当 student_id)
                print(f"创建学生信息，user_id={user_id}, student_id={username}")
                db.create_student(user_id, username)
                print(f"学生信息创建成功")
            elif role == 'teacher':
                # 教师 → 额外在 teacher 表插入一条记录(工号当 teacher_id)
                print(f"创建教师信息，user_id={user_id}, teacher_id={username}")
                db.create_teacher(user_id, username, None)
                print(f"教师信息创建成功")

            # 201 = 资源创建成功
            return jsonify({'success': True, 'user_id': user_id}), 201
        else:
            print("用户创建失败")
            return jsonify({'success': False, 'error': '注册失败，请稍后重试'}), 500

    except Exception as e:
        # 捕获所有异常，避免服务器崩溃
        print(f"注册接口异常: {e}")
        print(f"异常类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'}), 500
    finally:
        # 无论成功失败，最终都要释放数据库连接，防止连接泄漏
        print("请求处理完成，关闭数据库连接")
        db.disconnect()


# ============================================================
# 接口7: 用户登录  POST /api/login
# 请求 JSON: { "username": "学号", "password": "密码" }
# ============================================================
@app.route('/api/login', methods=['POST'])
def login_user():
    """用户登录接口"""
    try:
        data = request.get_json()

        # 提取登录信息
        username = data.get('username')
        password = data.get('password')

        # 校验必填
        if not all([username, password]):
            return jsonify({'success': False, 'error': '缺少用户名或密码'}), 400

        # 调用数据库方法验证账号密码
        user = db.verify_user_login(username, password)

        if user:
            # 登录成功 → 返回用户信息(注意不返回密码)
            user_info = {
                'id': user['id'],
                'username': user['username'],
                'name': user['name'],
                'avatarUrl': user['avatar_url'],
                'gender': user['gender'],
                'birthday': user['birthday'],
                'role': user['role'],
                'class_name': user['class_name']
            }
            return jsonify({'success': True, 'user_info': user_info}), 200
        else:
            # 登录失败 → 401 未授权
            return jsonify({'success': False, 'error': '用户名或密码错误'}), 401

    except Exception as e:
        print(f"登录接口异常: {e}")
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500


# ============================================================
# 接口8: 根据用户ID查询用户信息  GET /api/user/<user_id>
# ============================================================
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    """根据用户ID获取用户信息"""
    try:
        # 查询用户
        user = db.get_user_by_id(user_id)

        if user:
            # 组装返回数据(格式与登录一致，方便前端复用)
            user_info = {
                'id': user['id'],
                'username': user['username'],
                'name': user['name'],
                'avatarUrl': user['avatar_url'],
                'gender': user['gender'],
                'birthday': user['birthday'],
                'role': user['role'],
                'class_name': user['class_name']
            }
            return jsonify({'success': True, 'user_info': user_info}), 200
        else:
            # 查无此人
            return jsonify({'success': False, 'error': '用户不存在'}), 404

    except Exception as e:
        print(f"获取用户信息接口异常: {e}")
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500


# ============================================================
# 程序入口: 启动服务器
# ============================================================
if __name__ == '__main__':
    # host 绑定局域网 IP，其他设备可通过该 IP 访问
    # port 5000 端口，debug=True 支持热重载(改代码自动重启，生产环境应关闭)
    app.run(host='192.168.31.108', port=5000, debug=True)
