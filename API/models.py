
from django.db import models



class Source(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "api_source"


class Mark(models.Model):
    referred_id = models.IntegerField(null=False, primary_key=True)

    name = models.CharField(max_length=100, db_index=True)

    # source = models.ForeignKey(Source, null=True, on_delete=models.CASCADE)

    # class _Meta:
    #     unique_together = (
    #         ('referred_id', 'source',),
    #     )
    #     pass
    # pass

    class Meta:
        db_table = "api_mark"

    def __str__(self):
        return self.name


class Model(models.Model):
    referred_id = models.IntegerField(null=False, primary_key=True)

    name = models.CharField(max_length=100, db_index=True)
    terms = models.CharField(max_length=50)

    mark = models.ForeignKey(Mark, on_delete=models.CASCADE, null=True, related_name='models')

    class Meta:
        db_table = "api_model"

    def __str__(self):
        return self.name



class TypeCar(models.Model):
    referred_id = models.IntegerField(null=False, primary_key=True)

    name = models.CharField(max_length=150, default='')
    vol = models.CharField(max_length=150, default='')
    terms = models.CharField(max_length=50, default='')
    body_type = models.CharField(max_length=150, default='')
    cyl = models.CharField(max_length=5, default='')
    drive = models.CharField(max_length=150, default='')
    eng = models.CharField(max_length=150, default='')
    fuel = models.CharField(max_length=50, default='')
    hp = models.CharField(max_length=50, default='')
    kw = models.CharField(max_length=50, default='')

    model = models.ForeignKey(Model, on_delete=models.CASCADE, null=True, related_name='types')

    class Meta:
        db_table = "api_typecar"

    def __str__(self):
        return self.name


    # class _Meta:
    #     unique_together = (
    #         ('referred_id', 'source',),
    #     )
    #     pass
    # pass

class SubGroup(models.Model):
    referred_id = models.CharField(max_length=100, null=False, primary_key=True)

    name_subgroup = models.CharField(max_length=150, default='')
    code_subgroup = models.CharField(max_length=100, default='')
    name_group = models.CharField(max_length=150, default='')
    code_group = models.CharField(max_length=100, default='')

    typecar = models.ForeignKey(TypeCar, on_delete=models.CASCADE, null=True, related_name='subgroups')

    class Meta:
        db_table = "api_subgroup"

    def __str__(self):
        return self.name_subgroup







class Part(models.Model):
    # type_id = models.IntegerField(default=None)
    part_number = models.CharField(max_length=30, default='')
    prise = models.CharField(max_length=10, default='')
    retail = models.CharField(max_length=10, default='')
    brend = models.CharField(max_length=50, default='')
    name = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=500, default='')

    referred_id = models.CharField(max_length=100, null=False, primary_key=True)

    subgroup = models.ForeignKey(SubGroup, on_delete=models.CASCADE, null=True, related_name='parts')

    class Meta:
        db_table = "api_part"

    def __str__(self):
        return self.name



class PartDescription(models.Model):
    number = models.CharField(max_length=30, default='')
    prise = models.CharField(max_length=10, default='')
    retail = models.CharField(max_length=10, default='')
    brend = models.CharField(max_length=50, default='')
    name = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=500, default='')

    class Meta:
        db_table = "api_partdescription"

    def __str__(self):
        return self.name


class CrosesByString(models.Model):
    original_number = models.CharField(max_length=30, default='')
    cros_number = models.CharField(max_length=30, default='')

    class Meta:
        db_table = "api_crosesbystring"

    def __str__(self):
        return self.name


class Email(models.Model):

    addres = models.CharField(max_length=100, default='')
    data = models.CharField(max_length=100, default='')

    class Meta:
        db_table = "api_email"

    def __str__(self):
        return self.name






















