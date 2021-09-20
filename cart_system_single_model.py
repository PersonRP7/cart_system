from django.db import models
from decimal import Decimal

class CartProducts(models.Model):
    # Base repository of product instances
    title = models.CharField(max_length = 100)
    
    cijena_gotovina = models.DecimalField(max_digits = 6, decimal_places = 2,
        blank = True, null = True
    )

    cijena_kartica = models.DecimalField(max_digits = 6, decimal_places = 2,
        blank = True, null = True
    )
    
    amount = models.PositiveIntegerField(
        blank = True, null = True, default = 0
    )

    slug = models.SlugField(
        max_length = 100,
        unique = True,
        blank = True,
        null = True
    )

    def __str__(self):
        return self.title

class Receipt(models.Model):

    name = models.CharField(
        max_length = 200
    )

    items = models.ManyToManyField(
        CartProducts, through = 'Intermediary'
    )

    total_price = models.DecimalField(
        max_digits = 6, decimal_places = 2,
        default = 0
    )
    completed = models.BooleanField(
        default = False
    )

    # @staticmethod
    # def create_receipt():
    #     Receipt.objects.create(name = "receipt1")
    #     receipt1 = Receipt.objects.get(name = "receipt1")
    #     receipt1.change_quantity(slug = "fries", sign = "add")
    #     receipt1.change_quantity(slug = "fries", sign = "add")
    #     receipt1.change_quantity(slug = "cola", sign = "add")


    def calculate_total(self):
        self.total_price = Decimal(0)
        for item in self.items.all():
            self.total_price += item.cijena_kartica
        self.save()
		
    def calculate_per_slug(self):
		#subtotal
        new_list = []
        new_dictionary = {}
        for value in self.items.all():
            if new_list and new_list[-1][0] == value:
                new_list[-1].append(value)
            else:
                new_list.append([value])
        for i in new_list:
            if len(i) > 1:
                for j in i:
                    # new_dictionary[j.title] = j.cijena_kartica * len(i)
                    # new_dictionary[j.title] = f"{j.cijena_kartica * len(i)}. Amount: {len(i)}."
                    new_dictionary[j.title] = [f"{j.cijena_kartica * len(i)}", len(i)]
            else:
                # print(i[0].title)
                # use a list to hold multiple values
                # new_dictionary[i[0].title] = f"{i[0].cijena_kartica}"
                new_dictionary[i[0].title] = [f"{i[0].cijena_kartica}", len(i)]
        print(new_dictionary)

    def create_description(self):
        new_str = ""
        for i in self.items.all():
            new_str += f"{i.__str__()} "
        return new_str

    def change_quantity(self, slug, sign):
        item = CartProducts.objects.get(slug = slug)
        if sign == "remove":
            Intermediary.objects.filter(item = item, receipt = self).first().delete()
            self.calculate_total()
        elif sign == "add":
            Intermediary.objects.create(item = item, receipt = self)
            self.calculate_total()

    def remove_all_instances(self, slug):
        item = CartProducts.objects.get(slug = slug)
        Intermediary.objects.filter(item = item).delete()

    def __str__(self):
        return f"{self.items.all()}"

class Intermediary(models.Model):

    item = models.ForeignKey(CartProducts, on_delete = models.CASCADE)
    receipt = models.ForeignKey(Receipt, on_delete = models.CASCADE)