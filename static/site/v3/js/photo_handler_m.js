/*
 * @author: Danny
 * 
 * manyunkai@hotmail.com
 * Copyright 2012 - 2014 DannyWork Project 
 */

$(document).ready(function(){
	var btn = $('.getMore');
	var photo_box = $('.photoBox');
	var page = 1;
	var photo_loading_status = 0;
	function get_photos(){
		if (photo_loading_status){
			return false;
		}
		photo_loading_status = 1;

		btn.fadeOut('fast');
		$.ajax({
			url: '.',
			type: 'GET',
			data: {'page': page},
			dataType: 'json'
		})
		.success(function(data){
			if (data.status){
				for (var i=0; i < data.items.length; i++){
					var image = new Image;
					image.src = '/media/images/photos/s350/' + data.items[i];
					$(image).load(function(){
						$(this).hide();
						photo_box.append(this);
						$(this).fadeIn();
					})
				}
				page++;
				if (data.has_next){
					btn.fadeIn('fast');
				}
			}
			photo_loading_status = 0;
		})
		.error(function(jqXHR, textStatus) {
			btn.text('请求失败：服务器或网络错误，请稍后重试...')
			btn.fadeIn('fast');
		})
		return false;
	}
	
	btn.bind('click', get_photos);
	get_photos();
})
