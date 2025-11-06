Task:
Create a dockerized service that fetches NIFTY 500 index data for the last 7
days and generates alerts. 

Alert trigger:
If today's close from last day's close is less than 2%, trigger an alert.
OR
If today's close from second last day's close is less than 2%, trigger an alert.
OR
...
OR
If today's close from 6th last day's close is less than 2%, trigger an alert.

Write the app in such a way that it is extensible. We might want to add other
indices or different trigger.

Alerts should be generated using https://github.com/binwiederhier/ntfy. We want to
self-host it. You will have to do it so that our service and ntfy works
together. Create a docker-compose file.

The service should check for alert trigger condition once a day at 4pm.

Use context7 MCP to get updated information about anything.

