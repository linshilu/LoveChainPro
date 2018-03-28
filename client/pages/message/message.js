// pages/message/message.js
const app = getApp();

Page({
    data: {
        message: []
    },

    onLoad: function (options) {
        wx.request({
            url: app.globalData.host +'/list/',
            method: 'POST',
            header: { 'cookie': app.globalData.cookie },
            data: {},
            success: res => {
                this.setData({
                    message: res.data.data
                })
            }
        })
    }
})