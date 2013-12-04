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
	var form = $('#comment_form');
	var submit_btn = $('#comment_form_submit');
	var submit_status = 0;
	
	function form_submit(){
		if (submit_status){
			return false;
		}
		submit_status = 1;
		$(this).css('background-color', '#eb9300');
		$(this).text('正在提交...');
		$.ajax({
			url: form.attr('action'),
			type: 'POST',
			data: form.serialize(),
			dataType: 'json'
		})
		.success(function(data){
			if (data.status){
				cmt_box = $('.cmtBox');
				if (!cmt_box.length){
					cmt_box = $('<div class="cmtBox fltlft"><div id="cmtTitle"><span class="fs24">有<span id="cmt_count">1</span>条留言：</span></div></div>');
					cmt_box.insertBefore('.cmtInputBox');
				}
				cmt = $(data.html);
				
				$('#cmt_count').text(parseInt($('#cmt_count').text()) + 1);
				
				related_id = parseInt($('#id_related').val());
				if (related_id){
					$('#cmt_box_' + related_id).append(cmt);
				} else {
					cmt_box.append(cmt);
				}
				form[0].reset();
				$('html, body').animate({scrollTop: cmt[0].offsetTop - 70}, 500);
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
	
	$('.commentator').live('click', function(){
		$('#info').empty();
		$('#info').append('<a class="blueA">正在回复来自 ' + $(this).text() + ' 的留言</a>（<a class="blueA" id="reply_cancel" href="#">取消</a>）').slideDown();
		$('#id_related').val($(this).attr('data-id'));
		$('html, body').animate({scrollTop: $('.cmtInputBox')[0].offsetTop - 80}, 500);
		return false;
	});
	
	$('#reply_cancel').live('click', function(){
		$('#id_related').val('');
		form[0].reset();
		$('#info').empty().slideUp();;
		return false;
	})
});
