import re
import time
from django.db.models import QuerySet
from django.db.models import Manager
from ..models import Mark, Model, TypeCar, SubGroup, Part, PartNumbersWithOutDuplicates, PartDescription, Imege, CrosesByString
import random
import json
from collections import namedtuple
import pypyodbc
import requests
import requests.cookies
from http.cookies import SimpleCookie
from urllib.parse import urlencode
import urllib
import certifi

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

            for current_mark in all_marks_list:
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

    def get_subgroups_from_site(self):

        counter = 0
        all_types = TypeCar.objects.all()
        for current_type in all_types:
            counter += 1
            print('current_type', current_type.referred_id)
            try:
                # если нашли в таблице подгруп по типу ищем или все подгрупы и групы спаршены
                objects = SubGroup.objects.filter(typecar_id=current_type.referred_id)
                print(counter, ' from ', len(all_types))
                if(len(objects) == 0):
                    if counter % 10 == 0:
                        print(current_type.referred_id)
                        time.sleep(random.randint(8, 13))
                    # print(counter, ' from ', len(all_types))

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

            except:
                print('exept')
                pass


class ParserListPartsBySubgroup(Loginization):
    def __init__(self):
        super(ParserListPartsBySubgroup, self).__init__()

    def get_list_parts_by_subgroup_from_site(self):
        pass
        # counter = 0
        # subgrups_all = SubGroup.objects.all()
        # for current_subgroup in subgrups_all:
        #
        #     counter += 1
        #     if counter % 10 == 0:
        #         time.sleep(random.randint(5, 10))
        #         print(counter,  )
        #
        #     text = current_subgroup.name_subgroup
        #     code = current_subgroup.typecar_id
        #
        #     query = dict(code=code, group=text)
        #     test = urlencode(query)
        #     try:
        #         obj = Part.objects.get(subgroup_id= )

            # except Part.DoesNotExist:
            #     response = requests.get('http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test),
            #                             cookies=self.cookies, headers=self.headers)
            #     # print(counter)
            #     # print(response.status_code)
            #     if 200 <= response.status_code < 400:
            #         # print(response.json())
            #         parts_by_type_and_subgroup = dict(response.json())
            #         for key, value in parts_by_type_and_subgroup.items():
            #             if key == 'items':
            #                 for part in list(value):
            #
            #                     current_part = Part()
            #
            #                     current_part.part_number = part['Item']
            #                     current_part.prise = part['Price']
            #                     current_part.retail = part['Retail']
            #                     current_part.brend = part['Бренд']
            #                     current_part.name = part['Название']
            #                     current_part.description = part['Описание']
            #                     current_part.type_id = current_subgroup.typecar
            #                     current_part.referred_id = str(current_subgroup.referred_id) + '&' + str(current_part.part_number)
            #                     current_part.subgroup = current_subgroup.referred_id
            #
            #                     current_part.save()

    def get_list_parts_by_mark(self, mark):

        counter = 0
        curr_mark = Mark.objects.get(name=mark)
        print(curr_mark.referred_id)
        curr_models = Model.objects.values('referred_id', 'name', 'mark_id').filter(mark_id=curr_mark)
        print(curr_models)

        for curr_model in curr_models:
            curr_types = TypeCar.objects.values('name', 'model_id', 'referred_id').filter(model_id=curr_model['referred_id'])

            for curr_type in curr_types:
                curr_subgrps = SubGroup.objects.values('typecar_id', 'name_subgroup', 'referred_id').filter(typecar_id=curr_type['referred_id'])

                for curr_subgrp in curr_subgrps:
                    counter += 1

                    text = curr_subgrp['name_subgroup']
                    code = curr_subgrp['typecar_id']
                    refsub = curr_subgrp['referred_id']
                    query = dict(code=code, group=text)
                    test = urlencode(query)


                    try:
                        obj = Part.objects.filter(subgroup_id=refsub).count()

                        if obj > 0:
                            print(counter, 'exist ', curr_subgrp['name_subgroup'], curr_type['name'])
                        if obj == 0:


                            with requests.get(
                                    'http://b2b.ad.ua/api/catalog/items?{query}'.format(query=test),
                                    cookies=self.cookies, headers=self.headers) as response:

                                print(counter, 'parts is not exist ', curr_subgrp['name_subgroup'], curr_type['name'])
                                time.sleep(random.randint(1, 2))

                                if 200 <= response.status_code < 400:
                                    parts_by_type_and_subgroup = dict(response.json())
                                    for key, value in parts_by_type_and_subgroup.items():
                                        if key == 'items' and len(value) > 0:
                                            for part in list(value):
                                                current_part = Part()

                                                current_part.part_number = part['Item']
                                                current_part.prise = part['Price']
                                                current_part.retail = part['Retail']
                                                current_part.brend = part['Бренд']
                                                current_part.name = part['Название']
                                                current_part.description = part['Описание']
                                                current_part.referred_id = str(
                                                    curr_subgrp['referred_id']) + '&' + str(
                                                    part['Item'])
                                                current_part.subgroup_id = curr_subgrp['referred_id']

                                                current_part.save()
                                                response.close()
                                                print('save', current_part.part_number)
                                        else:
                                            current_part = Part()

                                            current_part.part_number = ''
                                            current_part.prise = ''
                                            current_part.retail = ''
                                            current_part.brend = ''
                                            current_part.name = ''
                                            current_part.description = ''
                                            current_part.referred_id = ''
                                            current_part.subgroup_id = curr_subgrp['referred_id']

                                            current_part.save()
                                            response.close()

                                            print('save with out parts', current_part.part_number)
                                            time.sleep(random.randint(1, 2))
                                else:
                                    print('!!!!! Bead RESPONS !!!!!', response.status_code)
                                    time.sleep(random.randint(20, 20))

                        else:
                            print(counter, obj)
                            pass
                    except :
                        print('!!!!!!!!!!Part.DoesNotExist!!!!!!!!!!')
                        pass











    def delete_duplicate_parts_and_update_db(self):
        part_number_list = Part.objects.values('part_number').distinct()

        for current_number_part in part_number_list:
            try:
                obj = PartNumbersWithOutDuplicates.objects.get(part_number=current_number_part['part_number'])
            except PartNumbersWithOutDuplicates.DoesNotExist:
                obj = PartNumbersWithOutDuplicates(part_number=current_number_part['part_number'])
                obj.save()
        pass



    def get_images_and_description_part_and_save_to_db(self):
        counter = 0

        part_number_without_duplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        # снять тестовое ограничение количества
        for current_number_part in part_number_without_duplicate:
            counter += 1

            if counter % 8 == 0:
                time.sleep(random.randint(5, 10))
                print(counter, ' from ', len(part_number_without_duplicate))

            curr = str(current_number_part['part_number']).replace('.', '')
            curr = curr.replace(' ', '')
            curr = curr.replace('-', '')
            curr = curr.replace('/', '')
            curr = curr.replace('_', '')
            curr = curr.replace('(', '')
            curr = curr.replace(')', '')

            query = dict(grp='', item=curr)

            response = requests.get('http://b2b.ad.ua/api/catalog/search?{query}'.format(query=urlencode(query)),
                                    cookies=self.cookies,
                                    headers=self.headers)


            # print(response.json())


            for k, v in dict(response.json()).items():
                # get and save images
                if (k == 'images' and len(v) > 0):
                    for i in v:
                        try:
                            img = Imege.objects.get(part_number=current_number_part['part_number'],
                                                    tab_image=i['GraTab'],
                                                    name_image=i['GraGrdId'])

                        except Imege.DoesNotExist:
                            img = Imege(part_number=current_number_part['part_number'],
                                        tab_image=i['GraTab'],
                                        name_image=i['GraGrdId'])
                            img.save()

                if (k == 'images' and len(v) == 0):
                    try:
                        img = Imege.objects.get(part_number=current_number_part['part_number'])

                    except Imege.DoesNotExist:
                        img = Imege(part_number=current_number_part['part_number'])
                        img.save()

                # get data for part and save
                if (k == 'items' and len(v) > 0):
                    for spare in v:
                        try:
                            obj = PartDescription.objects.get(number=current_number_part['part_number'])

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

                if (k == 'items' and len(v) == 0):
                    try:
                        spare = PartDescription.objects.get(number=current_number_part['part_number'])

                    except PartDescription.DoesNotExist:
                        spare = PartDescription(number=current_number_part['part_number'])
                        spare.save()
        pass

    def get_cros_numbers(self):
        # ar1 = list()
        # original_number = CrosesByString.objects.values('original_number')
        # # for i in original_number:
        # #     ar1.append(i)
        # print('original_number all length = ' + str(len(original_number)))
        #
        # ar2 = list()
        # original_number = CrosesByString.objects.values('original_number').distinct()
        # # for i in original_number:
        # #     ar2.append(i)
        # print('original_number distinct = ' + str(len(original_number)))
        #
        # ar3 = list()
        # original_number = CrosesByString.objects.values('cros_number').distinct()
        # # for i in original_number:
        # #     ar3.append(i)
        # print('cros_number distinct = ' + str(len(original_number)))

        # arr1 = list()
        # for i in original_number:
        #     arr1.append(i['original_number'])
        #
        # # print(original_number)
        #
        # # part = Part.objects.values('part_number').distinct()
        # # print(len(part))
        # # # print(part)
        #
        # part_number_without_duplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        # print(len(part_number_without_duplicate))
        # arr2 = list()
        # for i in part_number_without_duplicate:
        #     arr2.append(i['part_number'])
        #
        # # print(arr)
        #
        # diff = list(set(arr2) - set(arr1))
        # print(len(diff))
        #
        # for i in diff:
        #     url = dict(code=i)
        #     url = urlencode(url)
        #     print(url + ' --- ' + i)





        #---------------------------------------------------------------------------------


        part_number_without_duplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        counter = 0
        for current_number_part in part_number_without_duplicate:

            counter += 1

            if counter % 10 == 0:
                time.sleep(random.randint(5, 10))
                print(counter, ' from ', len(part_number_without_duplicate))

            query = dict(code=current_number_part['part_number'])

            response = requests.get('http://b2b.ad.ua/api/catalog/replace?{query}'.format(query=urlencode(query)),
                                    cookies=self.cookies,
                                    headers=self.headers)

            # print(response.json())
            for k, v in dict(response.json()).items():
                if (k == 'items' and len(v) > 0):
                    for cros in v:
                        try:
                            obj = CrosesByString.objects.get(original_number=current_number_part['part_number'],
                                                             cros_number=cros['Item'])

                        except CrosesByString.DoesNotExist:
                            spare = CrosesByString(original_number=current_number_part['part_number'],
                                                   cros_number=cros['Item'])
                            spare.save()
                if (len(v) == 0):
                    # print(current_number_part['part_number'])
                    pass


        pass


    def get_quontity_part(self):

        self.headers['Content-Type'] = 'text/html'
        part_number_without_duplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        string_parts = ""

        A = part_number_without_duplicate
        f = lambda A, n=10: [A[i:i + n] for i in range(0, len(A), n)]
        splited_lists = f(A)
        for index, current_list in enumerate(splited_lists):

            counter = 0
            for part in current_list:
                counter += 1
                string_parts = string_parts + '\'\'' + part['part_number'] + '\'\','

                if (counter == len(current_list)):
                    string_parts = string_parts + '\'\'' + part['part_number'] + '\'\''

            print(index + 1, ' from ', len(splited_lists))
            response = requests.post('http://b2b.ad.ua/api/catalog/stockitems',
                                     json={'items': "{parts}".format(parts=string_parts)},
                                     cookies=self.cookies, headers=self.headers)

            for k in response.json():
                # print(k['LocationCode'] + k['ItemNo'] + k['Qty'])
                try:
                    obj = PartDescription.objects.get(number=k['ItemNo'])
                    if ('ЖТМ1' == k['LocationCode']):
                        obj.zhitomir = k['Qty']
                    if ('ВНЦ1' == k['LocationCode']):
                        obj.vinnitsa = k['Qty']
                    if ('КИЕВ1' == k['LocationCode']):
                        obj.kiyivone = k['Qty']
                    if ('ХМЛ1' == k['LocationCode']):
                        obj.khmelnitskiy = k['Qty']
                    if ('КИЕВ2' == k['LocationCode']):
                        obj.kiyivtwo = k['Qty']
                    obj.save()

                except PartDescription.DoesNotExist:
                    # print(k['ItemNo'] + "is ton exist in PartDescription table")
                    pass
            string_parts = ''
            time.sleep(random.randint(5, 10))

    def update_price_part(self):
        counter = 0
        part_number_without_duplicate = PartNumbersWithOutDuplicates.objects.values('part_number')
        # снять тестовое ограничение количества
        for current_number_part in part_number_without_duplicate:
            counter += 1
            if counter % 8 == 0:
                time.sleep(random.randint(5, 10))
                print(counter, ' from ', len(part_number_without_duplicate))
            curr = str(current_number_part['part_number']).replace('.', '')
            curr = curr.replace(' ', '')
            curr = curr.replace('-', '')
            curr = curr.replace('/', '')
            curr = curr.replace('_', '')
            curr = curr.replace('(', '')
            curr = curr.replace(')', '')

            query = dict(grp='', item=curr)
            response = requests.get('http://b2b.ad.ua/api/catalog/search?{query}'.format(query=urlencode(query)),
                                    cookies=self.cookies,
                                    headers=self.headers)

            for k, v in dict(response.json()).items():
                # get data for part and save
                if (k == 'items' and len(v) > 0):
                    for spare in v:
                        try:
                            obj = PartDescription.objects.get(number=current_number_part['part_number'])
                        except PartDescription.DoesNotExist:
                            obj = PartDescription()
                            obj.prise = spare['Price']
                            obj.retail = spare['Retail']
                            obj.save()
        pass

class MyInject():
    def __init__(self):
        super(MyInject, self).__init__()

    def injecttion(self):
        try:
            self.cookies = requests.cookies.RequestsCookieJar()
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            }

            response = requests.get('http://b2b.ad.ua/', headers=self.headers, verify=False)

            if response.status_code == 200:
                for history_response in response.history:
                    self.cookies.update(history_response.cookies)
                self.cookies.update(response.cookies)
                content = response.text
                # print(response.text)


            response = requests.get('http://dozor.kharkov.ua/news/', cookies=self.cookies, headers=self.headers)
            print(response.status_code)
            if 200 <= response.status_code < 400:
                print(response.json())

            pass
        except:
            print('eceptipn')
            pass










































