PROJECT_NAME=st-experiment-template
MODULE_NAME=st_experiment_template
REPORT_DIR=run/report
REPORT_PORT=8765
REPORT_PID := .report_server.pid
TEX_REPORT_DIR=docs/report
TEX_REPORT=RPT-00XXX-Report.tex
TEX_REPORT_BUILD_DIR=build

# build image locally for testing
# USAGE: make docker.build.local
docker.build.local:
	@docker build --tag ${PROJECT_NAME} --build-arg GITHUB_TOKEN=${GITHUB_TOKEN} .

# run a set of build tests from within the container
# NOTE: requires docker.build called prior to build the image
# USAGE: make docker.test.build
docker.test.build:
	@docker run \
		-e AWS_PROFILE="dev" \
		-v ${HOME}/.aws:/root/.aws:ro \
		--entrypoint python3 ${PROJECT_NAME} ./tests/build/test_container_build.py

# run an interactive shell inside the local container image
# NOTE: requires docker.build called prior to build the image
# NOTE: -e flag below just an example of howw to pass globals
# USAGE: make docker.shell
docker.shell:
	@docker run -it \
		-e EXAMPLE_GLOBAL="dummy" \
		-v ${HOME}/.aws:/root/.aws:ro \
		--entrypoint /bin/bash ${PROJECT_NAME}

# run the local image on specified input file.
# NOTE: --add-host flag here allows connecting to local DB
docker.run.local:
	@docker run \
		--add-host=dbhost:$$(ipconfig getifaddr en6) \
		-v ${HOME}/.aws:/root/.aws:ro \
		${PROJECT_NAME} ${MODULE_NAME}/main.py

# install the jupyter kernel if needed for reporting
# EXAMPLE USAGE: bootstrap.jupyter
bootstrap.jupyter:
	@python tools/bootstrap_jupyter.py

# initialize optional TeX report scaffold under docs/report
# EXAMPLE USAGE: make init.tex.report
init.tex.report:
	@python tools/init_tex_report.py

# compile formal TeX report
# EXAMPLE USAGE: make compile.tex.report
compile.tex.report:
	@mkdir -p $(TEX_REPORT_DIR)/$(TEX_REPORT_BUILD_DIR)
	@cd $(TEX_REPORT_DIR) && pdflatex -interaction=nonstopmode \
		-halt-on-error -output-directory $(TEX_REPORT_BUILD_DIR) $(TEX_REPORT)
	@cd $(TEX_REPORT_DIR) && pdflatex -interaction=nonstopmode \
		-halt-on-error -output-directory $(TEX_REPORT_BUILD_DIR) $(TEX_REPORT)

# locally run the primary entry point for testing outside of the container
# EXAMPLE USAGE: make run.local
run.local:
	@python ${MODULE_NAME}/main.py

# locally run the demo experiment
# EXAMPLE USAGE: make run.demo
demo_cfg=${MODULE_NAME}/experiment/demo/demo.yaml
run.demo:
	@python ${MODULE_NAME}/main.py -cfg $(demo_cfg)

# locally run unit tests
# USAGE: make unit.test
unit.test:
	@pytest --cov=${MODULE_NAME} --cov-report html:tests/reports/coverage \
		--cov-report term tests/unit -W ignore::DeprecationWarning
	mv tests/reports/coverage/index.html tests/reports/coverage/COVERAGE.html

# locally run linting tests
# USAGE: make lint
lint.test:
	flake8 ${MODULE_NAME}
	flake8 tests

# setup remote port forwarding for viewing reports on local machine
# EXAMPLE USAGE: make serve.reports
serve.reports:
	@if [ -f $(REPORT_PID) ] && kill -0 $$(cat $(REPORT_PID)) 2>/dev/null; then \
		echo "Server already running (PID $$(cat $(REPORT_PID)))"; \
	else \
		echo "Starting server on port $(REPORT_PORT)..."; \
		python3 -m http.server $(REPORT_PORT) --bind 127.0.0.1 --directory $(REPORT_DIR) > /dev/null 2>&1 & \
		echo $$! > $(REPORT_PID); \
		echo "PID $$(cat $(REPORT_PID))"; \
	fi

# kill report seeerver when done
# EXAMPLE USAGE: make stop.reports.server
stop.reports.server:
	@if [ -f $(REPORT_PID) ]; then \
		echo "Stopping server (PID $$(cat $(REPORT_PID)))"; \
		kill $$(cat $(REPORT_PID)) && rm $(REPORT_PID); \
	else \
		echo "No server running"; \
	fi

snapshot.artifacts:
	python tools/push_artifact.py