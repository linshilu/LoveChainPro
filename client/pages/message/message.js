// pages/message/message.js
const app = getApp();

Page({
    data: {
        message: []
    },

    onLoad: function (options) {
        wx.request({
            url: 'http://127.0.0.1/message/list/',
            method: 'POST',
            data: {},
            success: res => {
                this.setData({
                    message: res.data.data
                })
            }
        })
    }
})