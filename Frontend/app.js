// app.js
App({
  globalData: {
    userInfo: null,           // 用户信息
    systemInfo: null,         // 系统信息
    apiBaseUrl: 'http://192.168.31.108:5000' // 后端API地址
  },

  onLaunch() {
    // 获取系统信息
    wx.getSystemInfo({
      success: res => {
        this.globalData.systemInfo = res
      }
    })
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 监听网络状态
    wx.onNetworkStatusChange(res => {
      console.log('网络状态变化:', res)
    })
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    // 获取当前页面路径
    const pages = getCurrentPages()
    const currentPage = pages[pages.length - 1]
    const currentPath = currentPage ? currentPage.route : ''
    
    if (token && userInfo) {
      this.globalData.userInfo = userInfo
      // 可以在这里验证token有效性
      // 暂时跳过token验证
      
      // 根据用户角色设置tabbar的考试页面
      let displayRole = userInfo.role
      if (userInfo.role === 'admin' && userInfo.selected_role) {
        displayRole = userInfo.selected_role
      }
      this.setTabBarExamPage(displayRole)
      
      // 已经登录，直接进入对应角色的首页
      this.navigateToHome(displayRole)
    } else {
      // 未登录，跳转到登录页面
      // 但如果当前已经在登录页面或注册页面，则不执行跳转
      if (currentPath !== 'pages/login/login' && currentPath !== 'pages/register-info/register-info') {
        wx.reLaunch({
          url: '/pages/login/login'
        })
      }
    }
  },

  // 验证token有效性
  validateToken(token) {
    // 这里应该调用后端API验证token
    // 暂时返回true
    return true
  },

  // 全局登录方法
  login(userData) {
    return new Promise((resolve, reject) => {
      const { username, password } = userData
      
      // 调用后端登录API
      wx.request({
        url: `${this.globalData.apiBaseUrl}/api/login`,
        method: 'POST',
        data: {
          username,
          password
        },
        success: res => {
          if (res.data.success) {
            const userInfo = res.data.user_info
            
            // 生成token（这里暂时使用用户ID作为token）
            const token = `user_${userInfo.id}_${Date.now()}`
            
            // 添加token到用户信息
            userInfo.token = token
            userInfo.loginTime = new Date().toISOString()
            
            // 保存用户信息
            this.globalData.userInfo = userInfo
            wx.setStorageSync('userInfo', userInfo)
            wx.setStorageSync('token', token)
            
            resolve(userInfo)
          } else {
            reject(new Error(res.data.error || '登录失败'))
          }
        },
        fail: err => {
          reject(new Error('网络错误，请检查网络连接'))
        }
      })
    })
  },

  // 全局注册方法
  register(userData) {
    return new Promise((resolve, reject) => {
      // 调用后端注册API
      wx.request({
        url: `${this.globalData.apiBaseUrl}/api/register`,
        method: 'POST',
        data: userData,
        success: res => {
          if (res.data.success) {
            resolve(res.data)
          } else {
            reject(new Error(res.data.error || '注册失败'))
          }
        },
        fail: err => {
          reject(new Error('网络错误，请检查网络连接'))
        }
      })
    })
  },

  // 全局登出方法
  logout() {
    // 清除用户信息
    this.globalData.userInfo = null
    wx.removeStorageSync('userInfo')
    wx.removeStorageSync('token')
    
    // 跳转到登录页
    wx.reLaunch({
      url: '/pages/login/login'
    })
  },

  // 全局路由跳转（根据身份）
  navigateToHome(role) {
    const routes = {
      'student': '/pages/Exam-student/Exam-student',
      'teacher': '/pages/Exam-teacher/Exam-teacher'
    }
    
    if (routes[role]) {
      wx.reLaunch({
        url: routes[role]
      })
    } else {
      wx.showToast({
        title: '未知用户身份',
        icon: 'error'
      })
    }
  },

  // 全局错误处理
  handleError(error) {
    console.error('全局错误:', error)
    wx.showToast({
      title: error.message || '操作失败',
      icon: 'none'
    })
  },

  // 动态设置tabbar的考试页面
  setTabBarExamPage(role) {
    const examPage = role === 'teacher' ? '/pages/Exam-teacher/Exam-teacher' : '/pages/Exam-student/Exam-student'
    
    // 更新tabbar配置
    wx.setTabBarItem({
      index: 0, // 考试tab在tabbar中的索引
      pagePath: examPage
    })
  }
})