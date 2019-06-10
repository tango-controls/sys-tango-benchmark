package com.s2innovation.tango.benchmark.client.pushevent;

import fr.esrf.TangoApi.DeviceProxy;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.CallBack;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.TangoApi.events.EventData;
import fr.esrf.TangoApi.DbDatum;
import fr.esrf.TangoDs.TangoConst;
import java.util.List;
import java.util.ArrayList;

class TangoCounterCb extends CallBack {

    int counter = 0;
    int errors = 0;

    public void push_event(EventData ev) {
        if (ev.err) {
            errors++;
        } else {
            counter++;
        }
    }
}

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


    private static void sleepSeconds(double seconds) {
        try {
            Thread.sleep((long)(seconds * 1000));
        } catch (InterruptedException e) {
        }
    }

    public static void main(String[] args)
    {

        final String deviceName = getOption("device");
        final String attributeName = getOption("attribute");
        final String periodStr = getOption("period");
        final String sleepStr = getOption("sleep");

        if (deviceName == null
            || attributeName == null
            || periodStr == null
            || sleepStr == null)
        {
            System.exit(1);
        }

        double period = 0;
        try {
            period = Double.parseDouble(periodStr);
        } catch (Exception e) {
            System.exit(1);
        }

        double sleep = 0;
        try {
            sleep = Double.parseDouble(sleepStr);
        } catch (Exception e) {
            System.exit(1);
        }

        DeviceProxy proxy = null;
        try {
            proxy = new DeviceProxy(deviceName);
            proxy.set_timeout_millis(2000);
            proxy.put_property(new DbDatum("EventAttribute", attributeName));
            proxy.put_property(new DbDatum("EventSleepPeriod", sleep));
        } catch (DevFailed e) {
            System.exit(1);
        }

        TangoCounterCb callback = new TangoCounterCb();

        long startTime = System.currentTimeMillis();
        long endTime = startTime + 1000;

        try {
            final int eventId = proxy.subscribe_event(
                attributeName,
                TangoConst.CHANGE_EVENT,
                callback,
                new String[0]);

            sleepSeconds(1);

            startTime = System.currentTimeMillis();
            try {
                proxy.command_inout("StartEvents");
                sleepSeconds(period);
                proxy.command_inout("StopEvents");
            } catch (DevFailed e) {
            }
            endTime = System.currentTimeMillis();

            sleepSeconds(1);

            proxy.unsubscribe_event(eventId);

        } catch (DevFailed e) {
        }

        System.out.println(
            Long.toString(callback.counter) + " " +
            Double.toString(timeDelta(startTime, endTime)) + " " +
            Long.toString(callback.errors));

        System.exit(0);
    }
}
