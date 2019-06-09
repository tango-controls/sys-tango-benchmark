package com.s2innovation.tango.benchmark.client.write;

import fr.esrf.TangoApi.DeviceProxy;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.Tango.DevFailed;
import java.util.List;
import java.util.ArrayList;

public class App 
{
    private static String getOption(String name) {
        return System.getenv("_TANGO_BENCHMARK_" + name);
    }

    private static double timeDelta(long t1, long t2) {
        return (double)(t2-t1)/1000.0;
    }

    private static int[] parseShape(String inputStr) {
        final List<Integer> shape = new ArrayList<Integer>();
        for (final String s : inputStr.split(",")) {
            try {
                shape.add(Integer.parseInt(s));
            } catch(Exception e) {
            }
        }
        return shape.stream().mapToInt(i->i).toArray();
    }

    private static double[] parseValue(String inputStr) {
        final List<Double> value = new ArrayList<Double>();
        for (final String s : inputStr.split(",")) {
            final String val = s.replace("m", "-");
            try {
                value.add(Double.parseDouble(val));
            } catch(Exception e) {
            }
        }
        if (value.isEmpty()) {
            value.add(0d);
        }
        return value.stream().mapToDouble(i->i).toArray();
    }

    private static double[] multiplyValue(
        double[] value,
        int requiredSize) {
        final List<Double> newValue = new ArrayList<Double>();
        for (int i = 0; i < requiredSize; i++) {
            newValue.add(value[i % value.length]);
        }
        return newValue.stream().mapToDouble(i->i).toArray();
    }

    private static DeviceAttribute makeAttribute(
        String name,
        double[] value,
        int[] shape) {
        switch (shape.length) {
        case 0:
            if (value.length == 1) {
                return new DeviceAttribute(name, value[0]);
            } else {
                return new DeviceAttribute(name, value, value.length, 1);
            }
        case 1: {
            double[] tmpValue = multiplyValue(value, shape[0]);
            return new DeviceAttribute(name, tmpValue, shape[0], 1);
        }
        default: {
            double[] tmpValue = multiplyValue(value, shape[0] * shape[1]);
            return new DeviceAttribute(name, tmpValue, shape[0], shape[1]);
        }
        }
    }

    public static void main(String[] args)
    {

        final String deviceName = getOption("device");
        final String attributeName = getOption("attribute");
        final String periodStr = getOption("period");
        final String valueStr = getOption("value");
        final String shapeStr = getOption("shape");

        if (deviceName == null
            || attributeName == null
            || periodStr == null
            || valueStr == null
            || shapeStr == null)
        {
            System.exit(1);
        }

        double period = 0;
        try {
            period = Double.parseDouble(periodStr);
        }
        catch (Exception e) {
            System.exit(1);
        }

        DeviceProxy proxy = null;
        try {
            proxy = new DeviceProxy(deviceName);
        } catch (DevFailed e) {
            System.exit(1);
        }

        DeviceAttribute attribute = makeAttribute(
            attributeName,
            parseValue(valueStr),
            parseShape(shapeStr));

        long counter = 0;
        long errors = 0;

        long startTime = System.currentTimeMillis();
        long endTime = startTime;

        while (timeDelta(startTime, endTime) < period) {
            try {
                proxy.write_attribute(attribute);
                counter++;
            } catch (DevFailed e) {
                errors++;
            }
            endTime = System.currentTimeMillis();
        }

        System.out.println(
            Long.toString(counter) + " " +
            Double.toString(timeDelta(startTime, endTime)) + " " +
            Long.toString(errors));
    }
}
