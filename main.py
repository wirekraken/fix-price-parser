import requests
from bs4 import BeautifulSoup

session = requests.Session()

def auth(login, password):
	# url = "https://fix-price.ru/personal/?login=yes"
	url = "https://fix-price.ru/ajax/auth_user.php"
	params = {
		'AUTH_FORM':'Y',
		'TYPE':'AUTH',
		'backurl':'/personal/',
		'login': login,
		'password': password
	}
	session.post(url, data=params)
	
	return True

login = str(input('Input your login : '))
password = str(input('Input your password : '))

if not login == '' and not password == '':
	auth(login, password)
	print('Wait...')

def user_data():

	url = 'https://fix-price.ru/personal/#profile'
	response = session.get(url)
	page = BeautifulSoup(response.content, 'lxml')

	personal_data = page.find_all('div', class_='personal-data__item')[0].find_all('input', class_='form-control')

	for item in personal_data:

		if item.has_attr('name'):
			if item['name'] == 'NAME':
				dict_user_data['personal data']['Name'] = item['value']
			if item['name'] == 'LAST_NAME':
				dict_user_data['personal data']['Last name'] = item['value']
			if item['name'] == 'SECOND_NAME':
				dict_user_data['personal data']['Second name'] = item['value']

		if item.has_attr('placeholder'):
			if item['placeholder'] == '*EMAIL':
				dict_user_data['personal data']['Email'] = item['value']

		if item.has_attr('checked'):
			dict_user_data['personal data']['Gender'] = item['value']


	address = page.find_all('div', class_='personal-data__item')[1].find('div', id='region_selector')
	region = address.find_all('div', class_='location-select-wrap')[0].find_all('option')

	for item in region:
		if item.has_attr('selected'):
			dict_user_data['address']['Region'] = item['value']

	city = address.find_all('div', class_='location-select-wrap')[1].find_all('option')

	for item in city:
		if item.has_attr('selected'):
			dict_user_data['address']['City'] = item['value']

	subscribe = page.find_all('div', class_='personal-data__item')[1].find_all('div', class_='form-group')

	for item in subscribe:
		for k in item.find_all('input'):
			if k.has_attr('checked'):
				dict_user_data['Subscribe'] = k['name']

def favorites():

	base_url = "https://fix-price.ru/personal/"
	page_part = "?PAGEN_2="
	response = session.get(base_url+'#favorites')
	page = BeautifulSoup(response.content, 'lxml')

	pages = page.find('ul', class_='paging__list').find_all('li', class_='paging__item')[-1].text

	k = 1
	for i in range(1, int(pages) + 1):

		response = session.get(base_url + page_part + str(i) + '#favorites')
		page = BeautifulSoup(response.content, 'lxml')
		container = page.find('div', id='catalog_sect_cont').find_all('div', class_='main-list__card-item')

		for item in container:

			title = item.find('a', class_='product-card__title').text.strip()
			price = item.find('span', class_='badge-price-value')
			dict_favorites['product_'+str(k)] = { 'title' : title, 'price': price['data-price'] }

			k += 1

def actions():
	
	base_url = 'https://fix-price.ru/actions/'
	page_part = '?PAGEN_2='

	response = session.get(base_url)
	page = BeautifulSoup(response.content, 'lxml')

	pages = page.find('div','paging-wrap').find_all('li','paging__item')[-1].text

	for i in range(1, int(pages) + 1):

		response = session.get(base_url + page_part + str(i))
		page = BeautifulSoup(response.content, 'lxml')

		actions = page.find_all('div', class_='action-block')[0].find_all('div', class_='action-card')

		i = 1
		for item in actions:
			# выбираем только действующие акции
			if item.find('span', class_='action-card__footer-date'):

				title = item.find('div','action-card__desc-title').text.strip()
				info = item.find('h4','action-card__info').text.strip()
				dict_actions['action_'+str(i)] = {'title' : title, 'info': info }
			else:
				return True # если действующие акции закончились: заканчиваем переход по страницам
			i += 1

dict_user_data = {
	'personal data': {},
	'address': {},
	'Subscribe': None
}
dict_actions = {}
dict_favorites = {}

user_data()
favorites()
actions()

text_user_data = ''
for k, v in dict_user_data.items():
	if isinstance(v, dict):
		text_user_data += f'{k} :\n'
		for k, v in v.items():
			text_user_data += f'\t{k} : {v}\n'
		text_user_data += '\n'
	else:
		text_user_data += f'{k} : {v}\n'

text_fovorites_data = ''
for k, v in dict_favorites.items():
	if isinstance(v, dict):
		text_fovorites_data += f'{k} : \n'
		for k, v in v.items():
			text_fovorites_data += f'\t{k} : {v}\n'
		text_fovorites_data += '\n'

text_actions = ''
for k, v in dict_actions.items():
	if isinstance(v, dict):
		text_actions += f'{k} : \n'
		for k, v in v.items():
			text_actions += f'\t{k} : {v}\n'
		text_actions += '\n'

data = f'''
-------------------------User data-------------------------
{text_user_data}
---------------------Favorite protucts---------------------
{text_fovorites_data}
--------------------------Actions--------------------------
{text_actions}
'''

with open(f'{login}.txt', 'w') as write_file:
    write_file.write(data)
    print('Your data in the file', login+'.txt')
