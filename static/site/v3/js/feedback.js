/* DannyWork Project
 * 
 * @author: Danny
 * 
 * manyunkai@hotmail.com
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
})

$(document).ready(function(e) {
	var captcha = $('#captcha');
	var form = $('#contact_form');
	var submit_btn = $('#contace_form_submit');
	var submit_status = 0;
	
	function form_submit(){
		if (submit_status){
			return false;
		}
		submit_status = 1;
		$(this).css('background-color', '#eb9300');
		$(this).text('正在提交...');
		$.ajax({
			url: 'feedback/',
			type: 'POST',
			data: form.serialize(),
			dataType: 'json'
		})
		.success(function(data){
			if (data.status){
				errorMsgPopup('感谢您的反馈！', '您的反馈已成功提交，感谢您对 DannySite 的支持！');
				form[0].reset();
				captcha.click();
			} else {
				errorMsgPopup('表单填写有误', data.message);
				$('#id_captcha_0').val(data.captcha[0]);
				$('#id_captcha_1').val('');
				captcha.find('img').attr('src', data.captcha[1]);
			}
		})
		.error(function(jqXHR, textStatus) {
			captcha.click();
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
