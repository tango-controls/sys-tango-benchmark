#ifndef __EVENTTHREAD__
#define __EVENTTHREAD__

#include <tango.h>
#include "CppBenchmarkTarget.h"

namespace CppBenchmarkTarget_ns
{
  class EventThread: public omni_thread
  {
  public:
    EventThread(CppBenchmarkTarget* objServer,
		long speriod, omni_mutex& mutex);
    ~EventThread();
    void *run_undetached(void*);
    bool running;
    bool finished;
    long counter;
    long errorcounter;
  private:
    CppBenchmarkTarget* m_objServer;
    omni_mutex& m_mutex;
    long m_speriod;

  };

} // End of namespace

#endif // __EVENTTHREAD__
