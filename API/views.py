from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from API.serializers import MarkDetailsSerializer, ModelCarShortSerializer, TypeCarDetailsSerializer, \
    SubGroupDetailsSerializer, TypeCarShortSerializer, SubGroupShortSerializer, PartDetailsSerializer, \
    PartShortSerializer, MarkShortSerializer, ModelCarDetailsSerializer, EmailShortSerializer, EmailDetailsSerializer
from .helper.parser import ParserMarks, Loginization, ParserModels, ParserTypes, ParserSubGroups, \
    ParserListPartsBySubgroup
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from django.db.models import Q
from django.contrib import admin

from .models import Mark, Model, TypeCar, SubGroup, Part, Email

from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
# from rest_framework.decorators import detail_route
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request








class SelectableSerializerViewSetMixin:
    serializer_list_class = None

    def get_list_serializer_class(self):
        return self.serializer_list_class if self.serializer_list_class is not None else self.get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        many = kwargs.get('many', False)

        serializer_class = self.get_serializer_class() if not many else self.get_list_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class MarkViewSet(SelectableSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkDetailsSerializer
    serializer_list_class = MarkShortSerializer

    pass


class ModelViewSet(SelectableSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelCarDetailsSerializer
    serializer_list_class = ModelCarShortSerializer

    pass

# class TypeCarPars(SelectableSerializerViewSetMixin, viewsets.ModelViewSet):
#     queryset = TypeCar.objects.all()
#     serializer_class = TypeCarShortSerealizer
#     serializer_list_class = TypeCarShortSerializer
#     pass


class TypeViewSet(SelectableSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = TypeCar.objects.all()
    serializer_class = TypeCarDetailsSerializer
    serializer_list_class = TypeCarShortSerializer

    pass

class SubGoupViewSet(SelectableSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = SubGroup.objects.all()
    serializer_class = SubGroupDetailsSerializer
    serializer_list_class = SubGroupShortSerializer

    pass

class PartViewSet(SelectableSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartDetailsSerializer
    serializer_list_class = PartShortSerializer

    pass









class MarksParserView(APIView):

    def post(self, request, format=None):
        marks = ParserMarks()
        marks.get_all_marks_from_site()
        marks.add_marks_to_db()
        return Response({200}, Response.status_code)



class ModelsParserView(APIView):

    def post(self, request, format=None):
        models = ParserModels()
        models.get_all_models_from_site()
        return Response({200}, Response.status_code)



class TypesParserView(APIView):
    # @csrf_exempt
    def post(self, request, format=None):
        types = ParserTypes()
        t = types.get_all_types_from_site()
        print(t)
        return Response({}, Response.status_code)

    pass

class SubGoupsParserView(APIView):

    def post(self, request, format=None):
        subgroups = ParserSubGroups()
        s = subgroups.get_subgroups_from_site()
        print(s)
        return Response({}, Response.status_code)

    pass

class PartsBySubgroupView(APIView):

    def post(self, request, format=None):
        # p = ParserListPartsBySubgroup()
        # p.get_list_parts_by_subgroup_from_site()

        marks = ['ACURA',
                 'AUDI',
                 'BMW',
                 'CHERY',
                 'CHEVROLET',
                 'CHEVROLET(SGM)',
                 'CITROEN',
                 'DACIA',
                 'DAEWOO',
                 'FIAT',
                 'FORD',
                 'FORD USA',
                 'GEELY',
                 'HONDA',
                 'HONDA(GAC)',
                 'HYUNDAI',
                 'INFINITI',
                 'JEEP',
                 'KIA',
                 'LADA',
                 'LANCIA',
                 'LAND',
                 'ROVER',
                 'LEXUS',
                 'MAZDA',
                 'MERCEDES - BENZ',
                 'MINI',
                 'MITSUBISHI',
                 'NISSAN',
                 'NISSAN(DFAC)',
                 'OPEL',
                 'PEUGEOT',
                 'RENAULT',
                 'SAAB',
                 'SEAT',
                 'SKODA',
                 'SMART',
                 'SSANGYONG',
                 'SUBARU',
                 'SUZUKI',
                 'TOYOTA',
                 'TOYOTA(FAW)',
                 'TOYOTA(GAC)',
                 'UZ - DAEWOO',
                 'VOLVO',
                 'VW',
                 'ZAZ']

        p = ParserListPartsBySubgroup()
        p.get_list_parts_by_mark()
        return Response({}, Response.status_code)

    pass




class SendEmailView(APIView):
    def post(self, request, format=None):
        try:

            # send_mail(subject, messages, from_email, to_list, fail_silently)
            # serializer = EmailSerializer(data=request.data)
            # if not serializer.is_valid():
            #     return Response(data=serializer.errors, status=400)
            # data = parse_mail(request, serializer, pk)
            # if data is None:
            #     return Response(data=dict(detail='FAILED'), status=400)
            # email, text_message, html_message = data
            sent = send_mail(
                subject='subject: Thank you for Pre-Order from ',
                message='message: welcome!!!',
                from_email='v.chegarovskiy@gmail.com',
                recipient_list=['v.chegarovskyi@temabit.com'],
                # recipient_list=get_environment().getProperty('SEND_EMAIL_ADDRESS').value,
                fail_silently=True,
                # html_message=html_message,
            )
            if sent == 1:
                return Response(data=dict(detail='Письмо отправлено на вашу почту'), status=201)
            else:
                return Response(data=dict(detail='Ошибка отправки письма'), status=400)
        except Exception as e:
            return Response(data=dict(detail='Критическая ошибка', message=repr(e)), status=400)

    class Meta:
        pass

    pass


class SendEmailViewSet(SelectableSerializerViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Email.objects.all()
    serializer_class = EmailDetailsSerializer
    serializer_list_class = EmailShortSerializer

    pass



class DeleteDuplicatesPartsView(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.delete_duplicate_parts_and_update_db()
        # marks = ParserMarks()
        # marks.get_all_marks_from_site()
        # marks.add_marks_to_db()
        return Response({200}, Response.status_code)
        pass

class GetCrosesParts(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.get_cros_numbers()

        return Response({200}, Response.status_code)
        pass

class SetTimeTable(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.setDataToTimeTable()

        return Response({200}, Response.status_code)
        pass

class GetDescription(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.getDescriptionParts()

        return Response({200}, Response.status_code)
        pass

class ClearQuantity(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.clearQuontityInDescriptionTable()

        return Response({200}, Response.status_code)
        pass


class ClearPrise(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.clearPriseInPartDescriptionTable()

        return Response({200}, Response.status_code)
        pass

class GetDescriptionsParts(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.get_images_and_description_part_and_save_to_db()

        return Response({200}, Response.status_code)
        pass

class GetQuontityParts(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.get_quontity_part()

        return Response({200}, Response.status_code)
        pass

class UpdatePriseParts(APIView):

    def post(self, request, format=None):
        parts = ParserListPartsBySubgroup()
        parts.update_price_part()

        return Response({200}, Response.status_code)
        pass

class Inject(APIView):
    def post(self, request, format=None):
        q = ParserListPartsBySubgroup()
        # q.testQ()
        q.update_price_quick()

        return Response({200}, Response.status_code)
        pass
    pass

class Search(APIView):
    def post(self, request, format=None):
        q = ParserListPartsBySubgroup()
        q.testQ()

        return Response({200}, Response.status_code)
        pass
    pass


