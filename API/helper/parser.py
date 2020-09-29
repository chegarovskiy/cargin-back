import re
import time
from django.db.models import QuerySet
from django.db.models import Manager

from API.helper.parser_price import Parser_price
from ..models import Mark, Model, TypeCar, SubGroup, Part, PartNumbersWithOutDuplicates, PartDescription, Imege, CrosesByString, TimeData
import random
import json
from collections import namedtuple
# import pypyodbc
import requests
import requests.cookies
from http.cookies import SimpleCookie
from urllib.parse import urlencode
import urllib
import certifi
import os
from django.db.models import Q
from django.db.models import Count, Max

#response = requests.post('http://b2b.ad.ua/Account/Login?ReturnUrl=%2F', data={'ComId': '15', 'UserName': '10115', 'Password': 'e89f1a11', 'RememberMe': False, '__RequestVerificationToken': '<TOKEN>'})

class Loginization:
    def __init__(self):
        self.cookies = requests.cookies.RequestsCookieJar()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        }
        self.token = None
        response = requests.get('http://b2b.ad.ua/', headers=self.headers, verify=False)

        if response.status_code == 200:
            for history_response in response.history:
                self.cookies.update(history_response.cookies)
            self.cookies.update(response.cookies)
            content = response.text
            # print(response.text)
            match = re.search(
                r'<input\s+name="__RequestVerificationToken"\s+type="hidden"\s+value="(?P<value>[a-zA-Z0-9_-]+)"\s*/>',
                content,
            )
            if match:
                self.token = match.groupdict().get('value')
                pass
            pass

        response = requests.post(
            'http://b2b.ad.ua/Account/Login?ReturnUrl=%2F',
            data={
                'ComId': '15',
                'UserName': '10115',
                'Password': 'e89f1a11',
                'RememberMe': False,
                '__RequestVerificationToken': self.token,
            },
            cookies=self.cookies,
            headers=self.headers,
        )
        # print(cookies)
        # print(headers)
        if 200 <= response.status_code < 400:
            for history_response in response.history:
                self.cookies.update(history_response.cookies)
            self.cookies.update(response.cookies)
            content = response.text
            # print(response.text)
            print('Login:', response.status_code, response.reason)
        else:
            print('Login failed with', response.status_code, response.reason)
            exit(1)



class ParserMarks(Loginization):
    def __init__(self):
        super(ParserMarks, self).__init__()
        self.mark_dict = dict()

    def get_all_marks_from_site(self):
        response = requests.get('http://b2b.ad.ua/api/catalog/marks', cookies=self.cookies, headers=self.headers)
        if 200 <= response.status_code < 400:
            all_marks_list = list(response.json())
            clearArrMark = ['ACURA',
                            'AUDI',
                            'BMW',
                            'CHERY',
                            'CHEVROLET',
                            'CHEVROLET (SGM)',
                            'CITROEN',
                            'DACIA',
                            'DAEWOO',
                            'FIAT',
                            'FORD',
                            'FORD USA',
                            'GEELY',
                            'HONDA',
                            'HONDA (GAC)',
                            'HYUNDAI',
                            'INFINITI',
                            'ISUZU',
                            'LANCIA',
                            'LAND ROVER',
                            'LEXUS',
                            'MAZDA',
                            'MERCEDES-BENZ',
                            'MINI',
                            'MITSUBISHI',
                            'NISSAN',
                            'NISSAN (DFAC)',
                            'OPEL',
                            'PEUGEOT',
                            'RENAULT',
                            'SEAT',
                            'SKODA',
                            'SMART',
                            'SSANGYONG',
                            'SUBARU',
                            'SUZUKI',
                            'TOYOTA',
                            'TOYOTA (FAW)',
                            'TOYOTA (GAC)',
                            'VOLVO',
                            'VW',
                            'ZAZ',
                            ]
            for current_mark in all_marks_list:
                if current_mark['Name'] in clearArrMark:
                    self.mark_dict[current_mark['MARK_ID']] = current_mark['Name']

                # верменный ограничитель на колличество спаршенных марок
                # if current_mark['Name'] == 'ZAZ':
                #         # or current_mark['Name'] == 'LEXUS'\
                #         # or current_mark['Name'] == 'BMW'\
                #
                #     self.mark_dict[current_mark['MARK_ID']] = current_mark['Name']
                # else:
                #     continue
        print(self.mark_dict.__len__())
        return self.mark_dict

    def add_marks_to_db(self):
        try:
            marks = self.mark_dict
            for k, v in dict(marks).items():
                current_mark = Mark()
                current_mark.name = v
                current_mark.referred_id = k
                current_mark.save()
            return 1
        except:
            return 0

    def get_all_mark(self):

        m = Mark.objects.all()
        return m



class ParserModels(Loginization):
    def __init__(self):
        super(ParserModels, self).__init__()
        self.model_dict = dict()


    def get_all_models_from_site(self):
        try:
            for m in list(Mark.objects.all()):
                query = dict(code=m.referred_id)
                response = requests.get('http://b2b.ad.ua/api/catalog/models?{query}'.format(query=urlencode(query)),
                                        cookies=self.cookies, headers=self.headers)
                all_models_list = list(response.json())
                for current_mod in all_models_list:
                    mod = Model()
                    mod.name = current_mod['MODEL']
                    mod.referred_id = current_mod['MOD_ID']
                    mod.terms = current_mod['MOD_TERMS']
                    mod.mark_id = current_mod['MARK_ID']
                    mod.save()
            return 1
        except:
            return 0

