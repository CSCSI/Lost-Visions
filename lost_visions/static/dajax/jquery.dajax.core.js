var Dajax = window.Dajax || (function($) {
    var that = {};

    that.process = function(data)
    {
        $.each(data, function(i,elem) {
        switch(elem.cmd)
        {
            case 'alert':
                alert(elem.val);
            break;

            case 'data':
                eval( elem.fun+"(elem.val);" );
            break;

            case 'as':
                if(elem.prop == 'innerHTML'){
                    $(elem.id).html(elem.val);
                }
                else{
                    $.each($(elem.id),function(){ this[elem.prop] = elem.val; });
                }
            break;

            case 'addcc':
                $.each(elem.val,function(){
                    $(elem.id).addClass(String(this));
                });
            break;

            case 'remcc':
                $.each(elem.val,function(){
                    $(elem.id).removeClass(String(this));
                });
            break;

            case 'ap':
                $.each($(elem.id),function(){ this[elem.prop] += elem.val; });
            break;

            case 'pp':
                $.each($(elem.id),function(){ this[elem.prop] = elem.val + this[elem.prop]; });
            break;

            case 'clr':
                $.each($(elem.id),function(){ this[elem.prop] = ""; });
            break;

            case 'red':
                window.setTimeout('window.location="'+elem.url+'";',elem.delay);
            break;

            case 'js':
                eval(elem.val);
            break;

            case 'rm':
                $(elem.id).remove();
            break;

            default:
            break;
            }
        });
    }

    return that;
}(jQuery));

window.Dajax = Dajax;
