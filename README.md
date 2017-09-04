# django-sandbox

[![Build Status](https://travis-ci.org/luizribeiro/django-sandbox.svg?branch=master)](https://travis-ci.org/luizribeiro/django-sandbox) [![Coverage Status](https://coveralls.io/repos/github/luizribeiro/django-sandbox/badge.svg)](https://coveralls.io/github/luizribeiro/django-sandbox)

If using Heroku, do this first:

```
% heroku create
```

Then set everything up:

```
% yarn
% virtualenv venv
% source venv/bin/activate
(venv) % pip install -r requirements.txt
(venv) % python manage.py collectstatic
```

To run locally with Heroku:

```
% heroku local web
```

Or simply:

```
(venv) % env $(cat .env | xargs) gunicorn sandbox.wsgi --log-file -
```
