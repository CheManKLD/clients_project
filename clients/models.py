from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Organization(models.Model):
    client_name = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('client_name', 'name')

    def __str__(self):
        return f'{self.client_name}: {self.name}'


class Bill(models.Model):
    client_org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    sum = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateField()

    class Meta:
        unique_together = ('client_org', 'number')

    def __str__(self):
        return f'{self.client_org}: № {self.number}, sum {self.sum}'

