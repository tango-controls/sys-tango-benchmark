package com.s2innovation.tango.benchmark.client.event;

import fr.esrf.TangoApi.DeviceProxy;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.CallBack;
import fr.esrf.TangoDs.TangoConst;
import java.util.List;
import java.util.ArrayList;

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
        final String attributeName = getOption("attribute");
        final String periodStr = getOption("period");

        if (deviceName == null || attributeName == null || periodStr == null)
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

        CallBack callback = new CallBack();

        List<Integer> eventIds = new ArrayList<Integer>();

        long startTime = System.currentTimeMillis();
        long endTime = startTime;

        while (timeDelta(startTime, endTime) < period) {
            try {
                final int eventId = proxy.subscribe_event(
                    attributeName,
                    TangoConst.CHANGE_EVENT,
                    callback,
                    new String[0]);

                eventIds.add(eventId);
                counter++;
            } catch (DevFailed e) {
                errors++;
            }
            endTime = System.currentTimeMillis();
        }

        for (final Integer i : eventIds) {
            try {
                proxy.unsubscribe_event(i);
            } catch (DevFailed e) {
            }
        }

        System.out.println(
            Long.toString(counter) + " " +
            Double.toString(timeDelta(startTime, endTime)) + " " +
            Long.toString(errors));

        System.exit(0);
    }
}
