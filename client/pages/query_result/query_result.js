// pages/query_result/query_result.js
const app = getApp();

Page({
  data: {
    result: [],
    message: null,
  },

  onLoad: function (options) {
    wx.request({
      url: 'http://127.0.0.1:5000/pairquery/result/list/',
      method: 'POST',
      header: { 'content-type': 'application/x-www-form-urlencoded', 'Cookie': app.globalData.cookie },
      data: {
        'src_open_id': app.globalData.userInfo.nickName,
            },
      success: res => {
        this.setData({
          result: res.data.qa_list_source
        })
        console.log(res.data.qa_list_source)
      }
    })
  }
})