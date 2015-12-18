#!/usr/bin/env python
# coding=utf-8

from optparse import OptionParser

# parse args to options
parser = OptionParser()
parser.add_option("--host", dest="host", default="localhost",
                  help="the ip to binding with(may need root)", type="string")
parser.add_option("--port", dest="port", default=8080,
                  help="the port to listen", type="int")
parser.add_option("-x", action="store_true", dest="xheader", help="get real ip from xheader")
parser.add_option("-d", action="store_true", dest="debug", help="run with debug mode")
parser.add_option("-s", action="store_true", dest="setup", help="do setup for the first time")
parser.add_option("-c", action="store_true", dest="clear", help="clear database when doing setup")
(options, args) = parser.parse_args()


if __name__ == '__main__':
    if options.setup:
        from core.models import drop_all, create_all, get_engine
        engine = get_engine(echo=True)
        if options.clear:
            drop_all(engine)
        create_all(engine)
        print("ChocoBlog setup complete.")
    else:
        from core.application import app
        app.run(host=options.host, port=options.port, debug=options.debug)
