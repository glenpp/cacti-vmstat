# vmstat on Cacti via SNMP

## vmstat to SNMP

I run a cron job to pick up data and dump it in files where snmpd can pick it up as a low privilege user. I'm doing the same here, except that I'm using it to run vmstat in the background to collect data over the polling period.

Take the data collection script **vmstat\_cron.py**, make this executable and stick it somewhere convenient. I will assume **/etc/snmp/** for this article with the output files in **/var/local/snmp/**. Then run this every 5 minutes (or matching your Cacti polling interview) with a cron job - eg. some lines to run this in the background:

```sh
/etc/snmp/vmstat_cron.py /var/local/snmp/vmstat &
```

That will launch vmstat in a wrapper which will run for 5 minutes (300 seconds) outputting to a temporary file and rename the temporary file to the name given as the first argument. You can easily alter the script if you poll more/less frequently.

Check that the output file is being created and has data in it - it will take 5 minutes from the next cron run before the file is created. Next, to get the data into snmpd add the line from **snmpd.conf.cacti-vmstat** to the **/etc/snmp/snmpd.conf** file.

That simply picks up the contents of the file when SNMP is queried. Restart snmpd and you should be able to test that with snmpwalk.

## SNMP to Cacti

Import the Cacti template **cacti_host_template_vmstat.xml** and add it to the host you have configured above. Add the graphs and all going well after a couple polls data should start appearing on the graphs.