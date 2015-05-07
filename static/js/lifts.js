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



    $(document).on("submit", "#lifts_form", function(e){
	e.preventDefault()
	// Disable the "send file" button on submit, and put up a message that we're uploading

	$("INPUT[type=submit]").attr("disabled", "disabled").attr("value", "Please Wait...");
	$("#messages").html("<h3>Your file is uploading.</h3><p><span id=percent_done>0</span>% done.  <span id=done_message></span></p> <p>This could take a while.  Please be patient, and don't leave this page.</p>");

	// Do an ajax submit, so we can show upload progress
	var formdata = new FormData($("#lifts_form")[0]);
	var action = $("FORM").attr("action");

	$.ajax({
	    url: action,
	    data: formdata,
	    type: 'POST',
	    processData: false,
	    contentType: false,
	    xhr: function(){
		var xhr = $.ajaxSettings.xhr();
		console.log(xhr);
		if (xhr.upload){
		    xhr.upload.addEventListener("progress", function(e){
			var percent = 0;
			if (e.lengthComputable) {
			    percent = Math.ceil(e.loaded / e.total * 100);
			}
			$("#percent_done").html(percent);
			if(percent === 100){
			    $("#done_message").html("Uploaded...hang on...");
			}
		    });
		}else{
		    console.log(xhr);
		}
		return xhr;
	    },
	    success: function(response){
		$("#content").html(response);
	    }
	});
    });
});
