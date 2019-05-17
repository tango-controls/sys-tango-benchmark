#include "EventThread.h"

namespace CppBenchmarkTarget_ns
{

  EventThread::EventThread(CppBenchmarkTarget* objServer,
			   long speriod, omni_mutex& mutex)
    :omni_thread(),
     m_objServer(objServer),
     m_speriod(speriod),
     m_mutex(mutex),
     running(true),
     finished(false),
     counter(0),
     errorcounter(0)
  {
    start_undetached();
  }

  EventThread::~EventThread()
  {
  }

  void* EventThread::run_undetached(void*)
  {
    bool loop = true;
    while(running){
      try{
	{
	  Tango::AutoTangoMonitor synch(m_objServer);
	  m_objServer->push_event();
	}
	{
	  omni_mutex_lock l(m_mutex);
	  counter++;
	}
      }
      catch(...){
	omni_mutex_lock l(m_mutex);
	errorcounter++;
      }
      {
	omni_mutex_lock l(m_mutex);
	loop = running;
      }
      if(loop)
	usleep(m_speriod);
    }
    {
      omni_mutex_lock l(m_mutex);
      finished = true;
    }
    omni_thread::exit();
    return NULL;
  }

} // End of namespace
