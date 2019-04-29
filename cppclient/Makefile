ifdef TANGO_ROOT
	MAKE_ENV=$(TANGO_ROOT)/share/pogo/preferences
else
	MAKE_ENV=/usr/share/pogo/preferences
endif

RELEASE_TYPE=RELEASE

TANGO_REQUIRED=TRUE

include $(MAKE_ENV)/tango.opt

CXXFLAGS += -std=c++14 -Wall -Wpedantic -Werror -Wno-error=deprecated

SOURCES=$(wildcard *.cpp)
CLIENTS=$(patsubst %.cpp, $(OUTPUT_DIR)/%, $(SOURCES))

all: $(CLIENTS)

clean:
	rm -rf $(OUTPUT_DIR)/*

$(OUTPUT_DIR):
	mkdir $@

$(CLIENTS): $(OUTPUT_DIR)/%: %.cpp | $(OUTPUT_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

.PHONY: all clean
