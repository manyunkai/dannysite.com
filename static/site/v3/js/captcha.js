/* DannyWork Project
 * 
 * @author: Danny
 * 
 * manyunkai@hotmail.com
 */

$(document).ready(function(){
	var captcha = $('#captcha');

	function refresh_captcha(){
		$.ajax({
			url: '/captcha/refresh/',
			type: 'GET',
			dataType: 'json',
			beforeSend: function(){
				captcha.unbind('click');
			}
		})
		.success(function(data){
			$('#id_captcha_0').val(data.key);
			$('#id_captcha_1').val('');
			captcha.find('img').attr('src', data.image_url);
		})
		.error(function(jqXHR, textStatus) {
			
		})
		.complete(function(){
			captcha.bind('click', refresh_captcha);
		});
		return false;
	}
	
	captcha.bind('click', refresh_captcha);
})