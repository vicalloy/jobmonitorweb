.PHONY: docs
init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock

ci:
	pipenv run py.test --junitxml=report.xml

isort:
	isort --recursive jobmonitorweb

flake8:
	pipenv run flake8 jobmonitorweb

coverage:
	pipenv run py.test --cov-config .coveragerc --verbose --cov-report term --cov-report html --cov=jobmonitorweb

celery-w:
	celery worker -A jobmonitorweb -l info

celery-beat:
	celery -A jobmonitorweb beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

flower:
	celery flower -A jobmonitorweb --address=127.0.0.1 --port=5555

run:
	python manage.py runserver

publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
