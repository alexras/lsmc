.PHONY: build-mac
build-mac: images
	python setup.py py2app --excludes gdbm

.PHONY: build-win
build-win: images-win
	python setup_win.py py2exe

.PHONY: images
images:
	cd images && ./make_images.sh

.PHONY: images-win
images-win:
	cd images && ./make_images_win.sh

.PHONY: debug
debug:
	./dist/main.app/Contents/MacOS/main

.PHONY: clean
clean:
	rm -rf build
	rm -rf dist

.PHONY: install-deps-mac
install-deps-mac:
	pip install --upgrade -r ../requirements.txt

.PHONY: install-deps-win
install-deps-win:
	pip install --upgrade -r ../requirements_win.txt \
		--allow-external wxPython \
		--allow-unverified wxPython \
		--allow-external ObjectListView \
		--allow-unverified ObjectListView
