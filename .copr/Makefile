# .copr/Makefile — COPR make srpm compatible (cleaned version)

TAR_NAME := FreeCAD-main
TARBALL := main.tar.gz

# Expect 'outdir' and 'spec' to be passed in via CLI
outdir ?= $(CURDIR)
spec ?=

#prev_commits = $(shell curl -s 'https://api.github.com/repos/FreeCAD/FreeCAD/compare/120ca87015...main' | grep "\"ahead_by\":" | sed -s 's/ //g' | sed -s 's/"ahead_by"://' | sed -s 's/,//')
#git_commit_no =  $(shell echo $$(($(prev_commits) + 1)))

.PHONY: srpm archive update-submodules clean

srpm: archive update-spec
	rpmbuild -bs \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(outdir)" \
		freecad.spec
	@echo "✓ SRPM generated at $(outdir)"

install-tools:
	@missing=""; \
	for cmd in git curl; do \
		if ! command -v $$cmd &>/dev/null; then \
			missing="$$missing $$cmd"; \
		fi; \
	done; \
	if [ -n "$$missing" ]; then \
		dnf install -y $$missing; \
	fi
	@echo "✓ All dependencies are installed";


update-spec: install-tools
	$(eval prev_commits := $(shell curl -s 'https://api.github.com/repos/FreeCAD/FreeCAD/compare/120ca87015...main' | grep "\"ahead_by\":" | sed -s 's/ //g' | sed -s 's/"ahead_by"://' | sed -s 's/,//'))
	$(eval git_commit_no :=  $(shell echo $$(($(prev_commits) + 1))))
	sed -e 's/{{{git_commit_no}}}/$(git_commit_no)/g' $(spec) > freecad.spec
	@echo "✓  Spec updated with git_commit_no = $(git_commit_no)"

update-submodules: install-tools
	git submodule update --init --recursive
	@echo "✓ Submodules updated"

archive: update-submodules install-tools
	git ls-files --recurse-submodules | tar caf $(TARBALL) --xform s:^:$(TAR_NAME)/: --verbatim-files-from -T-
	@echo "✓ Tarball created: $(TARBALL)"

clean:
	rm -f *.tar.gz *.src.rpm
	@echo "✓ Cleaned"
