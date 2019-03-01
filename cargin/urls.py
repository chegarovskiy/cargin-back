from django.conf.urls import url, include
from django.urls import re_path
from django.contrib import admin
from django.views.generic import TemplateView
from rest_framework import routers


from API import views as views_API


api_router = routers.DefaultRouter()
api_router.register(r'marks', views_API.MarkViewSet)
api_router.register(r'models', views_API.ModelViewSet)
api_router.register(r'typecar', views_API.TypeViewSet)
api_router.register(r'subgroups', views_API.SubGoupViewSet)
api_router.register(r'parts', views_API.PartViewSet)
api_router.register(r'sendemail', views_API.SendEmailViewSet)




# urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^__api__/', include(api_router.urls)),

    # re_path(r'^parser/marks/start', views_API.MarksParserView.as_view()),


    re_path(r'^parser/marks/', views_API.MarksParserView.as_view()),
    re_path(r'^parser/models/', views_API.ModelsParserView.as_view()),
    re_path(r'^parser/types/', views_API.TypesParserView.as_view()),
    re_path(r'^parser/subgroups/', views_API.SubGoupsParserView.as_view()),
    re_path(r'^parser/partsbysubgroups/', views_API.PartsBySubgroupView.as_view()),
    re_path(r'^parser/sendemail/', views_API.SendEmailView.as_view()),
]


