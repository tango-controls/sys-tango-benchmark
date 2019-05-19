package org.tango.javabenchmarktarget;

import fr.esrf.Tango.DevFailed;
import java.lang.Thread;
import java.util.concurrent.atomic.AtomicBoolean;

import org.tango.javabenchmarktarget.JavaBenchmarkTarget;

class EventThread extends Thread {

    private JavaBenchmarkTarget server;
    private int eventSleepPeriod;
    public final AtomicBoolean running = new AtomicBoolean(true);
    public final AtomicBoolean finished = new AtomicBoolean(false);
    private volatile int counter;
    private volatile int errorCounter;
    private final Object lock = new Object();
    
    EventThread(JavaBenchmarkTarget server,
		int eventSleepPeriod){
	this.server = server;
	this.eventSleepPeriod = eventSleepPeriod;
    }

    public int getCounter(){
	int counter;
	synchronized (lock) {
	    counter = this.counter;
	}
	return counter;
    }

    public int getErrorCounter(){
	int counter;
	synchronized (lock) {
	    counter = this.errorCounter;
	}
	return counter;
    }

    public void setFinished(boolean value){
        while(true) {
	    boolean existingValue = finished.get();
            if(finished.compareAndSet(existingValue, value)) {
                break;
            }
        }
    }
    
    public void setRunning(boolean value){
        while(true) {
	    boolean existingValue = running.get();
            if(running.compareAndSet(existingValue, value)) {
                break;
            }
        }
    }
    
    public boolean getRunning(){
	return running.get();
    }
    
    public boolean getFinished(){
	return finished.get();
    }
    
    public void run() {
	while(running.get()){
	    try{
	        synchronized (lock) {
		    server.PushEvent();
		    counter++;
		}
	    }
	    catch(DevFailed e){
	        synchronized (lock) {
		    errorCounter++;
		}
	    }
	    
	    if(running.get()){
		try{
		    sleep(eventSleepPeriod);
		}
		catch(java.lang.InterruptedException e){
		}
	    }
	}
	setFinished(true);
    }
}
