from django.contrib import admin
from django.http import HttpResponse

from API.models import Mark, Model, TypeCar, SubGroup, Part
from API.helper.parser import ParserMarks

# def parsmarks(modeladmin, request, queryset):
#     try:
#         marks = ParserMarks()
#         marks.get_all_marks_from_site()
#         marks.add_marks_to_db()
#         return HttpResponse(content=None, status=201)
#     except:
#         pass
#
# # class Parser(admin.ModelAdmin):
# #
# #     actions = [parsmarks]


class MarkModelAdmin(admin.ModelAdmin):

    class Meta:
        model = Mark

        pass

    pass


admin.site.register(Mark, MarkModelAdmin)







class ModelModelAdmin(admin.ModelAdmin):

    fields = ('name', 'terms')
    list_display = ('name', 'terms')

    class Meta:
        model = Model
admin.site.register(Model, ModelModelAdmin)


class TypeCarModelAdmin(admin.ModelAdmin):
    fields = ('name', 'vol', 'terms', 'body_type', 'cyl', 'drive', 'eng', 'fuel', 'hp', 'kw')
    list_display = ('name', 'vol', 'terms', 'body_type', 'cyl', 'drive', 'eng', 'fuel', 'hp', 'kw')

    class Meta:
        model = TypeCar
admin.site.register(TypeCar, TypeCarModelAdmin)


class SubgroupModelAdmin(admin.ModelAdmin):
    fields = ('name_subgroup', 'name_group', 'referred_id')
    list_display = ('name_subgroup', 'name_group', 'referred_id')
    class Meta:
        model = SubGroup
admin.site.register(SubGroup, SubgroupModelAdmin)


class PartModelAdmin(admin.ModelAdmin):
    fields = ('part_number', 'prise', 'retail', 'brend', 'name', 'description', 'referred_id')
    list_display = ('part_number', 'prise', 'retail', 'brend', 'name', 'description', 'referred_id')
    class Meta:
        model = Part
admin.site.register(Part, PartModelAdmin)





