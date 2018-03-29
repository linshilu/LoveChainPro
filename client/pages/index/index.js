//index.js
//获取应用实例
const app = getApp()

Page({
    data: {
        userInfo: {},
        user: {
            name: '加载中...',
            gender: '加载中...',
            love_status: '加载中...',
            balance: '加载中...'
        },
        reg: 0,
        font_color: '#aaa'
    },
    onLoad: function () {
        wx.login({
            success: res => {
                console.log(res)
                var code = res.code;
                wx.request({
                    url: app.globalData.host + '/login/',
                    method: 'POST',
                    header: { 'content-type': 'application/x-www-form-urlencoded' },
                    data: { 'code': code },
                    success: res => {
                        if (res.data.status == 'success') {
                            console.log(res.data);
                            app.globalData.cookie = res.header['Set-Cookie'];
                            this.setData({
                                reg: 1,
                                user: res.data.user,
                                font_color: '#000'
                            });
                        } else if (res.data.status == 'fail') {
                            console.log(res.data.msg);
                            if (res.data.msg == '未注册') {
                                this.setData({
                                    reg: 2
                                });
                            }
                        }
                    }
                })
            }
        });

        wx.getUserInfo({
            success: res => {
                app.globalData.userInfo = res.userInfo;
                this.setData({
                    userInfo: res.userInfo
                });
            }
        })

    },
    onShow: function () {
        if (this.data.reg == 1) {
            wx.request({
                url: app.globalData.host + '/user/data/',
                method: 'POST',
                header: { 'cookie': app.globalData.cookie },
                data: {},
                success: res => {
                    this.setData({
                        user: res.data,
                    });
                }
            })
        }
    },
    closeAccount: function () {
        wx.showModal({
            content: '确认注销用户？',
            showCancel: true,
            success: function (res) {
                if (res.confirm) {
                    wx.request({
                        url: app.globalData.host + '/close/',
                        method: 'POST',
                        header: { 'cookie': app.globalData.cookie },
                        data: {},
                        success: res => {
                        }
                    })
                }
            }
        });
    }
})
