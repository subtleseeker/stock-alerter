Task:
Create a dockerized service that fetches NIFTY 500 index data for the last 7
days and generates alerts. 

Alert trigger:
If today's close from one of the last 7 day's close is less than 2%, trigger an alert. If there are multiple of such dates, trigger alert for the maximum % change.
For example:
Today's close: 800
Last day's close: 801
Last 2nd day's close: 802
Last 3rd day's close: 804
Last 4rd day's close: 805
Last 5rd day's close: 809
Last 6rd day's close: 840

The maximum change is (800-840)/840-1=-4.7%
The dip is 4.7% maximum in the last 7 days. We should generate alert saying 4.7% change in last 6 days.

We should have atleast 2 data sources in case one of them doesn't work.

Write the app in such a way that it is extensible. We might want to add other
indices or different trigger.

Alerts should be generated using https://docs.ntfy.sh/. We want to
self-host it. You will have to do it so that our service and ntfy works
together. Create a docker-compose file. 
Our topic name is "niftyy".

The service should check for alert trigger condition once a day at 4pm.

Remember to always run the service after building to really see that it works. 

Use context7 MCP to get updated information about anything.

I have cloned an external repository that might be useful to find the data
sources and how to use them. It is present in repo/ directory.
