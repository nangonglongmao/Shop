$(function () {
    $(".ischose").bind("click",function () {
        cartid = $(this).attr("cartid");
        //告诉后台把当前用户的当前购物车数据isCheck更改
        $.post("/changecart2/",{"cartid":cartid}, function (data,status) {
            if (data.error === 0){
                if (data.flag){
                     $(document.getElementById(cartid)).html("√")
                }else {
                     $(document.getElementById(cartid)).html("")
                }

            }
        })
    });

    // 下订单
    $("#ok").bind("click", function () {
        const f = confirm("确认下单？");
        if (f){
            $.post("/qOrder/", function (data,status) {
                   if (data.error === 0){
                       location.href = "http://127.0.0.1:8000/cart/"
                   }
            })
        }
    })
});