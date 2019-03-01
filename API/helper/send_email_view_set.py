from django.core.mail import send_mail
from django.template import Context, loader
from django.conf import settings
from rest_framework.decorators import detail_route
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request
from rest_framework.response import Response
# from environment.settings import get_environment

import sys
from typing import Optional, Tuple


# from ..serializers.email_serializer import EmailData, EmailSerializer

# def parse_base(request: Request, serializer: EmailSerializer) -> EmailData:
# 	data = serializer.create(serializer.validated_data)  # type: EmailData
# 	# data.referrer = request.META.get('HTTP_REFERER')
# 	return data
#
# MESSAGES = dict(
# 	reserve=dict(
# 		title='Бронювання',
# 		parser=parse_base,
# 		html_template='base_email.html',
# 		text_template='base_email.txt'
# 	),
# 	tour=dict(
# 		title='Замовлення туру',
# 		parser=parse_base,
# 		html_template='base_email.html',
# 		text_template='base_email.txt'
# 	),
# 	corporate=dict(
# 		title='Корпоративний відпочинок',
# 		parser=parse_base,
# 		html_template='base_email.html',
# 		text_template='base_email.txt'
# 	),
# )
#
# def parse_mail(request: Request, serializer: EmailSerializer, pk: str) -> Optional[Tuple[EmailData, str, str]]:
# 	info = MESSAGES.get(pk) # type: Optional[dict]
# 	if info is None:
# 		return None
# 	title = info.get('title')
# 	parser = info.get('parser')
# 	text_template_name = info.get('text_template')
# 	html_template_name = info.get('html_template')
# 	if isinstance(title, str) and callable(parser) and isinstance(text_template_name, str) and isinstance(html_template_name, str):
# 		email_data = parser(request, serializer) # type: EmailData
# 		email_data.title = title
# 		context = Context(dict(
# 			data=email_data,
# 			request=request
# 		))
# 		return (
# 			email_data,
# 			loader.render_to_string(text_template_name, context=context, request=request),
# 			loader.render_to_string(html_template_name, context=context, request=request),
# 		)
# 	else:
# 		return None


class SendEmailViewSet(ViewSet):
	
	@detail_route(methods=['post'])
	def send(self, request: Request, pk: str):
		try:
			serializer = EmailSerializer(data=request.data)
			if not serializer.is_valid():
				return Response(data=serializer.errors, status=400)
			data = parse_mail(request, serializer, pk)
			if data is None:
				return Response(data=dict(detail='FAILED'), status=400)
			email, text_message, html_message = data
			sent = send_mail(
				subject=email.title,
				message=text_message,
				from_email=settings.EMAIL_HOST_USER,
				recipient_list=get_environment().getProperty('SEND_EMAIL_ADDRESS').value,
				fail_silently=True,
				html_message=html_message,
			)
			if sent == 1:
				return Response(data=dict(detail='Готово'), status=201)
			else:
				return Response(data=dict(detail='Помилка відправки листа'), status=400)
		except Exception as e:
			return Response(data=dict(detail='Критична помилка', message=repr(e)), status=400)
		
	class Meta:
		pass
	
	pass


__all__ = [SendEmailViewSet.__name__]