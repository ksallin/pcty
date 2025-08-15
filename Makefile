.PHONY: help lint env evn-init build release-patch release-minor release-major test test-coverage deploy

help:
	@echo "lint            - lints the *.py files within the package via black lintr"
	@echo "env             - created the pcty_crab conda environment for 3.10 python version."
	@echo "env-init        - installs all the dependency packages. Please ensure to activate the env prior to executing the command."
	@echo "env-init-testing - Not needed after you've created your project, you can delete this command"
	@echo "build           - builds the package wheel file"
	@echo "release-patch   - Increments the Package patch version by 1, creates the CHANGELOG.md and pushes all changes to the working branch"
	@echo "release-minor   - Increments the Package minor version by 1, creates the CHANGELOG.md and pushes all changes to the working branch"
	@echo "release-major   - Increments the Package major version by 1, creates the CHANGELOG.md and pushes all changes to the working branch"
	@echo "test            - Run all unit tests within the package test folder"
	
	@echo "virtualenv      - create the pcty_crab virtual environment for 3.10 python version."
	@echo "test-coverage   - Summarizes test code coverage in the package, and generates html docs to review"
	
	
	

.git:
	git init
	git add .

.set-git-config:
	git config --global --add safe.directory "$(CURDIR)"
	$(call TOUCH,$@)


lint-code: .git .set-git-config
	python -m pre_commit run --all-files

lint: lint-code

env-init:
	python -m pip install --editable .[all]
	$(call TOUCH,$@)

# pip does not have a no-self option like pdm
# we don't want the package installed on the docker image directly
# instead we can make env-init because it runs its own shell
install-deps:
	python -m pip install .[all]
	pip uninstall pcty_crab -y
	$(call TOUCH,$@)

build:
	python -m build --wheel -n -o .\dist
	$(call RM,build)
	$(call RM,pcty_crab.egg-info)


publish: package_name = 'pcty_crab'
publish: current_version = $(shell sed -n '1p' $(package_name)/VERSION)
publish: available_versions = $(shell pip index versions --pre --extra-index-url $(JFROG_PIP_INDEX_URL) $(package_name) | sed -nr 's/Available versions: (.+)/\1/p')
publish: build
publish:
	@printf "[distutils]\nindex-servers = local\n[local]\nrepository: $(JFROG_PYPI_SERVER)\nusername: $(JFROG_USERNAME)\npassword:$(JFROG_PASSWORD)" >> $(HOME)/.pypirc
	@python -c 'import webbrowser; webbrowser.open("http://i305.photobucket.com/albums/nn217/struck13_2008/joker.gif", new=0, autoraise=True)' || true
	@echo 'WARNING!!! Publishing from the local environment is strictly prohibited, due to the vulnerability issue as well as the risc to break upstream projects'
	@echo $(available_versions) | grep -qwF $(current_version) && \
     echo "$(current_version) was already published. Doing nothing" || \
	{ \
		echo "$(current_version) not found in the artifactory. \
		Publishing $(package_name)==$(current_version)..." ;\
		twine upload --repository local .dist/* ;\
	}

publish-alpha: package_name = 'pcty_crab'
publish-alpha: current_version = $(shell sed -n '1p' $(package_name)/VERSION)
publish-alpha:
	echo $(current_version) | grep -q 'a' && make publish && \
	echo "Published alpha version $(current_version) to artifactory." || \
	echo "No alpha version found, not publishing to artifactory."

clean:
	$(call RM,coverage_html)
	$(call RM,.coverage)
	$(call RM,.pytest_cache)
	$(call RM,.ruff_cache)
	$(call RM,.mypy_cache)
	$(call RM,build)
	$(call RM,dist)

# reset the env-init and install-deps so they might be executed again
env-reset:
	$(call RM,env-init)
	$(call RM,install-deps)
	$(call RM,.install-pre-commit-hooks)

test: env-init
	python -m pytest -s --cov-config=.coveragerc --cov=pcty_crab tests/

test-coverage: test
	rmdir /Q /S coverage_html
	coverage html -d coverage_html

gh-release:
	@curl -L \
	-X POST \
	-H "Accept: application/vnd.github+json" \
	-H "Authorization: Bearer $(GH_TOKEN)" \
	-H "X-GitHub-Api-Version: 2022-11-28" \
	https://api.github.com/repos/Paylocity/dst-pcty_crab/releases \
	-d '{"tag_name":"$(shell  sed -n '1p' pcty_crab/VERSION)","generate_release_notes":true}'


env:
	conda remove --name pcty_crab --all -y
	conda clean --all -y
	conda create --name pcty_crab python=3.10 -y

bump-alpha:
	git fetch --all --tags
	bumpversion alpha
	git push --tags

bump-patch:
	git fetch --all --tags
	bumpversion patch
	git push --tags

bump-minor:
	git fetch --all --tags
	bumpversion minor
	git push --tags

bump-major:
	git fetch --all --tags
	bumpversion major
	git push --tags

changelog: .set-gitchangelogcfg-path
	git fetch --all --tags
	break>CHANGELOG.md
	pdm run gitchangelog
	pdm run pre-commit run --all-files end-of-file-fixer || true

add-changelog:
	git add CHANGELOG.md
	git commit -m "chore: Updating CHANGELOG.md"

release-alpha: bump-alpha changelog add-changelog
	git push

release-patch: bump-patch changelog add-changelog
	git push

release-minor: bump-minor changelog add-changelog
	git push

release-major: bump-major changelog add-changelog
	git push



