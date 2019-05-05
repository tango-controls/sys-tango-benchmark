#include <cstdlib>
#include <iostream>
#include <chrono>
#include <string>

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

int main(int, char**)
{
    const char* deviceName = getOption("device");
    const char* attributeName = getOption("attribute");
    const char* periodStr = getOption("period");

    if (not (deviceName and attributeName and periodStr))
    {
        return 1;
    }

    const double period = std::atof(periodStr);

    std::string _attributeName = attributeName;

    auto proxy = Tango::DeviceProxy(deviceName);

    long counter = 0;
    long errors = 0;

    const auto startTime = std::chrono::system_clock::now();
    auto endTime = startTime;

    while (timeDelta(startTime, endTime) < period)
    {
        try
        {
            proxy.read_attribute(_attributeName);
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
