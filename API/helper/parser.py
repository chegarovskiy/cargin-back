import re
import time
from django.db.models import QuerySet
from django.db.models import Manager
from ..models import Mark, Model, TypeCar, SubGroup, Part
import random
import json
from collections import namedtuple
import pypyodbc
import requests
import requests.cookies
from http.cookies import SimpleCookie
from urllib.parse import urlencode
import urllib

#response = requests.post('http://b2b.ad.ua/Account/Login?ReturnUrl=%2F', data={'ComId': '15', 'UserName': '10115', 'Password': 'e89f1a11', 'RememberMe': False, '__RequestVerificationToken': '<TOKEN>'})

class Loginization:
    def __init__(self):
        self.cookies = requests.cookies.RequestsCookieJar()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        }
        self.token = None
        response = requests.get('http://b2b.ad.ua/', headers=self.headers)

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

            for current_mark in all_marks_list:
                # верменный ограничитель на колличество спаршенных марок
                if current_mark['Name'] == 'LEXUS' or current_mark['Name'] == 'ZAZ' or current_mark['Name'] == 'BMW':
                    self.mark_dict[current_mark['MARK_ID']] = current_mark['Name']
                else:
                    continue
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
        print("models_quontity", models_quontity)
        counter = 0
        # difference = list(set(),)
        # print("difference", difference)
        for mod in Model.objects.all():
            print("mod", mod)
            query = dict(code=mod.referred_id)
            counter += 1
            if counter % 10 == 0:
                time.sleep(random.randint(8, 13))
            # if counter == 5:
            #     break

            print('code=mod.referred_id', mod.referred_id)
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

    def get_subgroups_from_site(self):
        counter = 0
        for current_type in TypeCar.objects.all():
            counter += 1
            if counter % 10 == 0:
                time.sleep(random.randint(8, 13))
            # if counter == 1000:
            #     break
            print(counter)
            query = dict(code=current_type.referred_id)
            response = requests.get('http://b2b.ad.ua/api/catalog/groups?{query}'.format(query=urlencode(query)), cookies=self.cookies, headers=self.headers)

            if 200 <= response.status_code < 400:
                all_grups = dict(response.json())
                for key, value in all_grups.items():
                    if (key == 'groups'):
                        for cur_grpup in list(value):
                            for curr_subgrup in list(cur_grpup['subgrp']):

                                    curr_subgoup = SubGroup()
                                    curr_subgoup.code_group = cur_grpup['code']
                                    curr_subgoup.name_group = cur_grpup['name']

                                    curr_subgoup.code_subgroup = curr_subgrup['code']
                                    curr_subgoup.name_subgroup = curr_subgrup['name']
                                    curr_subgoup.typecar = current_type

                                    curr_subgoup.referred_id = str(curr_subgrup['code']) +'-'+ str(current_type.referred_id)

                                    curr_subgoup, created = SubGroup.objects.update_or_create(
                                        referred_id=curr_subgoup.referred_id,
                                                    defaults={'code_group': curr_subgoup.code_group,
                                                              'name_group': curr_subgoup.name_group,
                                                              'code_subgroup': curr_subgoup.code_subgroup,
                                                              'name_subgroup': curr_subgoup.name_subgroup,
                                                              'referred_id': curr_subgoup.referred_id,
                                                              'typecar': curr_subgoup.typecar
                                                              }
                                    )




