redeploy: clean build deploy

clean:
	/bin/rm -rf dist build

build:
	python3 setup.py bdist_wheel

deploy:
	pip3 install dist/*.whl --upgrade --user

uninstall:
	sudo pip uninstall pyarchappl

test:
	cd main/tests; python3 -m "pytest"
