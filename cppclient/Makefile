ifdef TANGO_ROOT
	MAKE_ENV=$(TANGO_ROOT)/share/pogo/preferences
else
	MAKE_ENV=/usr/share/pogo/preferences
endif

RELEASE_TYPE=RELEASE

TANGO_REQUIRED=TRUE

include $(MAKE_ENV)/tango.opt

INSTALL_DIR=$(TANGO_HOME)/bin

CXXFLAGS += -std=c++14 -Wall -Wpedantic -Werror -Wno-error=deprecated

SOURCES=$(wildcard *.cpp)
CLIENTS=$(patsubst %.cpp, %, $(SOURCES))
TARGETS=$(patsubst %.cpp, $(OUTPUT_DIR)/%, $(SOURCES))

all: $(TARGETS)

clean:
	rm -rf $(OUTPUT_DIR)/*

install:
	install -C $(OUTPUT_DIR)/* $(INSTALL_DIR)

uninstall:
	rm -f $(patsubst %, $(INSTALL_DIR)/%, $(CLIENTS))


$(OUTPUT_DIR):
	mkdir $@

$(TARGETS): $(OUTPUT_DIR)/%: %.cpp | $(OUTPUT_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

.PHONY: all clean install
