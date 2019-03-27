#!/usr/bin/env python

from tangobenchmarks import servers
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="waits till the device is running")
    parser.add_argument('devices', metavar='N', type=str, nargs='*',
                        help='a list of devices to wait for')

    args = parser.parse_args()
    if not args.devices:
        args.devices = ["sys/tg_test/1"]

    st = servers.Starter(None, None)

    for device in args.devices:
        print("Waiting for: %s" % device)
        status = st.checkDevice(device, 300)
        if not status:
            print("%s is not running" % device)
    

if __name__ == "__main__":
    main()
