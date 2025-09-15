from shop.models import CommentProducts,Products
from django.contrib.auth.models import User
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException



def create_comment_product(product_id, comment, rating, user):
    # This function should implement the logic to create a comment for a product.
    # It is assumed that the necessary models and logic are defined elsewhere in the codebase.
    product = Products.objects.get(id=product_id)
    if not product:
        raise CustomApiException(ErrorCodes.NOT_FOUND, "Product not found")
    user = User.objects.get(id=user.id)
    if not user:
        raise CustomApiException(ErrorCodes.NOT_FOUND, "User not found")
    CommentProducts.objects.create(
        product=product,
        comment=comment,
        rating=rating,
        commented_by=user
    )
    return True