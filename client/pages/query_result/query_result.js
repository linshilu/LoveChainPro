// pages/query_result/query_result.js
const app = getApp();

Page({
  data: {
    result: []
  },

  onLoad: function (options) {
    wx.request({
      url: 'http://127.0.0.1:5000/pairquery/result/list/',
      method: 'POST',
      data: {
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