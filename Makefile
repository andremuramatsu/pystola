PROJECT=pystola
VERSION=1.0.0
REVISION=1
BUILDDIR=$(CURDIR)/deb_dist
DESTDIR=$(BUILDDIR)/opt/$(PROJECT)
CONTROL=$(BUILDDIR)/DEBIAN/control
ARCHITECTURE=$(shell dpkg --print-architecture)

all:
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Clean build artifacts"

clean:
	rm -Rf $(DESTDIR)
	rm -Rf build/
	rm -Rf dist/
	rm $(PROJECT).spec

builddeb:
	@mkdir -p $(BUILDDIR)
	@mkdir -p $(DESTDIR)
	pyinstaller -D -s -y --clean ./src/$(PROJECT).py
	cp ./dist/$(PROJECT)/* $(DESTDIR)/ -Rv
	cp ./lib/vnu $(DESTDIR)/ -Rv
	fakeroot dpkg-deb -b $(BUILDDIR) $(PROJECT)_$(VERSION)-$(REVISION)_$(ARCHITECTURE).deb
