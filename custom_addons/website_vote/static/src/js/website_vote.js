$(document).ready(function () {
    $("body").bind("ajaxSend", function(elm, xhr, s){
       if (s.type == "POST") {
          xhr.setRequestHeader('X-CSRF-Token', $('csrf_token').val());
       }
    });
    $('#vote').on('click', function (e) {
        alert(1);
        $.ajax({
            type: "POST",
            url: "/vote-submit/",
            async: true,
            data: { logDownload: true, CSRF: $('csrf_token').val() }
        });
    });
});