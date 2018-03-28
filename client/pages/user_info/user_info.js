//index.js
//获取应用实例
const app = getApp()

Page({
    data: {
        userInfo: app.globalData.userInfo,
        myUserInfo: {},
        hasUserInfo: false,
        canIUse: wx.canIUse('button.open-type.getUserInfo')
    },
    onLoad: function () {
        wx.request({
            url: app.globalData.host + '/person/info/',
            method: 'POST',
            data: {},
            header: {
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

    formSubmit: function(e) {
        console.log('form发生了submit事件，携带数据为：', e.detail.value.userName)
        wx.request({
            url: app.globalData.host + '/person/info',
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
