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

    auto proxy = Tango::DeviceProxy(deviceName);

    long counter = 0;
    long errors = 0;

    std::vector<int> eventIds;
    eventIds.reserve(100'000);

    Tango::CallBack callback{};

    const auto startTime = std::chrono::system_clock::now();
    auto endTime = startTime;

    while (timeDelta(startTime, endTime) < period)
    {
        try
        {
            int eventId = proxy.subscribe_event(
                attributeName,
                Tango::EventType::CHANGE_EVENT,
                &callback);

            eventIds.push_back(eventId);

            counter++;
        }
        catch (...)
        {
            errors++;
        }
        endTime = std::chrono::system_clock::now();
    }

    for (const auto eventId : eventIds)
    {
        try
        {
            proxy.unsubscribe_event(eventId);
        }
        catch (const Tango::DevFailed& e)
        {
            std::cerr << "unsubscribe_event failed: " << e.errors[0].desc << "\n";
        }
    }


    std::cout
        << counter << " "
        << timeDelta(startTime, endTime) << " "
        << errors << "\n";

    return 0;
}
