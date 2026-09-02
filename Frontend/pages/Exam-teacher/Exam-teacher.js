// pages/Exam-teacher/Exam-teacher.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    uploadProgress: 0, // 上传进度
    isUploading: false, // 是否正在上传
    uploadStatus: '', // 上传状态：''、'success'、'fail'
    selectedFileName: '' // 选中的文件名
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {

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

  },

  /**
   * 上传试卷
   */
  uploadExam: function() {
    const that = this;
    
    // 如果正在上传，不允许重复操作
    if (that.data.isUploading) {
      wx.showToast({
        title: '正在上传中...',
        icon: 'none'
      });
      return;
    }
    
    // 选择文件
    wx.chooseMessageFile({
      count: 1, // 最多选择1个文件
      type: 'file', // 选择文件类型
      extension: ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'], // 允许的文件扩展名
      success(res) {
        const tempFilePath = res.tempFiles[0].path;
        const fileName = res.tempFiles[0].name;
        const fileSize = res.tempFiles[0].size;
        
        console.log('选择的文件:', fileName, '大小:', fileSize);
        
        // 验证文件大小（限制100MB）
        if (fileSize > 100 * 1024 * 1024) {
          wx.showToast({
            title: '文件大小不能超过100MB',
            icon: 'none'
          });
          return;
        }
        
        // 更新选中的文件名
        that.setData({
          selectedFileName: fileName,
          isUploading: true,
          uploadProgress: 0,
          uploadStatus: ''
        });
        
        // 上传文件
        const uploadTask = wx.uploadFile({
          url: 'http://192.168.31.108:5000/File/upload', // 服务器上传接口
          filePath: tempFilePath,
          name: 'file', // 与后端接口的file参数对应
          formData: {
            'filename': fileName
          },
          success(result) {
            try {
              const data = JSON.parse(result.data);
              if (result.statusCode === 200) {
                that.setData({
                  uploadStatus: 'success',
                  isUploading: false
                });
                wx.showToast({
                  title: '上传成功',
                  icon: 'success',
                  duration: 2000
                });
                console.log('上传结果:', data);
              } else {
                that.setData({
                  uploadStatus: 'fail',
                  isUploading: false
                });
                wx.showToast({
                  title: data.error || '上传失败',
                  icon: 'none'
                });
                console.error('上传失败:', data);
              }
            } catch (e) {
              that.setData({
                uploadStatus: 'fail',
                isUploading: false
              });
              wx.showToast({
                title: '上传失败，服务器返回格式错误',
                icon: 'none'
              });
              console.error('解析上传结果失败:', e);
            }
          },
          fail(err) {
            that.setData({
              uploadStatus: 'fail',
              isUploading: false
            });
            wx.showToast({
              title: '上传失败，请检查网络',
              icon: 'none'
            });
            console.error('上传错误:', err);
          },
          complete() {
            // 重置进度条（可选）
            setTimeout(() => {
              that.setData({
                uploadProgress: 0,
                selectedFileName: ''
              });
            }, 2000);
          }
        });
        
        // 监听上传进度
        uploadTask.onProgressUpdate((res) => {
          console.log('上传进度:', res.progress);
          console.log('已上传字节:', res.totalBytesSent);
          console.log('预期总字节:', res.totalBytesExpectedToSend);
          
          that.setData({
            uploadProgress: res.progress
          });
        });
      },
      fail(err) {
        console.error('选择文件失败:', err);
        if (err.errMsg !== 'chooseMessageFile:fail cancel') {
          wx.showToast({
            title: '选择文件失败',
            icon: 'none'
          });
        }
      }
    })
  },
})