  from django.db import models
from django.utils.text import slugify
from decimal import Decimal


class Product(models.Model):

    title = models.CharField(
        max_length = 200
    )
    price = models.DecimalField(max_digits = 6, decimal_places = 2,
        blank = True, null = True 
    )
    base_price = models.DecimalField(max_digits = 6, decimal_places = 2,
        blank = True, null = True
    )
    slug = models.SlugField(
        max_length = 100,
        unique = True,
        blank = True,
        null = True
    )
    amount = models.PositiveIntegerField(
        default = 0
    )

    def __str__(self):
        return self.title
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        if self.base_price == None:
            self.base_price = self.price
        super().save(*args, **kwargs)

class Order(models.Model):

    session_key = models.CharField(
        max_length = 200
    )
    products = models.ManyToManyField(
        Product
    )
    total_price = models.DecimalField(
        max_digits = 6, decimal_places = 2,
        blank = True, null = True
    )
    completed = models.BooleanField(
        default = False
    )

    def calculate_total(self):
        for item in self.products.all():
            self.total_price += item.price
        return self.total_price
    
    def change_quantity(self, slug, sign):
        product = Product.objects.get(slug = slug)
        if sign == "increase":
            more_product = Product.objects.get(slug = slug)
            self.products.add(product)

    def __str__(self):
        return self.session_key
    

def add_slugs():
    from custom.models import Product
    instances = Product.objects.all()
    for instance in instances:
        instance.save()


class Item(models.Model):

    title = models.CharField(
        max_length = 200
    )
    amount = models.PositiveIntegerField(
        default = 0
    )

    price = models.DecimalField(max_digits = 6, decimal_places = 2,
        blank = True, null = True 
    )
    base_price = models.DecimalField(max_digits = 6, decimal_places = 2,
        blank = True, null = True
    )

    slug = models.SlugField(
        max_length = 100,
        unique = True,
        blank = True,
        null = True
    )
    def __str__(self):
        return self.title

    @staticmethod
    def add_slugs():
        from custom.models import Item
        instances = Item.objects.all()
        for instance in instances:
            instance.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        if self.base_price == None:
            self.base_price = self.price
        super().save(*args, **kwargs)
    
class Receipt(models.Model):

    name = models.CharField(
        max_length = 200
    )

    items = models.ManyToManyField(
        Item, through = 'Intermediary'
    )

    total_price = models.DecimalField(
        max_digits = 6, decimal_places = 2,
        default = 0
    )
    completed = models.BooleanField(
        default = False
    )

    @staticmethod
    def create_receipt():
        Receipt.objects.create(name = "receipt1")
        receipt1 = Receipt.objects.get(name = "receipt1")
        receipt1.change_quantity(slug = "fries", sign = "add")
        receipt1.change_quantity(slug = "fries", sign = "add")
        receipt1.change_quantity(slug = "cola", sign = "add")


    def calculate_total(self):
        self.total_price = Decimal(0)
        for item in self.items.all():
            self.total_price += item.price
        self.save()

    def change_quantity(self, slug, sign):
        item = Item.objects.get(slug = slug)
        if sign == "remove":
            Intermediary.objects.filter(item = item, receipt = self).first().delete()
            self.calculate_total()
        elif sign == "add":
            Intermediary.objects.create(item = item, receipt = self)
            self.calculate_total()

    def remove_all_instances(self, slug):
        item = Item.objects.get(slug = slug)
        Intermediary.objects.filter(item = item).delete()

    def __str__(self):
        return f"{self.items.all()}"
    

class Intermediary(models.Model):

    item = models.ForeignKey(Item, on_delete = models.CASCADE)
    receipt = models.ForeignKey(Receipt, on_delete = models.CASCADE)

    