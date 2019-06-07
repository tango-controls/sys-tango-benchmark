package com.s2innovation.tango.benchmark.client.command;

import fr.esrf.TangoApi.DeviceProxy;
import fr.esrf.Tango.DevFailed;

public class App 
{
    private static String getOption(String name)
    {
        return System.getenv("_TANGO_BENCHMARK_" + name);
    }

    private static double timeDelta(long t1, long t2)
    {
        return (double)(t2-t1)/1000.0;
    }

    public static void main(String[] args)
    {

        final String deviceName = getOption("device");
        final String commandName = getOption("command");
        final String periodStr = getOption("period");

        if (deviceName == null || commandName == null || periodStr == null)
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

        long counter = 0;
        long errors = 0;

        long startTime = System.currentTimeMillis();
        long endTime = startTime;

        while (timeDelta(startTime, endTime) < period) {
            try {
                proxy.command_inout(commandName);
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
