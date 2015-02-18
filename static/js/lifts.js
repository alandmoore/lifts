$(document).ready(function(){


    $("#pw_protect_username,#pw_protect_password").prop("disabled", true);
    $(document).on("change", "#do_password", function(){
	$("#pw_protect_username,#pw_protect_password").prop("disabled", ! $(this).is(":checked"));
    });
    
});
