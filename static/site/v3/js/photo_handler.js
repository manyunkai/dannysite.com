/* DannyWork Project
 * 
 * @author: Danny
 * 
 * manyunkai@hotmail.com
 */

$(document).ready(function(){
	btn = $('.getMore');
	photo_loading_status = 0;
	if (!btn.length){
		return false;
	}
	
	function get_more(){
		if (photo_loading_status){
			return false;
		}
		photo_loading_status = 1;

		btn.fadeOut('fast');
		$.ajax({
			url: '.',
			type: 'GET',
			data: {'offset': btn.attr('data-offset')},
			dataType: 'json'
		})
		.success(function(data){
			if (data.status){
				var html = data.html + '<div class="clearfloat"></div>';
				$(html).insertBefore(btn);
				$(".scrollLoading").scrollLoading();
				if (data.has_next){
					btn.attr('data-offset', data.offset);
					btn.fadeIn('slow');
					photo_loading_status = 0;
				} else {
					btn.remove();
				}
			}
		})
		.error(function(jqXHR, textStatus) {
			btn.text('请求失败：服务器或网络错误，请稍后重试...')
			btn.fadeIn('fast');
		})
	}
	
	btn.bind('click', get_more);
})
