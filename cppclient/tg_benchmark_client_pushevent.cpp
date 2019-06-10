#include <cstdlib>
#include <iostream>
#include <chrono>
#include <string>
#include <memory>
#include <thread>

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

struct TangoCounterCb : public Tango::CallBack
{
    int counter = 0;
    int errors = 0;

    virtual void push_event(Tango::EventData* ev) override
    {
        if (ev->err)
        {
            errors++;
        }
        else
        {
            counter++;
        }
    }
};

int main(int, char**)
{
    const char* deviceName = getOption("device");
    const char* attributeName = getOption("attribute");
    const char* periodStr = getOption("period");
    const char* sleepStr = getOption("sleep");

    if (not (deviceName and attributeName and periodStr and sleepStr))
    {
        return 1;
    }

    const double period = std::atof(periodStr);
    const double sleep = std::atof(sleepStr);

    std::unique_ptr<Tango::DeviceProxy> proxy;

    try
    {
        proxy = std::make_unique<Tango::DeviceProxy>(deviceName);
        proxy->set_timeout_millis(2000);
        {
            Tango::DbDatum dbd("EventAttribute");
            dbd << attributeName;
            Tango::DbData db{};
            db.push_back(dbd);
            proxy->put_property(db);
        }
        {
            Tango::DbDatum dbd("EventSleepPeriod");
            dbd << sleep;
            Tango::DbData db{};
            db.push_back(dbd);
            proxy->put_property(db);
        }
    }
    catch (const Tango::DevFailed& e)
    {
        Tango::Except::print_exception(e);
        std::cout << "0 0 0\n";
        return 1;
    }


    TangoCounterCb callback{};

    auto startTime = std::chrono::system_clock::now();
    auto endTime = startTime + std::chrono::seconds(1);

    try
    {
        const int eventId = proxy->subscribe_event(
            attributeName,
            Tango::EventType::CHANGE_EVENT,
            &callback);

        std::this_thread::sleep_for(std::chrono::seconds(1));

        startTime = std::chrono::system_clock::now();
        try {
            proxy->command_inout("StartEvents");
            std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<long>(1000.0*period)));
            proxy->command_inout("StopEvents");
        } catch (...) {
        }
        endTime = std::chrono::system_clock::now();

        std::this_thread::sleep_for(std::chrono::seconds(1));

        proxy->unsubscribe_event(eventId);

    } catch (...) {
    }

    std::cout
        << callback.counter << " "
        << timeDelta(startTime, endTime) << " "
        << callback.errors << "\n";

    return 0;
}
