/**
 * Created by SunCoder on 2016/8/30.
 */
var loading={

    //指定对象，产生loading遮罩
    Show : function (selecter) {
        loading.Hide(selecter);
        var obj = $(selecter);
        if (obj.length > 0) {
            //obj.css("position", "relative");
            if (obj.css("position") != "relative" && obj.css("position") != "fixed" && obj.css("position") != "absolute") {
                obj.css("position", "relative");
            }
            var ajld=$('<div class="Ajaxloading" style="z-index: 196;"></div>');
            ajld.appendTo(obj).width(obj[0].clientWidth).height(obj[0].clientHeight).show();
        }
    },

    //指定对象，隐藏loading遮罩
    Hide : function (selecter) {
        if(selecter){
            $(selecter).find('.Ajaxloading').remove();
        }
        else{
            $('.Ajaxloading').remove();
        }
    }
};
