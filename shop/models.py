from django.db import models
from account.models import User

# Create your models here.
def user_shop_file_path(instance, filename):
    """
    Returns the file path to upload the file to MEDIA_ROOT/user_{id}/shop/ directory.
    """
    return 'user_{0}/shop/{1}'.format(instance.user.id, filename)



class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to=user_shop_file_path, blank=True, null=True, verbose_name='Image')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    
    
    def __str__(self):
        return self.name


class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{}:{}".format(self.product.name, self.id)

    def update_quantity(self, quantity):
        self.quantity = self.quantity + quantity
        self.save()

    def total_cost(self):
        return self.quantity * self.price


class Order(models.Model):
    name = models.CharField(max_length=191)
    email = models.EmailField()
    postal_code = models.IntegerField()
    address = models.CharField(max_length=191)
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.id, self.email)

    def total_cost(self):
        return sum([ li.cost() for li in self.lineitem_set.all() ] )


class LineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}:{}".format(self.product.name, self.id)

    def cost(self):
        return self.price * self.quantity