class ParserTypes(Loginization):
    def __init__(self):
        super(ParserTypes, self).__init__()
        self.type_dictionary = dict()

    def get_all_types_from_site(self):
        models_quontity = len(Model.objects.all())
        models_all = Model.objects.all()
        counter = 0
        for mod in models_all:
            print(counter, ' from ', models_quontity, " mod - ", mod)
            query = dict(code=mod.referred_id)
            counter += 1
            if counter % 10 == 0:
                time.sleep(random.randint(8, 13))
            time.sleep(random.randint(1, 2))
            # print('code=mod.referred_id', mod.referred_id)
            response = requests.get('http://b2b.ad.ua/api/catalog/types?{query}'.format(query=urlencode(query)),
                                    cookies=self.cookies, headers=self.headers)
            if 200 <= response.status_code < 400:
                print("response.status_code", response.status_code)
                try:
                    for current_type in list(response.json()):
                        print('current_type', current_type)

                        # if not TypeCar.objects.filter(referred_id=current_type['typ_id']).exists():
                        typ = TypeCar()
                        typ.name = current_type['name_full']
                        typ.referred_id = current_type['typ_id']
                        typ.model_id = current_type['MOD_ID']
                        typ.body_type = current_type['body']
                        typ.cyl = current_type['cyl']
                        typ.drive = current_type['drive']
                        typ.eng = current_type['eng']
                        typ.fuel = current_type['fuel']
                        typ.hp = current_type['hp']
                        typ.kw = current_type['kw']
                        typ.terms = current_type['terms']
                        typ.vol = current_type['name']

                        typ, created = TypeCar.objects.update_or_create(
                            referred_id=int(current_type['typ_id']),
                                        defaults={
                                            'referred_id': current_type['typ_id'],
                                            'name': typ.name,
                                            'referred_id': typ.referred_id,
                                            'model_id': typ.model_id,
                                            'body_type': typ.body_type,
                                            'cyl': typ.cyl,
                                            'drive': typ.drive,
                                            'eng': typ.eng,
                                            'fuel': typ.fuel,
                                            'hp': typ.hp,
                                            'kw': typ.kw,
                                            'terms': typ.terms,
                                            'vol': typ.vol
                                        }
                        )

                        # typ.save()
                        # print(current_type['name_full'])
                        # else:
                        #     print(mod.referred_id)

                except Exception as err:
                    print(response.status_code, err)
                    return 'exeption'
            else:
                return 'last id model is: ' + mod.referred_id
        return response.status_code



class ParserSubGroups(Loginization):
    def __init__(self):
        super(ParserSubGroups, self).__init__()
    # готовый метод.
    def get_subgroups_from_site(self):
        counter = 0
        all_types = TypeCar.objects.all()
        allTypeCar = len(all_types)
        for current_type in all_types:
            counter += 1
            try:
                # если нашли в таблице подгруп по типу ищем или все подгрупы и групы спаршены
                obj = SubGroup.objects.filter(typecar_id=current_type.referred_id)
                if(obj.count() == 0):
                    if counter % 30 == 0:
                        time.sleep(random.randint(3, 8))
                    query = dict(code=str(current_type.referred_id))
                    print(counter, 'from', allTypeCar, 'http://b2b.ad.ua/api/catalog/groups?{query}'.format(query=urlencode(query)))
                    response = requests.get('http://b2b.ad.ua/api/catalog/groups?{query}'.format(query=urlencode(query)), cookies=self.cookies, headers=self.headers)
                    time.sleep(random.randint(3, 4))
                    if 200 <= response.status_code < 400:
                        all_grups = dict(response.json())
                        for key, value in all_grups.items():
                            if (key == 'groups'):
                                for cur_grpup in list(value):
                                    for curr_subgrup in list(cur_grpup['subgrp']):
                                        try:
                                            obj = SubGroup.objects.get_or_create(
                                                referred_id=str(curr_subgrup['code']) +'-'+ str(current_type.referred_id),
                                                defaults={'code_group': cur_grpup['code'],
                                                          'name_group': cur_grpup['name'],
                                                          'code_subgroup': curr_subgrup['code'],
                                                          'name_subgroup': curr_subgrup['name'],
                                                          'typecar_id': int(current_type.referred_id)
                                                          }
                                                )
                                            print("сохранили")
                                        except:
                                            print("не сохранили")

            except:
                print('exept')
                pass


