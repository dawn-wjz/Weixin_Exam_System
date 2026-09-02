// pages/profile/profile.js
const app = getApp()

Page({
  data: {
    userInfo: null
  },

  onLoad() {
    // 获取用户信息
    this.setData({
      userInfo: app.globalData.userInfo
    })
  },

  onShow() {
    // 每次显示页面时更新用户信息
    this.setData({
      userInfo: app.globalData.userInfo
    })
  },

  // 登出按钮点击事件
  onLogout() {
    wx.showModal({
      title: '确认登出',
      content: '您确定要退出登录吗？',
      success: res => {
        if (res.confirm) {
          // 调用全局登出方法
          app.logout()
        }
      }
    })
  },

  // 跳转到注册信息页面
  toRegisterInfo() {
    wx.navigateTo({
      url: '../register-info/register-info'
    })
  }
})