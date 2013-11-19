/*
 * @author: Danny
 * 
 * manyunkai@hotmail.com
 * Copyright 2012 - 2014 DannyWork Project 
 */

$(document).ready(function(){
	btn = $('.getMore');
	share_loading_status = 0;
	if (!btn.length){
		return false;
	}
	
	function get_more(){
		if (share_loading_status){
			return false;
		}
		share_loading_status = 1;
	
		var curr_page = btn.attr('data-page')

		btn.fadeOut('fast');
		$.ajax({
			url: '.',
			type: 'GET',
			data: {'page': curr_page},
			dataType: 'json'
		})
		.success(function(data){
			if (data.status){
				$(data.html).insertBefore(btn);
				if (data.has_next){
					btn.attr('data-page', curr_page + 1);
					btn.fadeIn('slow');
					share_loading_status = 0;
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