class ParserListPartsBySubgroup(Loginization):
    def __init__(self):
        super(ParserListPartsBySubgroup, self).__init__()

    def get_list_parts_by_subgroup_from_site(self):
        counter = 0
        for curr_subgrp in SubGroup.objects.values('typecar_id', 'name_subgroup', 'code_subgroup', 'referred_id').\
                order_by('referred_id'):
            counter += 1
            # print(curr_subgrp['name_subgroup'], curr_subgrp['typecar_id'])

            refsub = curr_subgrp['referred_id']

            text = curr_subgrp['name_subgroup']
            code = curr_subgrp['typecar_id']
            query = dict(code=code, group=text)
            test = urlencode(query)
            print(test)

            try:
                obj = Part.objects.filter(subgroup_id=refsub)

                if obj.count() > 0:
                    print('exist obj > 0', obj.count(), counter)
                if obj.count() == 0:
                    print('exist obj == 0', obj.count())
                    # if counter % 10 == 0:
                    #     time.sleep(random.randint(6, 9))
                    #     print('quantity requests:',  counter)

                    response = requests.get(
                        'http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test),
                        cookies=self.cookies, headers=self.headers)
                    print('запрос: ', counter, response.status_code)
                    time.sleep(random.randint(1, 2))

                    if 200 <= response.status_code < 400:
                        parts_by_type_and_subgroup = dict(response.json())
                        for key, value in parts_by_type_and_subgroup.items():

                            try:
                                if key == 'items' and len(value) > 0:
                                    for part in list(value):
                                        current_part = Part()

                                        current_part.part_number = part['Item']
                                        current_part.prise = part['Price']
                                        current_part.retail = part['Retail']
                                        current_part.brend = part['Бренд']
                                        current_part.name = part['Название']
                                        current_part.description = part['Описание']

                                        curr = str(part['Item']).replace('.', '')
                                        curr = curr.replace(' ', '')
                                        curr = curr.replace('-', '')
                                        curr = curr.replace('/', '')
                                        curr = curr.replace('_', '')
                                        curr = curr.replace('(', '')
                                        curr = curr.replace(')', '')

                                        current_part.referred_id = str(
                                            curr_subgrp['referred_id']) + '-' + str(curr)
                                        current_part.subgroup_id = curr_subgrp['referred_id']

                                        current_part.save()
                                        print('save', current_part.part_number, current_part.subgroup_id)

                                        response.close()

                            except:
                                print('ex2', key, value)
                                response.close()
                                pass
            except:
                print('!!!!!!!!!!ObjectDoesNotExist!!!!!!!!!!')




    def get_list_parts_by_mark(self):
        clear = lambda: os.system('cls')
        # print('curr_mark', self.mark)
        counter = 0
        curr_mark = Mark.objects.get(name='TOYOTA')
        print('curr_mark', curr_mark)


        curr_models = Model.objects.values('referred_id', 'name', 'mark_id').filter(mark_id=curr_mark)


        for curr_model in curr_models:
            curr_types = TypeCar.objects.values('name', 'model_id', 'referred_id').filter(model_id=curr_model['referred_id'])



            for curr_type in curr_types:
                curr_subgrps = SubGroup.objects.values('typecar_id', 'name_subgroup', 'code_subgroup', 'referred_id').filter(typecar_id=curr_type['referred_id'])



                for curr_subgrp in curr_subgrps:
                    counter += 1
                    print(counter)
                    text = curr_subgrp['name_subgroup']
                    code = curr_subgrp['typecar_id']
                    refsub = curr_subgrp['referred_id']
                    query = dict(code=code, group=text)
                    test = urlencode(query)

                    print('!!! curr_mark - curr_model - curr_type - curr_subgrp!!!', curr_mark, curr_model, curr_type, curr_subgrp)
                    # print('!!! curr_subgrp !!!', text, code)
                    # print(test)
                    # print('refsub', refsub)

                    try:
                        obj = Part.objects.filter(subgroup_id=refsub)

                        if obj.count() > 0:
                            print('exist obj > 0', curr_subgrp['name_subgroup'], curr_type['name'], obj.count())
                            clear()
                        if obj.count() == 0:
                            print('exist obj == 0', obj.count())
                            # if counter % 10 == 0:
                            #     time.sleep(random.randint(6, 9))
                            #     print('quantity requests:',  counter)

                            response = requests.get(
                                'http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test),
                                cookies=self.cookies, headers=self.headers)
                            print('запрос: ', counter, response.status_code)
                            time.sleep(random.randint(1, 2))

                            if 200 <= response.status_code < 400:
                                parts_by_type_and_subgroup = dict(response.json())
                                for key, value in parts_by_type_and_subgroup.items():

                                    try:
                                        if key == 'items' and len(value) > 0:
                                            for part in list(value):
                                                current_part = Part()

                                                current_part.part_number = part['Item']
                                                current_part.prise = part['Price']
                                                current_part.retail = part['Retail']
                                                current_part.brend = part['Бренд']
                                                current_part.name = part['Название']
                                                current_part.description = part['Описание']

                                                curr = str(part['Item']).replace('.', '')
                                                curr = curr.replace(' ', '')
                                                curr = curr.replace('-', '')
                                                curr = curr.replace('/', '')
                                                curr = curr.replace('_', '')
                                                curr = curr.replace('(', '')
                                                curr = curr.replace(')', '')

                                                current_part.referred_id = str(
                                                    curr_subgrp['referred_id']) + '-' + str(curr)
                                                current_part.subgroup_id = curr_subgrp['referred_id']

                                                current_part.save()
                                                print('save', current_part.part_number, current_part.subgroup_id)

                                                response.close()

                                    except:
                                        print('ex2', key, value)
                                        response.close()
                                        pass
                            # counter += 1
                            # print('exist obj == 0', curr_subgrp['name_subgroup'], curr_type['name'], obj.count())
                            #
                            # try:
                            #     if counter % 20 == 0:
                            #         time.sleep(random.randint(3, 8))
                            #     time.sleep(random.randint(0.6, 1))
                            #
                            #     response = requests.get(
                            #         'http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test),
                            #         cookies=self.cookies, headers=self.headers)
                            #
                            #     print('запрос: ', counter, curr_subgrp['name_subgroup'], curr_type['name'],
                            #           response.status_code)
                            #
                            #     print('http://b2b.ad.ua/api/catalog/items?{query}'.format(query=query))
                            #     if 200 <= response.status_code < 400:
                            #         parts_by_type_and_subgroup = dict(response.json())
                            #         for key, value in parts_by_type_and_subgroup.items():
                            #
                            #             try:
                            #                 if key == 'items' and len(value) > 0:
                            #                     for part in list(value):
                            #                         current_part = Part()
                            #
                            #                         current_part.part_number = part['Item']
                            #                         current_part.prise = part['Price']
                            #                         current_part.retail = part['Retail']
                            #                         current_part.brend = part['Бренд']
                            #                         current_part.name = part['Название']
                            #                         current_part.description = part['Описание']
                            #
                            #                         curr = str(part['Item']).replace('.', '')
                            #                         curr = curr.replace(' ', '')
                            #                         curr = curr.replace('-', '')
                            #                         curr = curr.replace('/', '')
                            #                         curr = curr.replace('_', '')
                            #                         curr = curr.replace('(', '')
                            #                         curr = curr.replace(')', '')
                            #
                            #                         current_part.referred_id = str(
                            #                             curr_subgrp['referred_id']) + '-' + str(curr)
                            #                         current_part.subgroup_id = curr_subgrp['referred_id']
                            #
                            #                         current_part.save()
                            #                         print('save', current_part.part_number, current_part.subgroup_id)
                            #                         response.close()
                                            # else:
                                            #     current_part = Part()
                                            #
                                            #     current_part.part_number = ''
                                            #     current_part.prise = ''
                                            #     current_part.retail = ''
                                            #     current_part.brend = ''
                                            #     current_part.name = ''
                                            #     current_part.description = ''
                                            #     current_part.referred_id = ''
                                            #     current_part.subgroup_id = curr_subgrp['referred_id']
                                            #
                                            #     current_part.save()
                                            #
                                            #     print('save with out parts', current_part.subgroup_id)
                                            #     response.close()
                                            #     time.sleep(random.randint(1, 2))
                            #             except:
                            #                 print('key == items and len(value) > 0', key, value)
                            #                 response.close()
                            #                 pass
                            #
                            #     else:
                            #         print('!!!!! Bead RESPONS !!!!!', response.status_code)
                            #         response.close()
                            #         time.sleep(random.randint(20, 20))
                            # except:
                            #     print('except 1', response.status_code)
                            #     # break

                    except:
                        print('!!!!!!!!!!ObjectDoesNotExist!!!!!!!!!!')











    def delete_duplicate_parts_and_update_db(self):
        counter = 0
        part_number_list = Part.objects.values('part_number').distinct()

        for current_number_part in part_number_list:
            counter = counter + 1
            try:
                obj = PartNumbersWithOutDuplicates.objects.get(part_number=current_number_part['part_number'])
                print(counter, current_number_part['part_number'])
            except PartNumbersWithOutDuplicates.DoesNotExist:
                print(counter, current_number_part['part_number'])
                obj = PartNumbersWithOutDuplicates(part_number=current_number_part['part_number'])
                obj.save()
        pass





    def update_price_quick(self):

        # ГОТОВЫЙ МЕТОД. Обновление ценника для запчастей из таблици PartDescription, которые есть в наличии
        total_for_parsing = list(PartDescription.objects.values_list('number', flat=True)
                                 .exclude(Q(vinnitsa__in=['0', ''])
                                          & Q(zhitomir__in=['0', ''])
                                          & Q(kiyivone__in=['0', ''])
                                          & Q(khmelnitskiy__in=['0', ''])
                                          & Q(kiyivtwo__in=['0', '']))
                                 .order_by('number'))

        sparsheno = list(PartDescription.objects.values_list('number', flat=True)
                         .exclude(Q(vinnitsa__in=['0', ''])
                                  & Q(zhitomir__in=['0', ''])
                                  & Q(kiyivone__in=['0', ''])
                                  & Q(khmelnitskiy__in=['0', ''])
                                  & Q(kiyivtwo__in=['0', '']))
                         .exclude(Q(prise__in=['']))
                         .order_by('number'))

        ostatok = list(PartDescription.objects.values_list('number', flat=True)
                       .exclude(Q(vinnitsa__in=['0', ''])
                                & Q(zhitomir__in=['0', ''])
                                & Q(kiyivone__in=['0', ''])
                                & Q(khmelnitskiy__in=['0', ''])
                                & Q(kiyivtwo__in=['0', '']))
                       .filter(Q(prise__in=['']))
                       .order_by('number'))


        print('total_for_parsing', len(total_for_parsing))
        print('sparsheno', len(sparsheno))
        print('ostatok', len(ostatok))




        parser_prise = Parser_price(self.cookies, self.headers, ostatok)
        parser_prise.search_main()
















    def get_images_and_description_part_and_save_to_db(self):
        counter = 0

        part_number_without_duplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        # снять тестовое ограничение количества
        for current_number_part in PartNumbersWithOutDuplicates.objects.values('part_number').order_by('part_number'):
            counter += 1

            try:
                obj = PartDescription.objects.filter(number=current_number_part['part_number'])

                if obj.count() > 0:
                    print('exist obj > 0', obj.count(), counter)
                if obj.count() == 0:
                    print('exist obj == 0', obj.count())

                    if counter % 10 == 0:
                        time.sleep(random.randint(3, 5))
                        print(counter, ' from ', len(part_number_without_duplicate))

                    curr = str(current_number_part['part_number']).replace('.', '')
                    curr = curr.replace(' ', '')
                    curr = curr.replace('-', '')
                    curr = curr.replace('/', '')
                    curr = curr.replace('_', '')
                    curr = curr.replace('(', '')
                    curr = curr.replace(')', '')

                    query = dict(grp='', item=curr)
                    time.sleep(.300)
                    response = requests.get('http://b2b.ad.ua/api/catalog/search?{query}'.format(query=urlencode(query)),
                                            cookies=self.cookies,
                                            headers=self.headers)
                    if 200 <= response.status_code < 400:
                        print("response.status_code", response.status_code)


                        for k, v in dict(response.json()).items():
                            # get and save images
                            if (k == 'images' and len(v) > 0):
                                for i in v:
                                    try:
                                        img = Imege.objects.get(part_number=current_number_part['part_number'],
                                                                tab_image=i['GraTab'],
                                                                name_image=i['GraGrdId'])
                                        print('ничего не делаем')

                                    except Imege.DoesNotExist:
                                        img = Imege(part_number=current_number_part['part_number'],
                                                    tab_image=i['GraTab'],
                                                    name_image=i['GraGrdId'])
                                        img.save()
                                        print('save image')

                            if (k == 'images' and len(v) == 0):
                                try:
                                    img = Imege.objects.get(part_number=current_number_part['part_number'])

                                except Imege.DoesNotExist:
                                    img = Imege(part_number=current_number_part['part_number'])
                                    img.save()
                                    print('у запчасти нет картинки')

                            # get data for part and save
                            if (k == 'items' and len(v) > 0):
                                for spare in v:
                                    try:
                                        obj = PartDescription.objects.get(number=current_number_part['part_number'])
                                        print('ничего не делаем с описанием, нашли в PartDescription')
                                    except PartDescription.DoesNotExist:
                                        obj = PartDescription()

                                        obj.number = current_number_part['part_number']
                                        obj.prise = spare['Price']
                                        obj.retail = spare['Retail']
                                        obj.brend = spare['Бренд']
                                        obj.name = spare['Название']
                                        obj.description = spare['Описание']
                                        if(str(spare['Info']) != "None"):
                                            obj.info = spare['Info']
                                        else:
                                            obj.info = ''
                                        obj.save()
                                        print('save description')

                            if (k == 'items' and len(v) == 0):
                                try:
                                    spare = PartDescription.objects.get(number=current_number_part['part_number'])
                                    print('ничего не делаем с описанием')
                                except PartDescription.DoesNotExist:
                                    spare = PartDescription(number=current_number_part['part_number'])
                                    spare.save()
                                    print('save empty')

            except Part.ObjectDoesNotExist:
                print('!!!!!!!!!!ObjectDoesNotExist!!!!!!!!!!')

    def get_cros_numbers(self):
        # ГОТОВЫЙ МЕТОД. берет из таблици PartNumbersWithOutDuplicates пробегается по ним и формирует-обновляет таблицу кросов
        self.headers['Content-Type'] = 'text/html'
        part_number_without_duplicate = PartNumbersWithOutDuplicates.objects.values('part_number').order_by('part_number').reverse()
        len_arr = len(part_number_without_duplicate)

        counter = 0
        query_counter = 0
        for current_number_part in part_number_without_duplicate:
            counter = counter + 1
            query = dict(code=current_number_part['part_number'])
            if counter % 30 == 0:
                # time.sleep(random.randint(3, 5))
                pass

            try:
                response = requests.get('http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query)),
                                        cookies=self.cookies, headers=self.headers)
                time.sleep(.3)
                if(len(response.json()['items']) > 0):

                    for kross in response.json()['items']:
                        try:
                            isExist = CrosesByString.objects.values('original_number', 'cros_number').filter(
                                original_number=current_number_part['part_number'],
                                cros_number=kross['Item'])
                            print("exist", len(isExist))
                            if(len(isExist) == 0):
                                cr = CrosesByString()
                                cr.original_number = current_number_part['part_number']
                                cr.cros_number = kross['Item']
                                cr.save()
                                print('save', counter, 'from', len_arr)
                        except:
                            print('1err')
                if (len(response.json()['items']) == 0):
                    # cr = CrosesByString()
                    # cr.original_number = current_number_part['part_number']
                    # cr.cros_number = ''
                    # cr.save()
                    print("нету кроса, записали номер", counter, 'from', len_arr)
            except:
                print("err")





    def get_quontity_part(self):
        # ГОТОВЫЙ МЕТОД. записывает наличие на складах запчастей в таблице API_partdescription (предварительно надо очистить)
        self.headers['Content-Type'] = 'text/html'
        qsParts = PartDescription.objects.values('number')
        string_parts = ""
        A = qsParts
        f = lambda A, n=10000: [A[i:i + n] for i in range(0, len(A), n)]
        splited_lists = f(A)
        for index, current_list in enumerate(splited_lists):

            counter = 0
            for part in current_list:
                counter += 1
                string_parts = string_parts + '\'\'' + part['number'] + '\'\','

                if (counter == len(current_list)):
                    string_parts = string_parts + '\'\'' + part['number'] + '\'\''

            print(index + 1, ' from ', len(splited_lists))
            response = requests.post('http://b2b.ad.ua/api/catalog/stockitems',
                                     json={'items': "{parts}".format(parts=string_parts)},
                                     cookies=self.cookies, headers=self.headers)
            print(response.status_code)
            for kross in response.json():
                # если нашли в таблице обновили колличество
                try:
                    obj = PartDescription.objects.get(number=kross['ItemNo'])
                    if kross['LocationCode'] == 'ВНЦ1':
                        obj.vinnitsa = str(kross['Qty'])
                    if kross['LocationCode'] == 'КИЕВ2':
                        obj.kiyivtwo = str(kross['Qty'])
                    if kross['LocationCode'] == 'КИЕВ1':
                        obj.kiyivone = str(kross['Qty'])
                    if kross['LocationCode'] == 'ХМЛ1':
                        obj.khmelnitskiy = str(kross['Qty'])
                    if kross['LocationCode'] == 'ЖТМ1':
                        obj.zhitomir = str(kross['Qty'])
                    # print(obj)

                    obj.save()
                    # print('save')

                except PartDescription.DoesNotExist:

                    print("is ton exist in PartDescription table")
                    # если не нашли добавили позицию с описанием и колличеством

                    pass
            string_parts = ''




    def setDataToTimeTable(self):
        # ГОТОВЫЙ МЕТОД. Заполняем данными таблицу API_timedata. В таблице находятся номера кросов с перентом для взятия описания для кроса
        counter = 0
        n = TimeData.objects.all()
        n.delete()

        qsCrosesAll = CrosesByString.objects.values('cros_number')
        print('qsCrosesAll', len(qsCrosesAll))
        qsWithOutDuplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        print('qsWithOutDuplicate', len(qsWithOutDuplicate))
        qsNewCroses = qsCrosesAll.values('cros_number').difference(qsWithOutDuplicate)
        print('qsNewCroses', len(qsNewCroses))
        distAllCroses = CrosesByString.objects.order_by('cros_number').distinct('cros_number')
        print(len(distAllCroses))
        qsDif = distAllCroses.values('original_number', 'cros_number').filter(cros_number__in=qsNewCroses)
        print(len(qsDif))


        for q in qsDif.values('original_number', 'cros_number'):
            counter = counter + 1
            print(counter, q)
            if q['cros_number'] != '':
                TimeData(n=q['original_number'], k=q['cros_number']).save()

        print(len(qsDif))




    def clearQuontityInDescriptionTable(self):
        # ГОТОВЫЙ МЕТОД. Oчищаем колличество в таблице API_partdescription.
        total_for_parsing = PartDescription.objects.values('number')\
                                    .exclude(Q(vinnitsa__in=[''])
                                          & Q(zhitomir__in=[''])
                                          & Q(kiyivone__in=[''])
                                          & Q(khmelnitskiy__in=[''])
                                          & Q(kiyivtwo__in=['']))\
        .update(vinnitsa='', zhitomir='', kiyivone='', khmelnitskiy='', kiyivtwo='')
        print('done. clear quantity')



    def clearPriseInPartDescriptionTable(self):
        # ГОТОВЫЙ МЕТОД. Oчищаем все ценники в таблице API_partdescription.
        d = PartDescription.objects.values('number', 'prise', 'retail')\
            .exclude(prise__isnull=True)\
            .exclude(prise__exact='')\
            .exclude(retail__isnull=True)\
            .exclude(retail__exact='')\
            .update(prise='', retail='')
        print('done. clear price')


    def getDescriptionParts (self):
        # ГОТОВЫЙ МЕТОД. По API_timeTable копируем описание запчастей из API_parts.
        #                Для крос номеров из API_timeTable парсим описание.

        # По табице PartNumbersWithOutDuplicates формируем записи с описанием из таблици API_Parts в API_partsdescription


        # Удаление дубликатов
        try:
            unique_fields = ['number']

            duplicates = (
                PartDescription.objects.values(*unique_fields).order_by().annotate(max_id=Max('id'), count_id=Count('id')).filter(count_id__gt=1)
            )
            for duplicate in duplicates:
                (
                    PartDescription.objects.filter(**{x: duplicate[x] for x in unique_fields}).exclude(id=duplicate['max_id']).delete()
                )
        except:
            print("не работает удаление дубликатво")


        counter = 0
        for p in PartNumbersWithOutDuplicates.objects.values('part_number'):
            counter = counter + 1
            print(counter)

            try:
                isExist = PartDescription.objects.values('number').filter(number=p['part_number'])
                print("exist", len(isExist))
                if (len(isExist) == 0):
                    d = Part.objects.values('part_number',
                                            'brend',
                                            'name',
                                            'description').filter(part_number=p['part_number']).first()

                    obj = PartDescription()
                    obj.number = d['part_number']
                    obj.brend = d['brend']
                    obj.name = d['name']
                    obj.description = d['description']
                    obj.save()
                    print('save', counter)
            except:
                print('1err')



        print('закончили')

        # Добавляем кросы из временной таблици в API_partsdescription
        counter = 0
        qsTimeData = TimeData.objects.values('n', 'k')



        print(len(qsTimeData))

        for p in qsTimeData:
            print(p['k'])
            if len(PartDescription.objects.values('number', 'brend').filter(number=p['k'])) == 0:
                d = PartDescription()
                d.number = p['k']
                d.save()
                print('добавили', p['k'])
            else:
                print("уже добавили крос номер")

        # Добавляем к крос номерам описание
        counter = 0
        for p in qsTimeData.values('n'):
            counter = counter + 1
            print(counter)
            try:
                query = dict(code=p['n'])
                time.sleep(.4)
                if counter % 30 == 0:
                    time.sleep(random.randint(3, 7))
                response = requests.get(
                    'http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query)),
                    cookies=self.cookies,
                    headers=self.headers)
                if 200 <= response.status_code < 400:
                    print('http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query)))

                    for k, v in dict(response.json()).items():
                        # get data for part and save
                        if (k == 'items' and len(v) > 0):
                            for spare in v:
                                print('spare[Item]', spare['Item'])
                                print(str(spare['Price']), str(spare['Retail']), str(spare['Бренд']),
                                      str(spare['Название']), str(spare['Описание']))
                                try:
                                    PartDescription.objects.get(Q(number__contains=spare['Item']))
                                    try:
                                        d = PartDescription.objects.get(Q(number=spare['Item']) & Q(brend=''))
                                        d.brend = str(spare['Бренд'])
                                        d.name = str(spare['Название'])
                                        d.description = str(spare['Описание'])
                                        d.save(update_fields=['brend', 'name', 'description'])
                                        print('>>>>обновили все поля')
                                    except:
                                        print('не обновили все поля')
                                except PartDescription.DoesNotExist:
                                    print('не сздан в таблице PartDescription', spare['Item'])
            except:
                print('уже')

        qsTail = PartDescription.objects.values('number', 'brend').filter(brend='')
        print(len(qsTail))

        if len(qsTail) > 0:
            for p in qsTail:
                print(p['number'])
                counter += 1
                if counter % 8 == 0:
                    time.sleep(random.randint(5, 10))
                    print(counter, ' from ', len(qsTail))
                curr = str(p['number']).replace('.', '')
                curr = curr.replace(' ', '')
                curr = curr.replace('-', '')
                curr = curr.replace('/', '')
                curr = curr.replace('_', '')
                curr = curr.replace('(', '')
                curr = curr.replace(')', '')

                query = dict(grp='', item=curr)
                response = requests.get(
                    'http://b2b.ad.ua/api/catalog/search?{query}'.format(query=urlencode(query)),
                    cookies=self.cookies,
                    headers=self.headers)

                for k, v in dict(response.json()).items():
                    # get data for part and save
                    if (k == 'items' and len(v) > 0):
                        for spare in v:
                            try:
                                if spare['Item'] == p['number']:
                                    obj = PartDescription.objects.get(number=p['number'])
                                    obj.brend = str(spare['Бренд'])
                                    obj.name = str(spare['Название'])
                                    obj.description = str(spare['Описание'])
                                    obj.save()
                                    print('save')
                            except PartDescription.DoesNotExist:
                                print('почему то не нашли, хотя должны были')

            pass

    def update_price_part(self):
        # РАБОЧИЙ МЕТОД ОБНОВЛЕНИЯ ЦЕН НА ЗАПЧАСТИ

        # qs = PartDescription.objects.values('number',
        #                                     'vinnitsa',
        #                                     'kiyivtwo',
        #                                     'kiyivone',
        #                                     'khmelnitskiy',
        #                                     'zhitomir',
        #                                     'prise').filter(
        #     Q(vinnitsa__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
        #     | Q(zhitomir__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
        #     | Q(kiyivone__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
        #     | Q(khmelnitskiy__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
        #     | Q(kiyivtwo__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
        #
        # ).order_by('number')
        #
        #
        # print('qs', len(qs))
        #
        # qsWithOutDuplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        # print('qsWithOutDuplicate', len(qsWithOutDuplicate))
        # qsNewCroses = qs.values('number').difference(qsWithOutDuplicate)
        # print(qsNewCroses)
        #
        # print('qsNewCroses', len(qsNewCroses))
        # qsByMark = qs.values('number').difference(qsNewCroses)
        # print('qsByMark', len(qsByMark))
        # print(qsByMark)
        # qsSubgrp = Part.objects.values('part_number', 'subgroup_id').filter(part_number__in=qsByMark).order_by('part_number').distinct('part_number')
        # print('qsSubgrp', len(qsSubgrp))
        # print(qsSubgrp)
        #
        # qsSubgrpId = qsSubgrp.values('subgroup_id')
        # print('qsSubgrpId', len(qsSubgrpId))
        # print(qsSubgrpId)
        #
        # qsNameCode = SubGroup.objects.values('referred_id', 'name_subgroup', 'typecar_id').filter(referred_id__in=qsSubgrpId)
        # print('qsNameCode', len(qsNameCode))
        # print(qsNameCode)
        #
        # counter = 0
        # # Обновление для номеров с помощью подгруппы и марки авто
        # for p in qsNameCode:
        #     counter = counter + 1
        #     if counter % 30 == 0:
        #         time.sleep(random.randint(3, 7))
        #     text = p['name_subgroup']
        #     code = p['typecar_id']
        #     query = dict(code=code, group=text)
        #     test = urlencode(query)
        #     response = requests.get(
        #         'http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test),
        #         cookies=self.cookies, headers=self.headers)
        #     print('запрос: ', counter, 'from', len(qsNameCode),  response.status_code)
        #
        #     if 200 <= response.status_code < 400:
        #         parts_by_type_and_subgroup = dict(response.json())
        #         for key, value in parts_by_type_and_subgroup.items():
        #
        #             try:
        #                 if key == 'items' and len(value) > 0:
        #                     for part in list(value):
        #                         try:
        #                             # qsByMark.get(Q(number__contains=part['Item']))
        #                             # print('+')
        #                             try:
        #                                 obj = PartDescription.objects.get(number=part['Item'])
        #                                 obj.prise = part['Price']
        #                                 obj.retail = part['Retail']
        #                                 obj.save()
        #                                 print('>>>save')
        #                             except:
        #                                 print('не сохранили')
        #
        #                         except:
        #                             print("не нужный номер")
        #             except:
        #                 print('exeption')
        #
        #
        # # Обновление для крос номеров

        qs = PartDescription.objects.values('number',
                                            'vinnitsa',
                                            'kiyivtwo',
                                            'kiyivone',
                                            'khmelnitskiy',
                                            'zhitomir',
                                            'prise').filter(
            Q(vinnitsa__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
            | Q(zhitomir__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
            | Q(kiyivone__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
            | Q(khmelnitskiy__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])
            | Q(kiyivtwo__in=['1', '2', '3', '4', '5', '6', '7', '8', '9', '>9'])

        ).order_by('number')

        print('qs', len(qs))

        # qsWithOutDuplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        # print('qsWithOutDuplicate', len(qsWithOutDuplicate))
        # qsNewCroses = qs.values('number').difference(qsWithOutDuplicate)
        # print('qsNewCroses', len(qsNewCroses))
        # distAllCroses = CrosesByString.objects.order_by('cros_number').distinct('cros_number')
        # print('distAllCroses', len(distAllCroses))
        # qsDif = distAllCroses.values('original_number', 'cros_number').filter(cros_number__in=qsNewCroses)
        # print('qsDif', len(qsDif))
        # print(qsDif)

        # for p in qsNewCroses:
        #     print(p['number'])
        #     if len(PartDescription.objects.values('number', 'brend').filter(number=p['number'])) == 0:
        #         d = PartDescription()
        #         d.number = p['number']
        #         d.save()
        #         print('добавили', p['k'])
        #     else:
        #         print("уже добавили крос номер")
        #
        # # Добавляем к крос номерам описание
        # counter = 0
        # for p in qsDif:
        #     counter = counter + 1
        #     print(counter)
        #     try:
        #         query = dict(code=p['original_number'])
        #         # time.sleep(.4)
        #         if counter % 30 == 0:
        #             time.sleep(random.randint(3, 7))
        #         response = requests.get(
        #             'http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query)),
        #             cookies=self.cookies,
        #             headers=self.headers)
        #         if 200 <= response.status_code < 400:
        #             print('http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query)))
        #
        #             for k, v in dict(response.json()).items():
        #                 # get data for part and save
        #                 if (k == 'items' and len(v) > 0):
        #                     for spare in v:
        #                         print('spare[Item]', spare['Item'])
        #                         print(str(spare['Price']), str(spare['Retail']), str(spare['Бренд']),
        #                               str(spare['Название']), str(spare['Описание']))
        #                         try:
        #                             # Отсекаем ненужные номера для обновления
        #                             qsDif.get(Q(cros_number__contains=spare['Item']))
        #                             print('+')
        #                             try:
        #                                 # Обновляем
        #                                 d = PartDescription.objects.get(Q(number=spare['Item']) & Q(prise=''))
        #                                 print("d", d)
        #                                 d.prise = str(spare['Price'])
        #                                 d.retail = str(spare['Retail'])
        #
        #                                 d.save()
        #                                 print('>>>>обновили ценник')
        #                             except:
        #                                 print('не обновили все поля')
        #                         except:
        #                             print('не нужный номер', spare['Item'])
        #     except:
        #         print('уже')

        # Обновление для остатка не обработанных номеров
        qsTail = qs.values('number', 'prise').filter(Q(prise=''))
        print('qsTail', len(qsTail))
        time.sleep(10)
        counter = 0
        if len(qsTail) > 0:
            for p in qsTail:
                print(p['number'])
                counter += 1
                time.sleep(random.randint(5, 10))
                print(counter, ' from ', len(qsTail))

                curr = str(p['number']).replace('.', '')
                curr = curr.replace(' ', '')
                curr = curr.replace('-', '')
                curr = curr.replace('/', '')
                curr = curr.replace('_', '')
                curr = curr.replace('(', '')
                curr = curr.replace(')', '')

                query = dict(grp='', item=curr)
                response = requests.get(
                    'http://b2b.ad.ua/api/catalog/search?{query}'.format(query=urlencode(query)),
                    cookies=self.cookies,
                    headers=self.headers)
                print(counter, 'from ', len(qsTail), 'http://b2b.ad.ua/api/catalog/search?{query}'.format(query=urlencode(query)))

                for k, v in dict(response.json()).items():
                    # get data for part and save
                    if (k == 'items' and len(v) > 0):
                        for spare in v:
                            try:
                                if spare['Item'] == p['number']:
                                    obj = PartDescription.objects.get(number=p['number'])
                                    obj.prise = str(spare['Price'])
                                    obj.retail = str(spare['Retail'])
                                    obj.save()
                                    print('save')
                            except PartDescription.DoesNotExist:
                                print('почему то не нашли, хотя должны были')
            pass

    def testQ(self):
        # ТЕСТОВАЯ ВЫБОРКА ЗАПЧАСТЕЙ ПО КОЛИЧЕСТВУ.
        print('test')




























