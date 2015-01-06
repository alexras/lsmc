all: images
	python setup.py py2app

.PHONY: images
images:
	cd images && ./make_images.sh

debug:
	./dist/main.app/Contents/MacOS/main

clean:
	rm -rf build
	rm -rf dist
