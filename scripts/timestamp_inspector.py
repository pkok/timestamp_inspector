#!/usr/bin/env python

import collections
import sys
from decimal import Decimal

import rosbag
from rospy import Duration

class Statistics(object):
    def __init__(self, topic, durations):
        self.topic = topic
        count = len(durations)
        quartile_pos = count / 4
        self.sorted = sorted(map(lambda d: d, durations))
        self.quartiles = [
                self.sorted[int(quartile_pos)],
                self.sorted[int(2*quartile_pos)],
                self.sorted[int(3*quartile_pos)],
        ]
        self.median = self.quartiles[1]
        self.average = sum(self.sorted) / count
        square_diff = lambda d: (d - self.average)**2
        squared_diff_from_avg = map(square_diff, self.sorted)
        self.stdev = (sum(squared_diff_from_avg) / count).sqrt()
        self._stdev_percent = self.stdev / self.average * 100
        self.count = count

    def __repr__(self):
        return """
Topic:      %s
# Messages: %s
Quartiles:  %s
Average:    % 15.5f
StDev:      % 15.5f
         =  % 15.5f %% of average""" % (self.topic, self.count, 
                 self.quartiles, self.average, self.stdev,
                 self._stdev_percent)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "Usage:"
        print "    %s BAG_NAME" % sys.argv[0]
        sys.exit()

    BAG_NAME = sys.argv[1]
    GLOBAL_TIME = "global"

    bag = rosbag.Bag(BAG_NAME)

    timestamps = collections.defaultdict(list)
    durations = {}
    statistics = []

    for topic, msg, time in bag.read_messages():
        timestamps[GLOBAL_TIME].append(time)
        if hasattr(msg, 'header'):
            timestamps[topic].append(msg.header.stamp)

    mapping = lambda t1, t2: Decimal((t1 - t2).to_nsec())
    for topic, stamps in timestamps.iteritems():
        durations[topic] = map(mapping, stamps[1:], stamps[:-1])
        statistics.append(Statistics(topic, durations[topic]))

    print "RESULTS"
    for stats in statistics:
        print stats
        print 20*"-"
