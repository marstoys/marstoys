import json



def read_products():
    with open('db/storage.json', 'r') as f:
        try:
            data: dict[str, dict] = json.load(f)
            return data
        except json.decoder.JSONDecodeError:
            return {}
        
def read_users():
    with open('db/users.json', 'r') as f:
        try:
            data: dict[str, dict] = json.load(f)
            return data
        except json.decoder.JSONDecodeError:
            return {}
def login()->str:
    users:dict[str,dict[str,str|int]]=read_users()
    username=input('Enter you username: ')
    password=input('Enter your password')
    for key, value in users.items():
        if username==value['username'] and password==value['password']:
            return value
    return'Couldn\'t find this user'
                
            
                

def buy_products():
    products=read_products()
    for index,title in enumerate(products.values()):
        print(f'{index+1} => {title['title']}')
    while True:
        buying_product=input('Enter which products you want to buy (write numbers): ')
        count=int(input(f'Write how much from every of them: '))

buy_products()