-- 创建数据库
CREATE DATABASE IF NOT EXISTS exam_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE exam_system;

-- 用户表：存储所有用户的基本信息
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，主键自增',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名/昵称',
    password VARCHAR(100) NOT NULL COMMENT '密码（加密存储）',
    name VARCHAR(20) NOT NULL COMMENT '真实姓名',
    avatar_url VARCHAR(255) DEFAULT '/images/个人.png' COMMENT '头像URL',
    gender ENUM('male', 'female') DEFAULT NULL COMMENT '性别（male:男，female:女）',
    birthday DATE DEFAULT NULL COMMENT '出生日期',
    role ENUM('student', 'teacher', 'admin') NOT NULL COMMENT '角色（student:学生，teacher:教师，admin:管理员）',
    class_name VARCHAR(50) DEFAULT NULL COMMENT '班级名称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 学生表：存储学生特有信息
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '学生ID，主键自增',
    user_id INT NOT NULL UNIQUE COMMENT '关联的用户ID',
    student_id VARCHAR(20) NOT NULL UNIQUE COMMENT '学号',
    -- 可以根据需要添加更多学生特有字段，如专业、年级等
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';

-- 教师表：存储教师特有信息
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '教师ID，主键自增',
    user_id INT NOT NULL UNIQUE COMMENT '关联的用户ID',
    teacher_id VARCHAR(20) NOT NULL UNIQUE COMMENT '教师工号',
    department VARCHAR(50) DEFAULT NULL COMMENT '所属部门',
    -- 可以根据需要添加更多教师特有字段，如职称、教授课程等
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教师表';

-- 试卷表：存储试卷信息
CREATE TABLE IF NOT EXISTS exam_papers (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '试卷ID，主键自增',
    title VARCHAR(100) NOT NULL COMMENT '试卷标题',
    description TEXT DEFAULT NULL COMMENT '试卷描述',
    file_path VARCHAR(255) NOT NULL COMMENT '试卷文件路径',
    file_name VARCHAR(100) NOT NULL COMMENT '试卷文件名',
    uploader_id INT NOT NULL COMMENT '上传者ID（教师ID）',
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    -- 可以根据需要添加更多字段，如考试时间、总分等
    FOREIGN KEY (uploader_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='试卷表';

-- 学生交卷表：存储学生交卷信息
CREATE TABLE IF NOT EXISTS student_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '交卷记录ID，主键自增',
    student_id INT NOT NULL COMMENT '学生ID',
    exam_paper_id INT NOT NULL COMMENT '试卷ID',
    file_path VARCHAR(255) NOT NULL COMMENT '交卷文件路径',
    file_name VARCHAR(100) NOT NULL COMMENT '交卷文件名',
    submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '交卷时间',
    score DECIMAL(5,2) DEFAULT NULL COMMENT '得分',
    -- 可以根据需要添加更多字段，如批改状态、批改时间等
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_paper_id) REFERENCES exam_papers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生交卷表';