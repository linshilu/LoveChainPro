//index.js
//获取应用实例
const app = getApp()

Page({
    data: {
        motto: 'Hello World',
        userInfo: {},
        user: {},
        login: true
    },
    //事件处理函数
    bindViewTap: function () {
        wx.navigateTo({
            url: '../logs/logs'
        })
    },
    onLoad: function () {
        wx.getUserInfo({
            success: res => {
                app.globalData.userInfo = res.userInfo;
                this.setData({
                    userInfo: res.userInfo
                });
            }
        })
        wx.request({
            url: 'http://127.0.0.1:5000/index/',
            method: 'POST',
            header: { 'cookie': app.globalData.cookie },
            data: {},
            success: res => {
                this.setData({
                    login: true,
                    user: res.data
                });
            }
        })
    }
})
