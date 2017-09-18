clean:
	/bin/rm -rf dist build

build:
	python setup.py bdist_wheel

deploy:
	sudo pip install dist/pyarchappl-0.0.1-py2-none-any.whl --upgrade

uninstall:
	sudo pip uninstall pyarchappl
	
test:
	nosetests