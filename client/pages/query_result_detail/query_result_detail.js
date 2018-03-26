const app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    result: null
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    wx.request({
      url: app.globalData.host + '/pairquery/result/detail/',
      method: 'POST',
      data: { 'result_id': options.result_id },
      header: { 'content-type': 'application/x-www-form-urlencoded', 'Cookie': app.globalData.cookie },
      success: res => {
        if (res.data.status == 'success') {
          this.setData({
            msg: res.data.result,
          })
        } else {
          console.log(res.data.result)
        }
      }
    })
  }
})