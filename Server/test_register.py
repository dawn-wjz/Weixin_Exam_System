from app import app
import json
import unittest

class TestRegisterAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_register(self):
        """测试注册接口"""
        print("开始测试注册接口...")
        
        # 测试数据
        data = {
            "studentId": "20210001",
            "password": "123456",
            "name": "测试用户",
            "avatarUrl": "/images/个人.png",
            "gender": "male",
            "birthday": "2000-01-01",
            "identity": "student",
            "selectedClass": "软件工程3班"
        }
        
        # 发送POST请求
        response = self.client.post(
            '/api/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # 打印响应结果
        print(f"响应状态码: {response.status_code}")
        print(f"响应数据: {response.data.decode('utf-8')}")
        
        # 断言
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()