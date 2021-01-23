# Paczkomatron3000

Nowoczesna aplikacja do monitorowania przesyłek wysyłanych do paczkomatów.


Drugi kamień milowy: https://damp-castle-13996.herokuapp.com/

Trzeci kamień milowy:</br>
aplikacja dla nadawcy - https://pacific-taiga-40295.herokuapp.com/ </br>
api - https://hidden-depths-96421.herokuapp.com/

Piąty kamień milowy:</br>
aplikacja dla nadawcy - https://floating-eyrie-35684.herokuapp.com/ </br>
api - https://peaceful-coast-27289.herokuapp.com/

Do uruchomienia drugiego kamienia milowego lokalnie potrzebne są pliki:
- .env zawierający zmienne REDIS_HOST=redis, REDIS_PORT=6379,REDIS_DB=0, SECRET_KEY oraz SESSION_COOKIE_SECURE=True
- web/cert.pem oraz web/key.pem będące wynikiem wygenerowania certyfikatu SSL (potrzebne do uruchomienia pod https aby ciasteczko miało flagę Secure), można uruchomić bez nich pod http, trzeba wtedy usunąć je jako argumenty w Dockerfile i zmienić zmienną SESSION_COOKIE_SECURE=False

Do uruchomienia trzeciego kamienia milowego lokalnie potrzebne są pliki:
- .env zawierający zmienne REDIS_HOST=redis, REDIS_PORT=6379,REDIS_DB=0, SECRET_KEY oraz SESSION_COOKIE_SECURE=True, API_HOST = http://api:8001, JWT_SECRET
- web/cert.pem oraz web/key.pem będące wynikiem wygenerowania certyfikatu SSL (potrzebne do uruchomienia pod https aby ciasteczko miało flagę Secure), można uruchomić bez nich pod http, trzeba wtedy usunąć je jako argumenty w Dockerfile i zmienić zmienną SESSION_COOKIE_SECURE=False
- aby aplikacja client połączyła się z lokalnym api zamiast z tym na heroku, należy uruchomić ją z argumentem "local", czyli "python client.py local"

Do uruchomienia piątego kamienia milowego lokalnie potrzebne są pliki:
- .env zawierający zmienne REDIS_HOST=redis, REDIS_PORT=6379,REDIS_DB=0, SECRET_KEY oraz SESSION_COOKIE_SECURE=True, API_HOST = http://api:8001, JWT_SECRET, AUTH0_DOMAIN, AUTH0_CLIENT_SECRET, AUTH0_CALLBACK_URL, AUTH0_AUDIENCE, COUR_CLIENT_ID, COUR_PUBLIC_KEY, MQ_HOST, MQ_VH, MQ_LOGIN, MQ_PASS
- web/cert.pem oraz web/key.pem będące wynikiem wygenerowania certyfikatu SSL (potrzebne do uruchomienia pod https aby ciasteczko miało flagę Secure), można uruchomić bez nich pod http, trzeba wtedy usunąć je jako argumenty w Dockerfile i zmienić zmienną SESSION_COOKIE_SECURE=False
- aby aplikacja client połączyła się z lokalnym api zamiast z tym na heroku, należy uruchomić ją z argumentem "local", czyli "python client.py local"

Aplikacja client zawiera listę dostępnych komend po wpisaniu polecenia "pomoc".

W aplikacji client można obejść logowanie przez oauth zakomentowując logikę (linijki 16-45) i odkomentowując wpisany na sztywno token (linijka 48)

Do logowania przez oauth utworzone jest konto testuser@mail.to z hasłem Password123

Aplikacje invoicer.py oraz monitor.py można uruchomić podobnie jak aplikację client.py można uruchomić z linii poleceń np. "python invoicer.py"
