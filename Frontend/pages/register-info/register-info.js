// pages/register-info/register-info.js
const app = getApp()

Page({

  /**
   * 页面的初始数据
   */
  data: {
    avatarUrl: '/images/个人.png', // 默认头像
    studentId: '', // 学号
    nickName: '', // 微信昵称
    password: '', // 密码
    name: '', // 姓名
    birthday: '', // 出生日期
    gender: '', // 性别
    classList: ['计算机1班', '软件工程3班', '软件工程4班', '软件工程5班', '软件工程2班'], // 班级列表
    selectedClass: '', // 选中的班级
    identityList: [ // 注册身份列表
      { label: '学生', value: 'student' },
      { label: '教师', value: 'teacher' },
      { label: '管理员', value: 'admin' }
    ],
    identity: '' // 选中的身份
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    console.log('注册页面onLoad被调用');
    console.log('传入的参数:', options);
  },

  /**
   * 选择头像
   */
  chooseAvatar() {
    const that = this;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success(res) {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        that.setData({
          avatarUrl: tempFilePath
        });
      }
    });
  },

  /**
   * 输入框内容变化
   */
  inputChange(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({
      [field]: value
    });
  },

  /**
   * 显示年龄选择器
   */
  showAgePicker() {
    // 触发picker的点击事件
    const picker = this.selectComponent('.age-picker');
    if (picker) {
      picker.show();
    }
  },

  /**
   * 出生日期变化
   */
  birthdayChange(e) {
    this.setData({
      birthday: e.detail.value
    });
  },

  /**
   * 选择性别
   */
  selectGender(e) {
    const gender = e.currentTarget.dataset.gender;
    this.setData({
      gender: gender
    });
  },

  /**
   * 班级变化
   */
  classChange(e) {
    const index = e.detail.value;
    this.setData({
      selectedClass: this.data.classList[index]
    });
  },

  /**
   * 注册身份变化
   */
  identityChange(e) {
    this.setData({
      identity: e.detail.value
    });
  },

  /**
   * 注册按钮点击事件
   */
  register() {
    const { studentId, nickName, password, name, birthday, gender, selectedClass, identity, avatarUrl } = this.data
    
    // 表单验证
    if (!studentId.trim()) {
      wx.showToast({ title: '请输入学号/工号', icon: 'none' });
      return;
    }
    if (!nickName.trim()) {
      wx.showToast({ title: '请输入微信昵称', icon: 'none' });
      return;
    }
    if (!password.trim()) {
      wx.showToast({ title: '请输入密码', icon: 'none' });
      return;
    }
    if (!name.trim()) {
      wx.showToast({ title: '请输入姓名', icon: 'none' });
      return;
    }
    if (!birthday) {
      wx.showToast({ title: '请选择出生日期', icon: 'none' });
      return;
    }
    if (!gender) {
      wx.showToast({ title: '请选择性别', icon: 'none' });
      return;
    }
    if (!identity) {
      wx.showToast({ title: '请选择身份', icon: 'none' });
      return;
    }
    if (identity === 'student' && !selectedClass) {
      wx.showToast({ title: '请选择班级', icon: 'none' });
      return;
    }
    
    // 显示加载状态
    wx.showLoading({
      title: '注册中...',
      mask: true
    })
    
    // 准备注册数据
    const registerData = {
      studentId: studentId,
      username: nickName, // 使用微信昵称作为用户名
      password: password,
      name: name,
      birthday: birthday,
      gender: gender,
      selectedClass: selectedClass,
      identity: identity,
      avatarUrl: avatarUrl
    }
    
    // 调用全局注册方法
    app.register(registerData)
      .then(res => {
        wx.hideLoading()
        wx.showToast({
          title: '注册成功',
          icon: 'success',
          duration: 1500,
          success: () => {
            // 返回登录页面
            setTimeout(() => {
              wx.navigateBack();
            }, 1500);
          }
        });
      })
      .catch(err => {
        wx.hideLoading()
        wx.showToast({
          title: err.message || '注册失败，请重试',
          icon: 'none'
        });
      })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})