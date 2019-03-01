from rest_framework import serializers
from .models import Mark, Model, TypeCar, SubGroup, Part, Email


class MarkShortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mark
        fields = ('url', 'name', 'referred_id')

        pass
    pass


class ModelCarShortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Model
        fields = ('url', 'name', 'terms', 'referred_id')

        pass
    pass


class TypeCarShortSerealizer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TypeCar
        fields = ('url', 'name', 'vol', 'terms', 'body_type', 'cyl', 'drive', 'eng', 'fuel', 'hp', 'kw', 'referred_id')

        pass
    pass


class SubGroupShortSerealizer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SubGroup
        fields = ('url', 'name_subgroup', 'code_subgroup', 'name_group', 'code_group', 'referred_id')

        pass
    pass

class PartShortSerealizer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Part
        fields = ('url', 'part_number', 'prise', 'retail', 'brend', 'name', 'description', 'referred_id')

        pass
    pass

class EmailShortSerealizer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Email









class MarkDetailsSerializer(serializers.HyperlinkedModelSerializer):
    models = ModelCarShortSerializer(many=True)

    class Meta:
        model = Mark
        fields = ('url', 'name', 'referred_id', 'models')
        pass
    pass


class ModelCarDetailsSerializer(serializers.HyperlinkedModelSerializer):
    types = TypeCarShortSerealizer(many=True)
    mark = MarkShortSerializer()

    class Meta:
        model = Model
        fields = ('url', 'name', 'terms', 'referred_id', 'mark_id', 'mark', 'types')

        pass
    pass

class TypeCarDetailsSerializer(serializers.HyperlinkedModelSerializer):
    subgroups = SubGroupShortSerealizer(many=True)
    model = ModelCarShortSerializer()

    class Meta:
        model = TypeCar
        fields = ('url', 'name', 'vol', 'terms', 'body_type', 'cyl', 'drive', 'eng', 'fuel', 'hp', 'kw', 'referred_id', 'model', 'subgroups')

        pass
    pass

class SubGroupDetailsSerealizer(serializers.HyperlinkedModelSerializer):
    parts = PartShortSerealizer(many=True)
    typecar = TypeCarShortSerealizer()

    class Meta:
        model = SubGroup
        fields = ('url', 'referred_id', 'name_subgroup', 'code_subgroup', 'name_group', 'code_group', 'typecar','parts')

        pass
    pass



class PartDetailsSerealizer(serializers.HyperlinkedModelSerializer):

    subgoups = SubGroupShortSerealizer()

    class Meta:
        model = Part
        fields = ('url', 'part_number', 'brend', 'subgoups')

        pass
    pass

class EmailDetailsSerializer(serializers.HyperlinkedModelSerializer):
    emails = EmailShortSerealizer(many=True)

    class Meta:
        model = Email
        fields = ('addres', 'data')
        pass
    pass












