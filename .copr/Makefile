# .copr/Makefile — COPR make srpm compatible (cleaned version)

VERSION := $(shell git describe --tags --always | sed 's/^v//; s/-/./g')
TAR_NAME := FreeCAD-main
TARBALL := main.tar.gz

# Expect 'outdir' and 'spec' to be passed in via CLI
outdir ?= $(CURDIR)
spec ?=

.PHONY: srpm archive update-submodules clean

srpm: archive
	rpmbuild -bs \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(outdir)" \
		--load="rpkg.macros" \
		$(spec)
	@echo "✓ SRPM generated at $(outdir)"
install-tools:
	dnf -y install git

update-submodules: install-tools
	git submodule update --init --recursive
	@echo "✓ Submodules updated"

archive: update-submodules
	git ls-files --recurse-submodules | tar caf $(TARBALL) --xform s:^:$(TAR_NAME)/: --verbatim-files-from -T-
	@echo "✓ Tarball created: $(TARBALL)"

clean:
	rm -f *.tar.gz *.src.rpm
	@echo "✓ Cleaned"
