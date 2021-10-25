import discord
import json
import requests
import asyncio
from bs4 import BeautifulSoup

client = discord.Client()

token = ""
channelID = 0
loginYPAREO = ''
passwordYPAREO = ''
with open("config.json") as file:
    data = json.load(file)
    token = data["token"]
    channelID = data["channelID"]
    loginYPAREO = data['Identifiant_YPAREO']
    passwordYPAREO = data['Password_YPAREO']

@client.event
async def on_ready():
    print("I'm ready ! What can I do to help you ?")

URL = "https://ypareo.purple-campus.com/purple/index.php"
LOGIN_ROUTE = "/authentication"
BULLETIN_ROUTE = "/apprenant/bulletin/2839683/3187048/"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36', 
           'origin': URL, 
           'referer': URL + LOGIN_ROUTE}

s = requests.session()

login_page = BeautifulSoup(s.get(URL + '/login/').text, 'html.parser')
token_csrf = login_page.find('input', {'id': 'token-csrf'}).get('value')

login_payload = {
        'login': loginYPAREO,
        'password': passwordYPAREO, 
        'token_csrf': token_csrf}

login_req = s.post(URL + LOGIN_ROUTE, headers=HEADERS, data=login_payload)

bulletin_page = BeautifulSoup(s.get(URL + BULLETIN_ROUTE).text, 'html.parser')

moyenne = bulletin_page.find('tfoot', {'class': 'table-foot'}).find('td', {'class': 'moyenneApp'}).text.replace(' ', '')
moyenne = moyenne.replace('\r\n', '')
moyenne = moyenne.replace(',', '.')

data = {'note': float(moyenne)}

with open('data.json', 'w') as file:
    json.dump(data, file)


async def search_moyenne():
    while True:
        moyenneOlder = 0.0

        with open('data.json', 'r') as file:
            data = json.load(file)
            moyenneOlder = data['note']

        response = requests.get("http://localhost/Projet-Web/view/indexView.php")
        soup = BeautifulSoup(s.get(URL + BULLETIN_ROUTE).text, 'html.parser')
        
        moyenneNow = soup.find('tfoot', {'class': 'table-foot'}).find('td', {'class': 'moyenneApp'}).text.replace(' ', '')
        moyenneNow = moyenne.replace('\r\n', '')
        moyenneNow = moyenneNow.replace(',', '.')

        if (float(moyenneNow) != moyenneOlder):
            print("Nouvelle note ! La moyenne a changé")

            channel = client.get_channel(channelID)

            embed = discord.Embed(title=":bell: Nouvelle note disponible !", url="https://ypareo.purple-campus.com/purple/", description="Nouvelle note disponible ! Vous pouvez aller la consulter sur le site YPAREO en cliquant sur le titre du message :smile:", color=discord.Color.blue())
            embed.set_thumbnail(url="https://talentsdunumerique.com/sites/default/files/public/logo-3il-2018.jpg")
            await channel.send(embed=embed)

            data = {'note': float(moyenneNow)}

            with open('data.json', 'w') as file:
                json.dump(data, file)

        print("MoyenneNow = " + str(moyenneNow) + " ; MoyenneOlder = " + str(moyenneOlder))
        await asyncio.sleep(120)


client.loop.create_task(search_moyenne())

client.run(token)

    
