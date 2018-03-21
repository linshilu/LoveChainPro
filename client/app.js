//app.js
App({
    onLaunch: function () {
        var app = this;
        // 展示本地存储能力
        var logs = wx.getStorageSync('logs') || []
        logs.unshift(Date.now())
        wx.setStorageSync('logs', logs)

        wx.login({
            success: res => {
                console.log(res)
                var code = res.code;
                wx.request({
                    url: 'http://127.0.0.1:5000/login/',
                    method: 'POST',
                    header: { 'content-type': 'application/x-www-form-urlencoded' },
                    data: { 'code': code },
                    success: res => {
                        if (res.data.status == 'success') {
                            app.globalData.cookie = res.header['Set-Cookie'];
                            app.globalData.is_reg = true;
                        } else if (res.data.status == 'fail') {
                            console.log(res.data.msg);
                            if (res.data.msg == '未注册') {
                                app.globalData.is_reg = false;
                            }
                        }
                    }
                })
            }
        });

        // 获取用户信息
        wx.getSetting({
          success: res => {
            if (res.authSetting['scope.userInfo']) {
              // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
              wx.getUserInfo({
                success: res => {
                  // 可以将 res 发送给后台解码出 unionId
                  app.globalData.userInfo = res.userInfo

                  // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
                  // 所以此处加入 callback 以防止这种情况
                  if (this.userInfoReadyCallback) {
                    this.userInfoReadyCallback(res)
                  }
                }
              })
            }
          }
        })
    },
    globalData: {
        host: "http://127.0.0.1:5000",
        userInfo: null,
        cookie: null,
        is_reg: true
    }
})