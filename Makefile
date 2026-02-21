PYTHON := .venv/bin/python
MPREMOTE := mpremote
DEVICE := auto
SRC_DIR := src
BOARD_PATH := :

PY_FILES := $(shell find $(SRC_DIR) -type f -name "*.py")
HTML_FILES := $(shell find $(SRC_DIR) -type f -name "*.html")
NETWORKS_FILE := networks.json
ASSET_FILES := $(shell find $(SRC_DIR)/static -type f -not -name "*.py" -not -name "*.html")
FILES := $(PY_FILES) $(HTML_FILES) $(ASSET_FILES)

.PHONY: all sync lint format typecheck test flash clean

all: lint format typecheck test

sync:
	uv sync

# Install the typing stubs
stubs:
	uv pip install -r pyproject.toml --extra stubs --target typings

lint:
	.venv/bin/ruff check $(SRC_DIR) tests

format:
	.venv/bin/black $(SRC_DIR) tests

typecheck:
	.venv/bin/pyright $(SRC_DIR)

test:
	.venv/bin/pytest

flash: $(FILES)
	$(MPREMOTE) mip install github:josverl/micropython-stubs/mip/typing_extensions.mpy || true
	$(MPREMOTE) mip install github:josverl/micropython-stubs/mip/typing.mpy || true
	$(MPREMOTE) connect $(DEVICE) fs mkdir $(BOARD_PATH) || true
	$(MPREMOTE) connect $(DEVICE) fs mkdir $(BOARD_PATH)/lib || true
	$(MPREMOTE) connect $(DEVICE) fs mkdir $(BOARD_PATH)/vendor || true
	$(MPREMOTE) connect $(DEVICE) fs mkdir $(BOARD_PATH)/static || true
	$(MPREMOTE) connect $(DEVICE) fs mkdir $(BOARD_PATH)/tasks || true

	@for file in $(FILES); do \
		echo "Uploading $$file..."; \
		$(MPREMOTE) connect $(DEVICE) fs cp $$file $(BOARD_PATH)/$${file#$(SRC_DIR)/}; \
	done

	$(MPREMOTE) connect $(DEVICE) fs cp $(SRC_DIR)/$(NETWORKS_FILE) $(BOARD_PATH)/$(NETWORKS_FILE)

flash-clean:
	echo "import os" > .wipe.py
	echo "def wipe(path=''):" >> .wipe.py
	echo "    for f in os.listdir(path or '.'): " >> .wipe.py
	echo "        p = path + '/' + f if path else f" >> .wipe.py
	echo "        if os.stat(p)[0] & 0x4000:" >> .wipe.py
	echo "            wipe(p)" >> .wipe.py
	echo "            os.rmdir(p)" >> .wipe.py
	echo "        else:" >> .wipe.py
	echo "            os.remove(p)" >> .wipe.py
	echo "wipe()" >> .wipe.py
	$(MPREMOTE) connect $(DEVICE) run .wipe.py
	rm .wipe.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
