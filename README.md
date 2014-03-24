DannySite
=========

Source code to dannysite.com

Visit my website at http://www.dannysite.com/


### 介绍

DannySite是一个由个人兴趣与学习实践而生的个人网站。网站采用Django框架开发，功能主要包含博客和图片等。

### 功能

* 账户：注册、登录、修改密码、通过邮件重置密码、通过邮件邀请注册等；
* 博客：包含标签、分类、RSS订阅、搜索等。为方便编辑，还嵌入了UEditor（百度富文本编辑器）；
* 图片：目前仅支持最基本的浏览；
* 兴趣：目前仅支持最基本的浏览；
* 其他：关于与意见反馈、邮件队列、图片处理、分页功能等。

### 使用的第三方包

* django-simple-captcha：一个验证码模块；
* DjangoUeditor：百度富文本编辑器。为适应个人需求，对View等进行了重新定制。

### 目前未完善的功能和已知Bugs

* Account: 注册、密码修改、密码重置等template未完成；
* Ueditor: 上传图片等重写View后未考虑路径传入；
* Mail: 注册邀请邮件未投递。

### 关于DannySite - UI的版权

作为非设计出生的我来说，做一套像样的UI对我来说并不容易，因此我个人保留UI上的版权。感谢配合！
