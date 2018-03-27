//index.js
//获取应用实例
const app = getApp()

Page({
    data: {
        //可以通过hidden是否掩藏弹出框的属性，来指定那个弹出框
        hiddenmodalput: true,
        isDisabled: false,
        verifyMessage: ""
    },
    verifyCode: function (e) {
        this.setData({
            verifyMessage: e.detail.value
        })
    },

    //点击按钮痰喘指定的hiddenmodalput弹出框
    modalinput: function () {
        wx.request({
            url: 'http://192.168.1.206:5000/pair/unlock/check/',
            method: 'POST',
            data: {
            },
            header: {
                'content-type': 'application/x-www-form-urlencoded',
                'Cookie': app.globalData.cookie
            },
            success: res => {
                this.setData({
                    verifyMessage: res.data.msg
                })
                //console.log('携带数据为：', res)
            }
        })
        this.setData({
            hiddenmodalput: !this.data.hiddenmodalput
        })
    },
    //取消按钮
    cancel: function () {
        this.setData({
            hiddenmodalput: true
        });
    },
    //确认
    confirm: function (e) {
        wx.request({
            url: 'http://192.168.1.206:5000/pair/unlock/process/',
            method: 'POST',
            data: {
                'verifyCode': this.data.verifyMessage
            },
            header: {
                'content-type': 'application/x-www-form-urlencoded',
                'Cookie': app.globalData.cookie
            },
            success: res => {
                this.data.verifyMessage = res.data.msg
                this.setData({
                    isDisabled: true
                })
                //console.log('携带数据为：', res)
            }
        })
    }

})
