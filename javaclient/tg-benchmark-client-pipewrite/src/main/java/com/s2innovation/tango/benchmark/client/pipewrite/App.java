package com.s2innovation.tango.benchmark.client.pipewrite;

import fr.esrf.TangoApi.DeviceProxy;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.TangoApi.PipeDataElement;
import fr.esrf.TangoApi.DevicePipe;
import fr.esrf.TangoApi.PipeBlob;
import fr.esrf.Tango.DevPipeDataElt;
import fr.esrf.Tango.DevFailed;
import java.util.List;
import java.util.ArrayList;
import java.util.function.Function;

public class App 
{
    private static String getOption(String name) {
        return System.getenv("_TANGO_BENCHMARK_" + name);
    }

    private static double timeDelta(long t1, long t2) {
        return (double)(t2-t1)/1000.0;
    }

    private static List<Function<Integer, PipeDataElement>> makeDataElements() {
        final short[] shortArray = {0, 1, 2, 3, 4};
        final double[] doubleArray = {1.11, 2.22};

        List<Function<Integer, PipeDataElement>> des = new ArrayList<Function<Integer, PipeDataElement>>();
        des.add((i) -> new PipeDataElement(Integer.toString(i) + "DevLong64", (long)123));
        des.add((i) -> new PipeDataElement(Integer.toString(i) + "DevULong", (int)123));
        des.add((i) -> new PipeDataElement(Integer.toString(i) + "DevVarUShortArray",  shortArray));
        des.add((i) -> new PipeDataElement(Integer.toString(i) + "DevVarDoubleArray", doubleArray));
        des.add((i) -> new PipeDataElement(Integer.toString(i) + "DevBoolean", true));

        return des;
    }

    private static DevicePipe makePipeBlob(String name, int size) {
        PipeBlob blob = new PipeBlob(name);
        final List<Function<Integer, PipeDataElement>> des = makeDataElements();

        for (int i = 0; i < size; i++) {
            final PipeDataElement elem = des.get(i % des.size()).apply(i);
            blob.add(elem);
        }

        return new DevicePipe(name, blob);
    }

    public static void main(String[] args)
    {

        final String deviceName = getOption("device");
        final String pipeName = getOption("pipe");
        final String periodStr = getOption("period");
        final String sizeStr = getOption("size");

        if (deviceName == null
            || pipeName == null
            || periodStr == null
            || sizeStr == null)
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

        int size = 0;
        try {
            size = Integer.parseInt(sizeStr);
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

        DevicePipe pipe = makePipeBlob(pipeName, size);

        long counter = 0;
        long errors = 0;

        long startTime = System.currentTimeMillis();
        long endTime = startTime;

        while (timeDelta(startTime, endTime) < period) {
            try {
                proxy.writePipe(pipe);
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
