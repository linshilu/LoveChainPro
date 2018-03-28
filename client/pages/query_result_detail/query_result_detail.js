const app = getApp();

Page({

    /**
     * 页面的初始数据
     */
    data: {
        result: null,
        msg: null
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function (options) {
        wx.request({
            url: app.globalData.host + '/pair_query/result/detail/',
            method: 'POST',
            data: { dst_open_id: options.dst_open_id },
            header: { 'content-type': 'application/x-www-form-urlencoded', 'Cookie': app.globalData.cookie },
            success: res => {
                this.setData({
                    dst_open_id: options.dst_open_id,
                    status: options.status,
                    apply_time: options.apply_time,
                    msg: res.data,
                })
                console.log(res.data)
            }
        })
    }
})