from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('products/', ProductListAPIView.as_view(), name='products'),
    path('new-products/',PopularProducts.as_view(), name='popular-products'),
    path('product-details/<int:product_id>/', ProductDetailsAPIView.as_view(), name='product-details'),
    path('comment-create/', CommentProductAPIView.as_view(), name='comment-create'),
    path('comment-list/', ViewCommentProductAPIView.as_view(), name='comment-list'),
    path('comment-premission/', PermissionToCommentAPIView.as_view(), name='comment-premission'),
    path('order-product/', OrderCreateAPIView.as_view(), name='order-product'),
    path('order-history/',GetOrderHistoryAPIView.as_view(), name='order-history'),

]
