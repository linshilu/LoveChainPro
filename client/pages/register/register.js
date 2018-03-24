const app = getApp();

Page({
    data: {
        showTopTips: false,
        errorMsg: '',
        radioItems: [
            { name: '男', value: '0' },
            { name: '女', value: '1' }
        ],
        isAgree: false
    },

    formSubmit: function (e) {
        var obj = this;
        console.log(e.detail.value);
        if(!isValid(e.detail.value, obj)) return;
        var data = e.detail.value;
        console.log(data);
        wx.login({
            success: res => {
                var code = res.code;
                data['code'] = code;
                wx.request({
                    url: app.globalData.host + '/register/',
                    method: 'POST',
                    header: { 'content-type': 'application/x-www-form-urlencoded' },
                    data: data,
                    success: res => {
                        console.log(res)
                        if (res.data.status == 'success') {
                            wx.showModal({
                                content: res.data.msg,
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
                                content: res.data.msg,
                                showCancel: false,
                                success: function (res) {
                                    if (res.confirm) {
                                        console.log('用户点击确定')
                                    }
                                }
                            });
                        }
                    }
                })
            }
        });
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
    bindAgreeChange: function (e) {
        this.setData({
            isAgree: !!e.detail.value.length
        });
    }
});

function isValid(info, page) {
    if (page.data.isAgree == false) {
        showTopTips(page, '请同意用户协议')
        return false;
    }
    if (info.name == '') {
        showTopTips(page, '姓名不能为空')
        return false;
    }
    if (info.gender == '') {
        showTopTips(page, '未选择性别')
        return false;
    }
    if (info.id_number == '') {
        showTopTips(page, '身份证号不能为空')
        return false;
    }
    if (info.phone == '') {
        showTopTips(page, '手机号不能为空')
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