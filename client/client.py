import requests
import sys
import time

def safe_get(l, idx):
    try:
        return l[idx]
    except:
        return ""

if safe_get(sys.argv, 1) == "local":
    API = "http://localhost:8001"
else:
    API = "https://peaceful-coast-27289.herokuapp.com/"

CLIENT_ID = "NMAtsTzZo7Poh6OeKyDOo3Vpq70WHOnt"
SCOPE = "profile email openid"
AUDIENCE = "https://api.paczkomatron3000/"
payload = f"client_id={CLIENT_ID}&scope={SCOPE}&audience={AUDIENCE}"
headers = { 'content-type': "application/x-www-form-urlencoded" }
res = requests.post("https://zgagaczj.us.auth0.com/oauth/device/code", data=payload, headers=headers)
print(f"Kod autoryzacyjny: {res.json()['user_code']}")
print("Zweryfikuj urządzenie przechodząc pod poniższy link:")
print(res.json()["verification_uri_complete"])
interval = res.json()["interval"]
device_code = res.json()["device_code"]
headers = { 'content-type': "application/x-www-form-urlencoded" }
payload = f"grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code={device_code}&client_id={CLIENT_ID}"
res = requests.post("https://zgagaczj.us.auth0.com/oauth/token", data=payload, headers=headers)
time.sleep(interval)
while res.status_code != 200:
    error = res.json()["error"]
    print("Czekam na autoryzację...")
    if error == "expired_token" or error == "access_denied":
        print("Błąd autoryzacji, spróbuj ponownie")
        exit(1)
    res = requests.post("https://zgagaczj.us.auth0.com/oauth/token", data=payload, headers=headers)
    time.sleep(interval)
accesstoken = res.json()["access_token"]
idtoken = res.json()["id_token"]
head = {"Authorization": f"Bearer {accesstoken}", "IDToken": f"Bearer {idtoken}"}
res = requests.get(API + "/courier/jwt", headers=head)
if res.status_code != 200:
    print("Błąd podczas generacji tokenu, spróbuj ponownie później")
    exit(1)
token = res.text

#obejście logowania przez oauth0 stałym tokenem
#token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwYWN6a29tYXRyb24gYXV0aG9yaXphdGlvbiBzZXJ2ZXIiLCJzdWIiOiJjb3VyaWVyIiwidXNyIjoiamFua3VyaWVyb3d5IiwiYXVkIjoicGFjemtvbWF0cm9uIGFwaSIsImV4cCI6MTYxNTQ3MTk4Nn0.PAruRQyLXt62OBzcGbr4qwWiVGG4k_lQidGNFdhCmq8"

def showMiniHelp():
    print('Wpisz "pomoc" aby wyświetlić pomoc, "q" aby wyjść')

def printHelp():
    print("""Lista poleceń:
    pomoc - wyświetl listę komend
    q - wyjdź s programu
    lista - wyświetl listę etykiet i paczek
    paczka nowa <pid> - utwórz nową paczkę na podstawie id etykiety
    paczka status <pid> {dostarczona/odebrana} - zmień status paczki o podanym id na dostarczoną bądź odebraną""")

def printApiError():
    print("Nie można połączyć się z api, spróbuj ponownie później")

def printList():
    try:
        head = {"Authorization": f"Bearer {token}"}
        res = requests.get(API + "/labels", headers=head)
        if res.status_code == 200:
            plist = res.json()["_embedded"]["labels"]
            print("Lista etykiet:")
            for label in plist:
                print(label["pid"])
                if label.get('_links').get('package') is not None:
                    print(" nadana: tak")
                else:
                    print(" nadana: nie") 
        else:
            print("Nie można wczytać listy etykiet, spróbuj ponownie później")
        res = requests.get(API + "/packages", headers=head)
        if res.status_code == 200:
            plist = res.json()["_embedded"]["packages"]
            print("Lista paczek:")
            for label in plist:
                print(label["pid"])
                print(f"  status: {label.get('status')}")
        else:
            print("Nie można wczytać listy paczek, spróbuj ponownie później")
    except:
        printApiError()

def createPackage(pid):
    try:
        package = {
            "pid":pid
        }
        head = {"Authorization": f"Bearer {token}"}
        res = requests.post(API + "/packages", headers=head, json=package)
        if res.status_code == 200:
            print("Pomyślnie dodano paczkę")
        elif res.status_code == 400:
            print("Błąd: " + res.json().get("error"))
        else:
            print("Nie można dodać paczki, spróbuj ponownie później")
    except:
        printApiError()

def changePackageStatus(pid, status):
    try:
        package = {
            "pid":pid,
            "status":status
        }
        head = {"Authorization": f"Bearer {token}"}
        res = requests.put(API + "/packages/" + pid, headers=head, json=package)
        if res.status_code == 200:
            print("Pomyślnie zaktualizowano status paczki")
        elif res.status_code == 400:
            print("Błąd: " + res.json().get("error"))
        else:
            print("Nie można zaktualizować statusu paczki, spróbuj ponownie później")
    except:
        printApiError()

showMiniHelp()

while True:
    inp = input().split(" ")
    cmd = safe_get(inp, 0)
    if cmd == "pomoc":
        printHelp()
    elif cmd == "lista":
        printList()
    elif cmd == "q":
        exit(0)
    elif cmd == "paczka" and safe_get(inp, 1) == "nowa":
        pid = safe_get(inp, 2)
        if len(pid) == 0:
            print("nie podano id etykiety")
        else:
            createPackage(pid)
    elif cmd == "paczka" and safe_get(inp, 1) == "status":
        pid = safe_get(inp, 2)
        status = safe_get(inp, 3)
        if len(pid) == 0:
            print("nie podano id etykiety")
        if len(status) == 0:
            print("nie podano statusu")
        else:
            changePackageStatus(pid, status)
    else:
        showMiniHelp()