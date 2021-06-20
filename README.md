
# backend for the typometrics api

django rest framework

## make it run in dev

```bash 
git clone https://github.com/typometrics/djangotypometrics.git
cd into the folder
virtualenv typometricsenv
source typometricsenv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install django djangorestframework django-cors-headers tqdm bs4 dominate pandas

python3 manage.py runserver 7000
```

## installation on the server
try:

- check out first whether it's dameonized in typometricsdjango.ini - try first without it!
- easier to kill: uwsgi --ini typometricsdjango.ini --pidfile /home/typometrics/djangotypometrics/uwsgi_serv.pid
-	uwsgi --ini typometricsdjango.ini	

then:
-	check frontend (after having compiled the front end `quasar build` on the server: https://typometrics.elizia.net/
-	check the backend https://typometrics.elizia.net:7000/algodraftapp/draft/


```bash 
service uwsgi restart
systemctl restart nginx
```

