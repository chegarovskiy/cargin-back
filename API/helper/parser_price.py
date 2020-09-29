import time
import random
import requests
import requests.cookies
from urllib.parse import urlencode
from ..models import Mark,\
    Model, TypeCar, SubGroup, Part, PartNumbersWithOutDuplicates,\
    PartDescription, Imege, CrosesByString, TimeData
from django.db.models import Q
import re


# вспомагательный клас для парсинга и обновления цен запчастей которые есть в наличии
class Parser_price():
    def __init__(self, cookies, headers, ostatok):
        self.cookies = cookies
        self.headers = headers
        self.ostatok = ostatok

    def search_main(self):

        while len(self.ostatok) > 0:
            first_in_ostatok = self.ostatok[0]
            print('first_in_ostatok', first_in_ostatok)
            query_for_cross = ''
            origin = ''
            list_croces = []

                #Если есть крос, находим оригин номер
            if CrosesByString.objects.filter(cros_number=first_in_ostatok).exists():
                origin = CrosesByString.objects.values_list('original_number', flat=True).filter(
                    cros_number=first_in_ostatok)[:1]

                query_for_cross = dict(code=origin[0])
                #Поиск по подгруппе и марке
                # self.ostatok.remove(first_in_ostatok)
                print('1', 'first_in_ostatok', first_in_ostatok, 'query_for_cross', query_for_cross, len(self.ostatok))
                # Поиск по в кросах
                self.search_by_cross(query_for_cross)
                # self.ostatok.remove(first_in_ostatok)


            if PartNumbersWithOutDuplicates.objects.filter(part_number=first_in_ostatok).exists():
                print('2', 'first_in_ostatok', first_in_ostatok, 'query_for_cross', query_for_cross, len(self.ostatok))
                self.search_by_subgroup_and_mark(first_in_ostatok)
                # self.ostatok.remove(first_in_ostatok)


            if CrosesByString.objects.filter(original_number=first_in_ostatok).exists():
                print('3', 'first_in_ostatok', first_in_ostatok, 'query_for_cross', query_for_cross, len(self.ostatok))
                self.search_by_subgroup_and_mark(first_in_ostatok)

            if first_in_ostatok in self.ostatok:
                self.ostatok.remove(first_in_ostatok)
                print('__________________________________________________________________________________', first_in_ostatok)



            print(len(self.ostatok))




            # elif CrosesByString.objects.filter(original_number=first_in_ostatok).exists():
            #     origin = first_in_ostatok
            #     query_for_cross = dict(code=first_in_ostatok)
            #     # self.ostatok.remove(first_in_ostatok)
            #     print('2', 'origin', origin, 'query_for_cross', query_for_cross, len(self.ostatok))
            #     self.search_by_subgroup_and_mark(origin[0])
            #
            #
            # elif Part.objects.filter(part_number=first_in_ostatok).exists():
            #     origin = Part.objects.values_list('part_number', flat=True).filter(
            #         part_number=first_in_ostatok)[:1]
            #     query_for_cross = dict(code=origin[0])
            #     # self.ostatok.self.search_by_subgroup_and_mark(origin[0])(first_in_ostatok)
            #     print('3', 'origin', origin, 'query_for_cross', query_for_cross, len(self.ostatok))
            #     self.search_by_subgroup_and_mark(origin[0])
            #
            # else:
            #     print('4', "!!!!!не обработанный кейс. ", first_in_ostatok, len(self.ostatok))

        pass



    # если запчасть есть в Part находим ЕЕ и другие по подгруппе и марке авто
    def search_by_subgroup_and_mark(self, origin):
        print(Part.objects.filter(part_number=origin).exists())

        if Part.objects.filter(part_number=origin).exists():

            subgroup = Part.objects.values_list('subgroup_id', flat=True).filter(part_number=origin)[:1]
            print('subgroup', subgroup)
            # ищем нейм сабгруп айди для запроса
            text_subgroup = SubGroup.objects.values_list('name_subgroup', flat=True).filter(
                referred_id=subgroup[0])[:1]
            # print(text_subgroup[0])
            # print(subgroup['subgroup_id'])
            # print('----')
            [a, b] = re.split(r'-', subgroup[0])

            query = dict(code=b, group=text_subgroup[0])

            print(query)
            test = urlencode(query)
            response = requests.get(
                'http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test),
                cookies=self.cookies, headers=self.headers)
            print('!!!!!', 'http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test))
            # print(response.json())
            time.sleep(.3)

            if 200 <= response.status_code < 400:
                print(response.status_code)
                parts_by_type_and_subgroup = dict(response.json())
                # print(parts_by_type_and_subgroup)
                for key, value in parts_by_type_and_subgroup.items():
                    try:
                        if key == 'items' and len(value) > 0:
                            print(len(value))
                            # print(value)

                            for part in list(value):
                                # print(part['Item'])
                                if part['Item'] in self.ostatok:
                                    try:
                                        obj = PartDescription.objects \
                                            .filter(number=part['Item']) \
                                            .update(retail=part['Retail'], prise=part['Price'])

                                        self.ostatok.remove(part['Item'])
                                        print("!!!!!!!!!!ostatok-", len(self.ostatok), 'update:', part['Item'])

                                    except:
                                        print('exeption: can`t get number in PartDescription')
                                else:
                                    pass
                                    # print(part['Item'], '- не целевая запчасть')
                        else:
                            pass
                            # ToDo: можем вытянуть картинки от сюда
                            # print(key, len(value))

                    except:
                        print('somsing with parts')
        else:
            print('не нашли в таблице запчастей. халепа')



    def search_by_cross(self, query_for_cross):
        # парсим ценник в крос-номерах текущего номера
        try:
            response = requests.get(
                'http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query_for_cross)),
                cookies=self.cookies, headers=self.headers)
            print('-----кросы',
                  'http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query_for_cross)))

            time.sleep(.3)
            if (len(response.json()['items']) > 0):

                for kross in response.json()['items']:
                    if kross['Item'] in self.ostatok:
                        try:
                            obj = PartDescription.objects \
                                .filter(number=kross['Item']) \
                                .update(retail=kross['Retail'], prise=kross['Price'])

                            self.ostatok.remove(kross['Item'])
                            print("----------ostatok-", len(self.ostatok), 'update:', kross['Item'])

                        except:
                            print('exeption: can`t update prise part')
            else:
                print('len response - ', len(response.json()['items']))

        except:
            print("-exeption")



    def search_by_input(self, parts):
        # Прямой поиск через интпут сайта. Ограничен по колличеству запросов в сутки. 800 шт.
        # Использовать в саммую последнюю очередь. Рабочий.
        # Если запчасть в PartDescription без цены, парсим цену
        counter = 0
        count = 0
        len_parts_arr = len(parts)

        for part in parts:
            # return true or false
            isWithPrise = PartDescription.objects.values('number', 'prise', 'retail').filter(number=part) \
                .exclude(prise__isnull=True) \
                .exclude(prise__exact='') \
                .exclude(retail__isnull=True) \
                .exclude(retail__exact='')

            if not isWithPrise:
                print('get price')
                counter += 1

                curr = str(part).replace('.', '')
                curr = curr.replace(' ', '')
                curr = curr.replace('-', '')
                curr = curr.replace('/', '')
                curr = curr.replace('_', '')
                curr = curr.replace('(', '')
                curr = curr.replace(')', '')

                query = dict(grp='', item=curr)
                time.sleep(.300)
                if counter % 30 == 0:
                    time.sleep(random.randint(5, 10))

                response = requests.get(
                    'http://b2b.ad.ua/api/catalog/search?{query}'.format(query=urlencode(query)),
                    cookies=self.cookies,
                    headers=self.headers)
                print(part)
                print('http://b2b.ad.ua/api/catalog/search?{query}'.format(query=urlencode(query)))
                if 200 <= response.status_code < 400:
                    print(response.status_code)
                    for k, v in dict(response.json()).items():
                        # get data for part and save
                        if (k == 'items' and len(v) > 0):
                            for spare in v:
                                co = parts.filter(number=spare['Item']).count()
                                if co == 1:
                                    count += 1
                                    print(count)
                                    try:
                                        obj = PartDescription.objects \
                                            .filter(number=spare['Item']) \
                                            .update(retail=spare['Retail'], prise=spare['Price'])
                                        print('обновили колличество - count: ' + count)
                                    except:
                                        print('exeption: can`t get number in PartDescription')
                                else:
                                    print('не нужный номер. не обновляем цену')
            else:
                print('price exist')
