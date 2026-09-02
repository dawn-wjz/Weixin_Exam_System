// index.js
const defaultAvatarUrl = 'https://c-ssl.dtstatic.com/uploads/item/202005/18/20200518080041_cgwpv.thumb.400_0.png'
const app = getApp()

Page({
  data: {
    motto: '没有注册？ 立即注册!',
    password: '',
    userInfo: {
      avatarUrl: defaultAvatarUrl,
      nickName: ''
    },

    index:0,
    roleArray:[['选择班级!','软件工程3班','软件工程4班','软件工程5班'],['选择身份!','教师','学生']],
    roleIndex: [0,0],
    
    hasUserInfo: false,
    canIUseNicknameComp: wx.canIUse('input.type.nickname'),
  },
  bindRolePickerChange: function (e) {
    console.log('picker发送选择改变，携带值为', e.detail.value)
    this.setData({
      roleIndex: e.detail.value
    })
  },

  bindViewTap() {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },

  Register: function () {
    console.log('Register方法被调用');
    wx.redirectTo({
      url: '../register-info/register-info', 
      success: function() {
        console.log('页面跳转成功');
      },
      fail: function(err) {
        console.log('页面跳转失败:', err);
      }
    })
  },

  onChooseAvatar(e) {
    const { avatarUrl } = e.detail
    const { nickName } = this.data.userInfo
    this.setData({
      "userInfo.avatarUrl": avatarUrl,
      hasUserInfo: nickName && avatarUrl && avatarUrl !== defaultAvatarUrl,
    })
  },
  
  // 处理用户名输入
  onNicknameInput(e) {
    this.setData({
      "userInfo.nickName": e.detail.value
    })
    
    // 更新hasUserInfo状态
    const { userInfo } = this.data
    this.setData({
      hasUserInfo: userInfo.nickName && userInfo.avatarUrl && userInfo.avatarUrl !== defaultAvatarUrl
    })
  },
  
  // 处理密码输入
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    })
  },
  
  // 登录按钮点击事件
  onLogin() {
    const { userInfo, password, roleIndex, roleArray } = this.data
    
    // 验证输入
    if (!userInfo.nickName || !password) {
      wx.showToast({
        title: '请填写用户名和密码',
        icon: 'none'
      })
      return
    }
    
    // 验证角色选择
    const [classIndex, roleSelectIndex] = roleIndex
    if (classIndex === 0 || roleSelectIndex === 0) {
      wx.showToast({
        title: '请选择完整身份信息',
        icon: 'none'
      })
      return
    }
    
    // 获取选择的角色信息
    const className = roleArray[0][classIndex]
    const roleText = roleArray[1][roleSelectIndex]
    const selectedRole = roleText === '教师' ? 'teacher' : 'student'
    
    // 显示加载状态
    wx.showLoading({
      title: '登录中...',
      mask: true
    })
    
    // 调用全局登录方法
    app.login({
      username: userInfo.nickName,
      password: password
    }).then((userInfo) => {
      wx.hideLoading()
      
      // 如果是管理员，使用选择的角色进行跳转
      let displayRole = userInfo.role
      if (userInfo.role === 'admin') {
        displayRole = selectedRole
        // 保存选择的班级信息
        userInfo.selected_class = className
        userInfo.selected_role = selectedRole
      }
      
      // 登录成功，根据角色动态设置tabbar的考试页面路径
      app.setTabBarExamPage(displayRole)
      
      // 跳转到对应角色的首页
      app.navigateToHome(displayRole)
    }).catch(err => {
      wx.hideLoading()
      wx.showToast({
        title: err.message || '登录失败，请重试',
        icon: 'none'
      })
    })
  },
})