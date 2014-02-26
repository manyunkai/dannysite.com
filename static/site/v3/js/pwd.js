/*
 * @author: Danny
 * 
 * manyunkai@hotmail.com
 * Copyright 2012 - 2014 DannyWork Project 
 */

function errorMsgPopup(title, message){
	$('#error_title').text(title);
	$('#error_msg').text(message);
	
	$('.popupBox').fadeIn('fast');
}

$(document).ready(function(){
	$('#error_confirm').bind('click', function(){
		$('.popupBox').fadeOut('fast');
	});
});
 
 $(document).ready(function(){
 	var form = $('#pwd_reset_form');
	var submit_btn = $('#pwd_reset_submit');
	var submit_status = 0;
	
	function form_submit(){
		if (submit_status){
			return false;
		}
		submit_status = 1;
		$(this).css('background-color', '#eb9300');
		$(this).text('请稍后...');
		
		$.ajax({
			url: form.attr('action'),
			type: 'POST',
			data: form.serialize(),
			dataType: 'json'
		})
		.success(function(data){
			if (data.status){
				$('.container').html(data.html);
			} else {
				errorMsgPopup('认证错误', data.message);
			}
		})
		.error(function(jqXHR, textStatus) {
			errorMsgPopup('发生错误', '表单提交失败：服务器或网络错误，请重试。');
		})
		.complete(function(jqXHR, textStatus){
			submit_btn.css('background-color', '#f39800');
			submit_btn.text('提交');
			submit_status = 0;
		});
		
		return false;
	}
	
	submit_btn.bind('click', form_submit);
 });
