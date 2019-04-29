#include <cstdlib>
#include <iostream>
#include <chrono>
#include <string>
#include <functional>

#include <tango.h>

const char* getOption(const char* name)
{
    const auto envName = std::string("_TANGO_BENCHMARK_") + name;
    return std::getenv(envName.c_str());
}

template <typename Time>
double timeDelta(const Time& t1, const Time& t2)
{
    std::chrono::duration<double> d = t2 - t1;
    return d.count();
}

using BlobWriter = std::function<void(int, Tango::DevicePipe&)>;

template <typename T>
BlobWriter makeBlobWriter(const T& data)
{
    return [=](int prefix, auto& pipe)
    {
        auto tmpData = data;
        tmpData.name = std::to_string(prefix) + data.name;
        pipe << tmpData;
    };
}

auto makeBlobWriters()
{
    vector<unsigned short> shortArray{0, 1, 2, 3, 4};
    vector<double> doubleArray{1.11, 2.22};

    return std::vector<BlobWriter>{
        makeBlobWriter(Tango::DataElement<long int>("DevLong64", 123)),
        makeBlobWriter(Tango::DataElement<unsigned long>("DevULong", 123)),
        makeBlobWriter(Tango::DataElement<vector<unsigned short>>("DevVarUShortArray", shortArray)),
        makeBlobWriter(Tango::DataElement<vector<double>>("DevVarDoubleArray", doubleArray)),
        makeBlobWriter(Tango::DataElement<bool>("DevBoolean", true)) };
}

auto makePipeBlob(const char* name, int size)
{
    Tango::DevicePipe pipe(name);
    pipe.set_root_blob_name("PipeBlob");

    const auto blobWriters = makeBlobWriters();

    for (int i = 0; i < size; ++i)
    {
        blobWriters[i % blobWriters.size()](i, pipe);
    }

    return pipe;
}

int main(int, char**)
{
    const char* deviceName = getOption("device");
    const char* pipeName = getOption("pipe");
    const char* periodStr = getOption("period");
    const char* sizeStr = getOption("size");

    if (not (deviceName and pipeName and periodStr and sizeStr))
    {
        return 1;
    }

    const double period = std::atof(periodStr);

    const int size = std::atoi(sizeStr);

    auto pipeBlob = makePipeBlob(pipeName, size);

    auto proxy = Tango::DeviceProxy(deviceName);

    long counter = 0;
    long errors = 0;

    const auto startTime = std::chrono::system_clock::now();
    auto endTime = startTime;

    while (timeDelta(startTime, endTime) < period)
    {
        try
        {
            auto tmpBlob = pipeBlob; // copy needed, call resets the pipe
            proxy.write_pipe(tmpBlob);
            counter++;
        }
        catch (...)
        {
            errors++;
        }
        endTime = std::chrono::system_clock::now();
    }

    std::cout
        << counter << " "
        << timeDelta(startTime, endTime) << " "
        << errors << "\n";

    return 0;
}
