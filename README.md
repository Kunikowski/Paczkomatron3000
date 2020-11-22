# Paczkomatron3000

Nowoczesna aplikacja do monitorowania przesyłek wysyłanych do paczkomatów.

Wdrożona na Heroku: https://fathomless-beyond-00111.herokuapp.com/

Drugi kamień milowy: https://damp-castle-13996.herokuapp.com/

Do uruchomienia drugiego kamienia milowego lokalnie potrzebne są pliki:
- .env zawierający zmienne REDIS_HOST=redis, REDIS_PORT=6379, SECRET_KEY oraz SESSION_COOKIE_SECURE=True
- web/cert.pem oraz web/key.pem będące wynikiem wygenerowania certyfikatu SSL (potrzebne do uruchomienia pod https aby ciasteczko miało flagę Secure), można uruchomić bez nich pod http, trzeba wtedy usunąć je jako argumenty w Dockerfile i zmienić zmienną SESSION_COOKIE_SECURE=False
