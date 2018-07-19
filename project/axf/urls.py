# -*- coding:utf-8 -*-

from django.conf.urls import url
from axf import views

urlpatterns = [
    url(r'home/$',views.home),
    url(r'market/(\w+)/(\w+)/(\w+)/$',views.market),
    url(r'^cart/$',views.cart),
    #修改购物车  增加减少
    url(r'^changecart/(\d+)/$',views.changecart),
    #修改购物车  时候选中
    url(r'^changecart2/$', views.changecart2),
    #下订单
    url(r'^qOrder/$',views.qOrder) ,
    #查看订单
    url(r'^showOrder/$',views.showOrder),


    url(r'mine/$',views.mine),

    #登录界面
    url(r'login/$', views.login),
    url(r'quit/$', views.quit),
    #收货地址界面
    url(r'showAddress/$', views.showAddress),
    url(r'addAddress/$', views.addAddress),

    #搜索功能
    url(r'^search/$',views.search),

    #待评价
    url(r'^evaluate/$',views.evaluate),

    #客服服务
    url(r'^ICQ/$',views.ICQ),

    # 关于我们
    url(r'^about/$',views.about),




]