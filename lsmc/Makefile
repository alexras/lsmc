.PHONY: build-mac
build-mac:
	python setup.py py2app

.PHONY: build-win
build-win: images
	python setup_win.py py2exe

.PHONY: images
images:
	cd images && ./make_images.sh

.PHONY: debug
debug:
	./dist/main.app/Contents/MacOS/main

.PHONY: clean
clean:
	rm -rf build
	rm -rf dist
