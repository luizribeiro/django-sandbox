# django-sandbox

[![Build Status](https://travis-ci.org/luizribeiro/django-sandbox.svg?branch=master)](https://travis-ci.org/luizribeiro/django-sandbox) [![Coverage Status](https://coveralls.io/repos/github/luizribeiro/django-sandbox/badge.svg)](https://coveralls.io/github/luizribeiro/django-sandbox) [![Requirements Status](https://requires.io/github/luizribeiro/django-sandbox/requirements.svg?branch=master)](https://requires.io/github/luizribeiro/django-sandbox/requirements/?branch=master)

To do local development:

```
% yarn
% virtualenv -p python3.5 venv
% source venv/bin/activate
(venv) % pip install -r dev-requirements.txt
(venv) % pyre start
(venv) % ./manage.py collectstatic
(venv) % env $(cat .env | xargs) ./manage.py runserver
```
