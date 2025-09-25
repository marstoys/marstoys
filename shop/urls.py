from django.urls import path
from shop.views.get_all_products_list import ProductListAPIView
from shop.views.get_all_categories import CategoryListAPIView
from shop.views.get_product_comments import ProductComments
from shop.views.get_product_details import ProductDetailsAPIView
from shop.views.create_product_comments import CreateCommentProductAPIView
from shop.views.create_order import OrderCreateAPIView
from shop.views.get_permission_to_comment import PermissionToCommentAPIView
from shop.views.get_order_history import GetOrderHistoryAPIView
from shop.views.get_popular_products import PopularProducts
from shop.views.exel_import import ExcelUploadView



urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('products/', ProductListAPIView.as_view(), name='products'),
    path('new-products/', PopularProducts.as_view(), name='popular-products'),
    path('product-details/', ProductDetailsAPIView.as_view(), name='product-details'),
    path('comment-create/', CreateCommentProductAPIView.as_view(), name='comment-create'),
    path('comment-permission/', PermissionToCommentAPIView.as_view(), name='comment-premission'),
    path('order-product/', OrderCreateAPIView.as_view(), name='order-product'),
    path('order-history/',GetOrderHistoryAPIView.as_view(), name='order-history'),
    path('product-comments/<int:product_id>/', ProductComments.as_view(), name='product-comments'),
    path("excel-import/", ExcelUploadView.as_view(), name="excel-import"),
]
