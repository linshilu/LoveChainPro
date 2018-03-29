//logs.js
const app = getApp();
const util = require('../../utils/util.js')

Page({
    data: {
    },
    formSubmit: function (e) {
        console.log('form发生了submit事件，携带数据为：', e.detail.value['name'], e.detail.value['phone'], e.detail.value['dst_open_id']);
        e.detail.value['src_open_id'] = app.globalData.userInfo.nickName;
        wx.request({
            url: app.globalData.host + '/pair_query/apply/',
            method: 'POST',
            data: e.detail.value,
            header: {
                'content-type': 'application/x-www-form-urlencoded', // 默认值
                'cookie': app.globalData.cookie
            },
            success: function (res) {
                console.log(res.data)
                wx.showModal({
                    title: '提示',
                    content: res.data['state'],
                    success: function (res) {
                        if (res.confirm) {
                            console.log('用户点击确定')
                        } else if (res.cancel) {
                            console.log('用户点击取消')
                        }
                    }
                })
                /*
                wx.navigateTo({
                  url: '../query_result/query_result'
                })
                */

            }
        })

    },
    formReset: function () {
        console.log('form发生了reset事件')
    }
})
