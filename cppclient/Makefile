OUTDIR=bin

SOURCES=$(wildcard *.cpp)
CLIENTS=$(patsubst %.cpp, $(OUTDIR)/%, $(SOURCES))

all: $(CLIENTS)

clean:
	rm -rf $(OUTDIR)/*

$(OUTDIR):
	mkdir $@

$(CLIENTS): $(OUTDIR)/%: %.cpp | $(OUTDIR)
	g++ \
		-I/usr/include/tango \
		-I/usr/local/include/tango \
		-L/usr/lib \
		-L/usr/local/lib \
		-o $@ \
		$< \
		-ltango \
		-lomniORB4 \
		-lomnithread

.PHONY: all clean
