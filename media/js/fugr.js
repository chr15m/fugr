$(function(){
	// jquery-ui styles
	$('.tabs').tabs();
	$('button,input[type=submit]').button();
	
	// upload an OPML file
	$('button#upload-opml').click(function(e){
		$('input#opml-upload').trigger("click");
	});
	
	$('input[type=file]').change(function() {
		// $('input[type=text]').val($(this).val());
		$('form#opml-upload').submit();
	});
});
