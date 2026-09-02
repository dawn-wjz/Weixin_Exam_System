Page({

  /**
   * 页面的初始数据
   */
  data: {
    hasUploadedFiles: false, // 教师是否上传了文件
    uploadedFileName: '', // 上传的文件名
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 页面加载时检查是否有上传的文件
    this.checkForUploadedFiles();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 每次页面显示时都检查是否有上传的文件
    this.checkForUploadedFiles();
  },

  /**
   * 检查教师是否上传了文件
   */
  checkForUploadedFiles() {
    const that = this;
    
    wx.request({
      url: 'http://192.168.31.108:5000/File/check_upload', // 检查是否有上传文件的接口
      method: 'GET',
      success(res) {
        if (res.statusCode === 200 && res.data.has_file) {
          that.setData({
            hasUploadedFiles: true,
            uploadedFileName: res.data.filename
          });
        } else {
          that.setData({
            hasUploadedFiles: false,
            uploadedFileName: ''
          });
        }
      },
      fail(err) {
        console.error('检查上传文件失败:', err);
        that.setData({
          hasUploadedFiles: false,
          uploadedFileName: ''
        });
      }
    });
  },

  /**
   * 下载试卷
   */
  downloadPaper() {
    const that = this;
    
    // 检查是否有上传的文件
    if (!that.data.hasUploadedFiles) {
      wx.showToast({
        title: '教师还没发布考试！',
        icon: 'none',
        duration: 2000
      });
      return;
    }
    
    // 显示下载中提示
    wx.showLoading({
      title: '正在下载...',
      mask: true
    });
    
    // 下载文件
    wx.downloadFile({
      url: 'http://192.168.31.108:5000/File/download', // 下载文件的接口
      success(res) {
        if (res.statusCode === 200) {
          // 保存文件到本地
          try {
            const fs = wx.getFileSystemManager();
            // 获取用户目录
            const savedFilePath = wx.env.USER_DATA_PATH + '/' + that.data.uploadedFileName;
            
            // 保存文件
            fs.saveFileSync(res.tempFilePath, savedFilePath);
            
            wx.hideLoading();
            wx.showToast({
              title: '下载成功',
              icon: 'success',
              duration: 2000
            });
            
            // 打开文件
            wx.openDocument({
              filePath: savedFilePath,
              showMenu: true,
              success() {
                console.log('打开文件成功');
              },
              fail(err) {
                console.error('打开文件失败:', err);
                wx.showToast({
                  title: '打开文件失败',
                  icon: 'none'
                });
              }
            });
          } catch (saveErr) {
            wx.hideLoading();
            console.error('保存文件失败:', saveErr);
            wx.showToast({
              title: '保存文件失败',
              icon: 'none'
            });
          }
        } else {
          wx.hideLoading();
          wx.showToast({
            title: '下载失败',
            icon: 'none'
          });
        }
      },
      fail(err) {
        wx.hideLoading();
        console.error('下载文件失败:', err);
        wx.showToast({
          title: '下载失败，请检查网络',
          icon: 'none'
        });
      }
    });
  },

  /**
   * 交卷 - 上传学生的试卷文件
   */
  uploadPaper() {
    const that = this;
    
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
        
        // 显示上传中提示
        wx.showLoading({
          title: '正在上传...',
          mask: true
        });
        
        // 上传文件
        wx.uploadFile({
          url: 'http://192.168.31.108:5000/File/submit', // 服务器上传接口
          filePath: tempFilePath,
          name: 'file', // 与后端接口的file参数对应
          formData: {
            'student_id': 'student123', // 学生ID，这里可以根据实际需求获取
            'filename': fileName
          },
          success(result) {
            try {
              const data = JSON.parse(result.data);
              if (result.statusCode === 200 && data.success) {
                wx.hideLoading();
                wx.showToast({
                  title: '交卷成功',
                  icon: 'success',
                  duration: 2000
                });
                console.log('交卷成功:', data);
              } else {
                wx.hideLoading();
                wx.showToast({
                  title: data.error || '交卷失败',
                  icon: 'none'
                });
                console.error('交卷失败:', data);
              }
            } catch (e) {
              wx.hideLoading();
              wx.showToast({
                title: '交卷失败，服务器返回格式错误',
                icon: 'none'
              });
              console.error('解析交卷结果失败:', e);
            }
          },
          fail(err) {
            wx.hideLoading();
            wx.showToast({
              title: '交卷失败，请检查网络',
              icon: 'none'
            });
            console.error('交卷错误:', err);
          }
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
    });
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {
    // 下拉刷新时检查是否有新的上传文件
    this.checkForUploadedFiles();
    wx.stopPullDownRefresh();
  }
});