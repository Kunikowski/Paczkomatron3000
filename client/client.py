import requests
import sys


token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwYWN6a29tYXRyb24gYXV0aG9yaXphdGlvbiBzZXJ2ZXIiLCJzdWIiOiJjb3VyaWVyIiwidXNyIjoiamFua3VyaWVyb3d5IiwiYXVkIjoicGFjemtvbWF0cm9uIGFwaSIsImV4cCI6MTYxNTQ3MTk4Nn0.PAruRQyLXt62OBzcGbr4qwWiVGG4k_lQidGNFdhCmq8"

def safe_get(l, idx):
    try:
        return l[idx]
    except:
        return ""

if safe_get(sys.argv, 1) == "local":
    API = "http://localhost:8001"
else:
    API = "https://hidden-depths-96421.herokuapp.com"

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
                print(f"  status:{label.get('status')}")
        else:
            print("Nie można wczytać listy etykiet, spróbuj ponownie później")
        res = requests.get(API + "/packages", headers=head)
        if res.status_code == 200:
            plist = res.json()["_embedded"]["packages"]
            print("Lista paczek:")
            for label in plist:
                print(label["pid"])
                print(f"  status:{label.get('status')}")
        else:
            print("Nie można wczytać listy etykiet, spróbuj ponownie później")
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
        res = requests.post(API + "/packages/" + pid, headers=head, json=package)
        if res.status_code == 200:
            print("Pomyślnie zaktualizowano status paczki")
        elif res.status_code == 400:
            print("Błąd: " + res.json().get("error"))
        else:
            print("Nie można zaktualizować statusu paczki, spróbuj ponownie później")
    except:
        printApiError()

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