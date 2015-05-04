$(document).ready(function(){

    // Disable password fields until the box is checked to use them.
    $("#pw_protect_username,#pw_protect_password").prop("disabled", true);
    $(document).on("change", "#do_password", function(){
	$("#pw_protect_username,#pw_protect_password").prop("disabled", ! $(this).is(":checked"));
	$("#autogen_pw_note").toggle($(this).is(":checked"));
    });
    $("#do_password").trigger("change");
    
    // Create a new recipients box whenever the last one is given a value
    $(document).on("keyup", "input[name=recipients]", function(){
	if ($(this).val().length > 0 && $(this).is("input[name=recipients]:last")){
	    var new_li = $(this).closest("li").clone();
	    $(new_li).find("input[name=recipients]").removeAttr("required").val('');
	    $(this).closest("ul").append(new_li);
	}else if ($(this).val().length === 0){
	    if (!$(this).is("input[name=recipients]:last")){
		$(this).closest("li").remove();
	    }
	    $("input[name=recipients]:first").attr("required", "required");
	}
    });
    
});
