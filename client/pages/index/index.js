//index.js
//获取应用实例
const app = getApp()

Page({
    data: {
        motto: 'Hello World',
        userInfo: {},
        user: {
            name: '加载中...',
            gender: '加载中...',
            love_status: '加载中...',
            balance: '加载中...'
        },
        login: true,
        font_color: '#aaa'
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
                    user: res.data,
                    font_color: '#000'
                });
            },
            fail: res => {
                this.setData({
                    user: {
                        name: '加载失败',
                        gender: '加载失败',
                        love_status: '加载失败',
                        balance: '加载失败'
                    }
                });
            }
        })
    },
    closeAccount: function () {
        wx.request({
            url: 'http://127.0.0.1:5000/close/',
            method: 'POST',
            header: { 'cookie': app.globalData.cookie },
            data: {},
            success: res => {
            }
        })
    }
})
