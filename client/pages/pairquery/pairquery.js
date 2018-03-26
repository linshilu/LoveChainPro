//logs.js
const util = require('../../utils/util.js')

Page({
  data: {  
  },
  formSubmit: function (e) {
    console.log('form发生了submit事件，携带数据为：', e.detail.value['name'], e.detail.value['phone'], e.detail.value['dst_open_id'])
    wx.request({
      url: 'http://127.0.0.1:5000/pairquery/apply/', //仅为示例，并非真实的接口地址,
      method: 'POST',
      data: 
        e.detail.value
      ,
      header: {
        'content-type': 'application/x-www-form-urlencoded' // 默认值
      },
      success: function (res) {
        console.log(res.data)
      }
    })

  },
  formReset: function () {
    console.log('form发生了reset事件')
  }
})
