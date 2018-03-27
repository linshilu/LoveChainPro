const app = getApp();

Page({
    data: {
        showTopTips: false,
        errorMsg: '',
        radioItems: [
            { name: '恋人', value: '1' },
            { name: '夫妻', value: '2' }
        ],
    },

    formSubmit: function(e){
        var obj = this;
        if (!isValid(e.detail.value, obj)) return;
        var data = e.detail.value;
        console.log(data);

        if(data.id_number == '') delete data.id_number;
        else delete data.phone;

        wx.showModal({
            title: '提示',
            content: '确认发起配对申请?',
            success: function (res) {
                if (res.confirm) {
                    console.log('用户点击确定')
                    wx.request({
                        url: app.globalData.host + '/pair/lock/apply/',
                        method: 'POST',
                        header: { 'content-type': 'application/x-www-form-urlencoded' },
                        data: data,
                        success: res => {
                            console.log(res)
                            if (res.data.status == 'success') {
                                wx.showModal({
                                    content: '发起配对申请成功',
                                    showCancel: false,
                                    success: function (res) {
                                        if (res.confirm) {
                                            console.log('用户点击确定')
                                            wx.navigateBack({
                                                delta: 1
                                            })
                                        }
                                    }
                                });
                            }
                            else {
                                wx.showModal({
                                    content: '发起配对申请失败，请检查信息填写是否有误',
                                    showCancel: false,
                                    success: function (res) {
                                        if (res.confirm) {
                                            console.log('用户点击确定')
                                        }
                                    }
                                });
                            }
                        }
                    });
                } else if (res.cancel) {
                    console.log('用户点击取消')
                }
            }
        })
    },
    radioChange: function (e) {
        var radioItems = this.data.radioItems;
        for (var i = 0, len = radioItems.length; i < len; ++i) {
            radioItems[i].checked = radioItems[i].value == e.detail.value;
        }

        this.setData({
            radioItems: radioItems
        });
    },
})

function isValid(info, page) {
    if (info.name == '') {
        showTopTips(page, '姓名不能为空')
        return false;
    }
    if (info.id_number == '' && info.phone == '') {
        showTopTips(page, '身份证号与手机号必须至少填写一项');
        return false;
    }
    if (info.relationship == '') {
        showTopTips(page, '未选择关系')
        return false;
    }
    return true;
}

function showTopTips(page, msg) {
    page.setData({
        showTopTips: true,
        errorMsg: msg
    });
    setTimeout(function () {
        page.setData({
            showTopTips: false
        });
    }, 3000);
}