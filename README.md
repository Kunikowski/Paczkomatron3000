# Paczkomatron3000

Nowoczesna aplikacja do monitorowania przesyłek wysyłanych do paczkomatów.

Wdrożona na Heroku: https://fathomless-beyond-00111.herokuapp.com/

Drugi kamień milowy: https://damp-castle-13996.herokuapp.com/

Trzeci kamień milowy:</br>
aplikacja dla nadawcy - https://pacific-taiga-40295.herokuapp.com/ </br>
api - https://hidden-depths-96421.herokuapp.com/

Do uruchomienia drugiego kamienia milowego lokalnie potrzebne są pliki:
- .env zawierający zmienne REDIS_HOST=redis, REDIS_PORT=6379,REDIS_DB=0, SECRET_KEY oraz SESSION_COOKIE_SECURE=True
- web/cert.pem oraz web/key.pem będące wynikiem wygenerowania certyfikatu SSL (potrzebne do uruchomienia pod https aby ciasteczko miało flagę Secure), można uruchomić bez nich pod http, trzeba wtedy usunąć je jako argumenty w Dockerfile i zmienić zmienną SESSION_COOKIE_SECURE=False

Do uruchomienia trzeciego kamienia milowego lokalnie potrzebne są pliki:
- .env zawierający zmienne REDIS_HOST=redis, REDIS_PORT=6379,REDIS_DB=0, SECRET_KEY oraz SESSION_COOKIE_SECURE=True, API_HOST = http://api:8001, JWT_SECRET
- web/cert.pem oraz web/key.pem będące wynikiem wygenerowania certyfikatu SSL (potrzebne do uruchomienia pod https aby ciasteczko miało flagę Secure), można uruchomić bez nich pod http, trzeba wtedy usunąć je jako argumenty w Dockerfile i zmienić zmienną SESSION_COOKIE_SECURE=False
- aby aplikacja client połączyła się z lokalnym api zamiast z tym na heroku, należy uruchomić ją z argumentem "local", czyli "python client.py local"

Aplikacja client zawiera listę dostępnych komend po wpisaniu polecenia "pomoc".
