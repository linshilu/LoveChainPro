//index.js
//获取应用实例
const app = getApp()

Page({
    data: {
        motto: 'Hello World',
        userInfo: {},
        myUserInfo: {},
        hasUserInfo: false,
        canIUse: wx.canIUse('button.open-type.getUserInfo')
    },
    //事件处理函数
    bindViewTap: function () {
        wx.navigateTo({
            url: '../logs/logs'
        })
    },
    onLoad: function () {
        if (app.globalData.userInfo) {
            this.setData({
                userInfo: app.globalData.userInfo,
                hasUserInfo: true
            })
        } else if (this.data.canIUse) {
            // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
            // 所以此处加入 callback 以防止这种情况
            app.userInfoReadyCallback = res => {
                this.setData({
                    userInfo: res.userInfo,
                    hasUserInfo: true
                })
            }
        } else {
            // 在没有 open-type=getUserInfo 版本的兼容处理
            wx.getUserInfo({
                success: res => {
                    app.globalData.userInfo = res.userInfo
                    this.setData({
                        userInfo: res.userInfo,
                        hasUserInfo: true
                    })
                }
            })
        }

        wx.request({
            url: 'http://192.168.1.206:5000/person/info',
            method: 'GET',
            data: {},
            header: {
                //'content-type': 'application/json',
                'Cookie': app.globalData.cookie
            },
            success: res => {
                this.setData({
                    myUserInfo: res.data
                })
                //console.log('携带数据为：', res)
            }
        })
    },
    getUserInfo: function (e) {
        console.log(e)
        app.globalData.userInfo = e.detail.userInfo
        this.setData({
            userInfo: e.detail.userInfo,
            hasUserInfo: true
        })
    },

    formSubmit: function(e) {
        console.log('form发生了submit事件，携带数据为：', e.detail.value.userName)
        wx.request({
            url: 'http://192.168.1.206:5000/person/info',
            method: 'POST',
            data: {
                'name': e.detail.value.userName,
                'gender': e.detail.value.userGender,
                'phone': e.detail.value.userPhone,
                'IDCard': e.detail.value.userIDCard,
                'loveStatus': e.detail.value.userLoveStatus,
                'balance': e.detail.value.userBalance
            },
            header: {
                'content-type': 'application/x-www-form-urlencoded',
                'Cookie': app.globalData.cookie
            },
            success: function (res) {
                console.log('form发生了submit事件，携带数据为：', res.value)
            }
        })
    }
})
