from django import forms
from .models import Order,Product, CartItem


class CartForm(forms.Form):
    quantity = forms.IntegerField(initial='1')
    user_id = forms.IntegerField(widget=forms.HiddenInput)
    product_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CartForm, self).__init__(*args, **kwargs)


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('paid',)

        widgets = {
            'address': forms.Textarea(attrs={'row': 5, 'col': 8}),
        }

class ProductForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = Product
        fields = ['name', 'price', 'slug', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(initial='1')

    class Meta:
        model = CartItem
        fields = ('quantity',)