class ParserListPartsBySubgroup(Loginization):
    def __init__(self):
        super(ParserListPartsBySubgroup, self).__init__()

    def get_list_parts_by_subgroup_from_site(self):
        counter = 0
        for current_subgroup in SubGroup.objects.all():
            print(current_subgroup.typecar_id)
            print(current_subgroup.name_subgroup)
            # print(current_subgroup.code_subgroup)
            # print(current_subgroup.name_group)
            # print(current_subgroup.code_group)
            counter += 1
            if counter % 10 == 0:
                time.sleep(random.randint(5, 10))

            text = current_subgroup.name_subgroup
            code = current_subgroup.typecar_id
            # text_quote = urllib.parse.quote_plus(text)
            # print('text_quote', text_quote)
            # print('code', code)
            query = dict(code=code, group=text)
            test = urlencode(query)
            # print('test', test)

            response = requests.get('http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test), cookies=self.cookies, headers=self.headers)
            print(counter)
            # print(response.status_code)
            if 200 <= response.status_code < 400:
                print(response.json())
                parts_by_type_and_subgroup = dict(response.json())
                for key, value in parts_by_type_and_subgroup.items():
                    if key == 'items':
                        for part in list(value):

                            current_part = Part()

                            current_part.part_number = part['Item']
                            current_part.prise = part['Price']
                            current_part.retail = part['Retail']
                            current_part.brend = part['Бренд']
                            current_part.name = part['Название']
                            current_part.description = part['Описание']
                            current_part.type_id = current_subgroup.typecar
                            current_part.referred_id = str(current_subgroup.referred_id) + '&' + str(current_part.part_number)
                            current_part.subgroup = current_subgroup

                            current_part.save()














"""
query = dict(code=1139)
response = requests.get('http://b2b.ad.ua/api/catalog/models?{query}'.format(query=urlencode(query)), cookies=cookies, headers=headers)
if 200 <= response.status_code < 400:
    all_models_list = list(response.json())
    for current_mod in all_models_list:
        mod_dict[current_mod['MOD_ID']] = current_mod['MARK_ID']
        print(current_mod['MARK_ID'], current_mod['MOD_ID'])
        print(mod_dict.__len__())
#парсим все типы
for model_id in mod_dict.keys():
    query = dict(code=model_id)
    response = requests.get('http://b2b.ad.ua/api/catalog/types?{query}'.format(query=urlencode(query)),
                            cookies=cookies, headers=headers)
    if 200 <= response.status_code < 400:
        all_types_list = list(response.json())
        for current_type in all_types_list:
            type_dict[current_type['typ_id']] = current_type['MOD_ID']
            type_name_dict[current_type['typ_id']] = current_type['name_full']
            print('typ_id = ',current_type['typ_id'], 'name_full = ', current_type['name_full'])










# парсим групы

all_type_list_grp_subgrp = list() #[[ type_id, подгрупа, група], ...]

for type_id in type_dict.keys():
    query = dict(code=type_id)
    response = requests.get('http://b2b.ad.ua/api/catalog/groups?{query}'.format(query=urlencode(query)),
                            cookies=cookies, headers=headers)
    if 200 <= response.status_code < 400:
        type_list_grp_subgrp = list()
        all_grups = dict(response.json())
        for key, value in all_grups.items():
            grp_dict = dict()
            if (key == 'subgrp'):
                for cur_subgrp in list(value):
                    curType_subgrps_list = list()  # {name_group, name_sub_group}                  
                    curType_subgrps_list.append(type_id)
                    curType_subgrps_list.append(cur_subgrp['grp'])
                    curType_subgrps_list.append(cur_subgrp['code'])
                    all_type_list_grp_subgrp.append(curType_subgrps_list)
                    # print('id_type: ', type_id,  'подгрупа: ', cur_subgrp['code'], 'група: ', cur_subgrp['grp'])

for k in all_type_list_grp_subgrp:
    print(k[0], k[1], k[2])



# список запчастей (код, цена, ...)
curr_lisl_item_for_subgrup = list()
#all_cars_items__list = list()
#f = open('parts.txt', 'w')
for k in all_type_list_grp_subgrp:
    query = dict(code=k[0], group=k[2])
    response = requests.get('http://b2b.ad.ua/api/catalog/items?{query}'.format(query=urlencode(query)), cookies=cookies, headers=headers)
    if 200 <= response.status_code < 400:
        items_parts_dict = dict(response.json())
        for key, val in items_parts_dict.items():
            if(key == 'items'):
                for item in list(val):
                    curr_lisl_item_for_subgrup.append(k[0])
                    curr_lisl_item_for_subgrup.append(k[1])
                    curr_lisl_item_for_subgrup.append(k[2])
                    curr_lisl_item_for_subgrup.append(item['Item'])
                    #f.write(str(item['Item'])')
                    curr_lisl_item_for_subgrup.append(item['Price'])
                    curr_lisl_item_for_subgrup.append(item['Retail'])
                    print(k[0], k[1], k[2], item['Item'], item['Price'], item['Retail'])

"""
"""
list_items = list()
list_items_without_duplicate = list()
f = open('parts.txt', 'r')
f1 = open('list_items_without_duplicate.txt', 'w')
for line in f:
    list_items.append(line)

list_items_without_duplicate = list(set(list_items))
f.close()
print(list_items.__len__())
print(list_items_without_duplicate.__len__())
for i in list_items_without_duplicate:
    f1.write(str(i))
f1.close()
"""

# запчасти с привязанными аналогами
# list_spare_parts = list()
# f = open('list_items_without_duplicate.txt', 'r')
# f1 = open('test.txt', 'w')
# L = [item.replace('\n', '') for item in f]
# for item in L:
#     # print(item)
#     query = dict(code=item)
#     response = requests.get('http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query)), cookies=cookies, headers=headers)
#     print('    ', response.status_code, response.json())
#     curr_spares = dict()
#     curr_spares[item] = response.text
#     list_spare_parts.append(curr_spares)
#     # проверка на новые номера из аналогов
#     for k, v in dict(response.json()).items():
#         if (k == 'items'):
#             for numb_spare in v:
#                 print(numb_spare['Item'])
#                 f1.write(str(numb_spare['Item']))
#
# test_spare_count = list()
# for line in f1:
#     test_spare_count.append(line)
# print(test_spare_count.__len__())
#
#
# f.close()
# f1.close()





# запись в файл наличия на складах

# f = open('list_items_without_duplicate.txt', 'r')
# headers['Content-Type'] = 'text/html'
# response = requests.post('http://b2b.ad.ua/api/catalog/stockitems', json={'items' : "''MH OC90OF ''"}, cookies=cookies, headers=headers)
# print(response.status_code, response.reason, repr(response.text))


# for item in f:
#     enc_item = '\'\'' + item.strip() + '\'\''
#     response = requests.post('http://b2b.ad.ua/api/catalog/stockitems', json=dict(items=enc_item), cookies=cookies, headers=headers)
#     print(response.status_code, response.reason, repr(response.text))
#
# f_stocks = open('quontity_parts_in_stocks.txt', 'w')
# for quontity_item in response.json():
#     print(quontity_item['ItemNo'], quontity_item['LocationCode'], quontity_item['Qty'])
#     f_stocks.write(str(quontity_item))
#
#


























