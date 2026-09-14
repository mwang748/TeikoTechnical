ifeq ($(OS),Windows_NT)
PYTHON ?= "$(USERPROFILE)/anaconda3/python.exe"
VENV_PYTHON = .venv/Scripts/python.exe
else
PYTHON ?= python3
VENV_PYTHON = .venv/bin/python
endif

.PHONY: setup pipeline dashboard

setup: .venv/pyvenv.cfg
	$(VENV_PYTHON) -m pip install -r requirements.txt

.venv/pyvenv.cfg:
	$(PYTHON) -m venv .venv

pipeline:
	$(VENV_PYTHON) load_data.py
	$(VENV_PYTHON) run_pipeline.py

dashboard:
	$(VENV_PYTHON) -m streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501 --server.headless true
