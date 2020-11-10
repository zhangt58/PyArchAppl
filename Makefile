redeploy: clean build deploy

clean:
	/bin/rm -rf dist build

build:
	python3 setup.py bdist_wheel

deploy:
	pip3 install dist/pyarchappl-0.3.0-py2.py3-none-any.whl --upgrade --user

uninstall:
	sudo pip uninstall pyarchappl
	
test:
	nosetests
