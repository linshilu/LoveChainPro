const app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    msg: null
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    wx.request({
        url: app.globalData.host + '/message/detail/',
        method: 'POST',
        data: {'msg_id': options.msg_id},
        header: { 'content-type': 'application/x-www-form-urlencoded', 'Cookie': app.globalData.cookie},
        success: res => {
            if(res.data.status == 'success'){
                this.setData({
                    msg: res.data.msg,
                })
            }else{
                console.log(res.data.msg)
            }
        }
    })
  },
  confirmModel: function(e){
      var content_text = {'refuse': '拒绝', 'confirm': '确认'};
      var confirm_number = {'refuse': 3, 'confirm': 2};

      wx.showModal({
          title: '操作确认',
          content: '确认' + content_text[e.target.id] + '该请求？',
          success: function (res) {
              if (res.confirm) {
                  var url = '';
                  if (this.data.msg.type == 1) {
                      url = app.globalData.host + '/pair/lock/confirm/';
                  } else if (this.data.msg.type == 3) {
                      url = app.globalData.host + '/pair/query/confirm/';
                  }
                  wx.request({
                      url: url,
                      method: 'POST',
                      data: { 'msg_id': msg.id, 'confirm': confirm_number[e.target.id] },
                      header: { 'content-type': 'application/x-www-form-urlencoded', 'Cookie': app.globalData.cookie },
                      success: res => {
                          if (res.data.status == 'success') {
                              wx.navigateBack({
                                  delta: 1
                              })
                          }
                      }
                  })
              } else if (res.cancel) {
                  console.log('用户点击取消');
              }
          }
      });
  }
})