#include <cstdlib>
#include <iostream>
#include <chrono>
#include <string>
#include <vector>
#include <algorithm>

#include <tango.h>

using Shape = std::vector<int>;
using Value = std::vector<double>;

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

auto parseShape(const char* inputStr)
{
    Shape shape{};
    std::istringstream input(inputStr);
    for (std::string line; std::getline(input, line, ',');)
    {
        shape.push_back(std::atoi(line.c_str()));
    }
    return shape;
}

auto parseValue(const char* inputStr)
{
    Value value{};
    std::istringstream input(inputStr);
    for (std::string line; std::getline(input, line, ',');)
    {
        std::replace(line.begin(), line.end(), 'm', '-');
        value.push_back(std::atoi(line.c_str()));
    }
    if (value.empty())
    {
        value.push_back(0);
    }
    return value;
}

auto multiplyValue(const Value& value, int requiredSize)
{
    Value newValue;
    newValue.reserve(requiredSize);
    for (int i = 0; i < requiredSize; ++i)
    {
        newValue.push_back(value[i % value.size()]);
    }
    return newValue;
}

auto makeAttribute(const char* name, const Value& value, const Shape& shape)
{
    switch (shape.size())
    {
        case 0:
            if (value.size() == 1)
            {
                return Tango::DeviceAttribute(name, value[0]);
            }
            else
            {
                Value tmpValue = value;
                return Tango::DeviceAttribute(name, tmpValue);
            }
        case 1:
        {
            Value tmpValue = multiplyValue(value, shape[0]);
            return Tango::DeviceAttribute(name, tmpValue);
        }
        default:
        {
            Value tmpValue = multiplyValue(value, shape[0] * shape[1]);
            return Tango::DeviceAttribute(name, tmpValue, shape[0], shape[1]);
        }
    }
}

int main(int, char**)
{
    const char* deviceName = getOption("device");
    const char* attributeName = getOption("attribute");
    const char* periodStr = getOption("period");
    const char* valueStr = getOption("value");
    const char* shapeStr = getOption("shape");

    if (not (deviceName
        and attributeName
        and periodStr
        and valueStr
        and shapeStr))
    {
        return 1;
    }

    const double period = std::atof(periodStr);

    auto attribute = makeAttribute(
        attributeName,
        parseValue(valueStr),
        parseShape(shapeStr));

    auto proxy = Tango::DeviceProxy(deviceName);

    long counter = 0;
    long errors = 0;

    const auto startTime = std::chrono::system_clock::now();
    auto endTime = startTime;

    while (timeDelta(startTime, endTime) < period)
    {
        try
        {
            proxy.write_attribute(attribute);
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
