vmstat () {
	/usr/bin/vmstat -S K 300 2 \
		| /usr/bin/tail -n1 \
		| /bin/sed 's/^  *//' \
		| /bin/sed 's/  */\n/g' \
		>/var/local/snmp/vmstat.tmp$$
	/bin/grep '^MemTotal:' /proc/meminfo \
		| /bin/sed 's/^.* \([0-9]\{1,\}\) .*$/\1/' \
		>>/var/local/snmp/vmstat.tmp$$
	mv /var/local/snmp/vmstat.tmp$$ /var/local/snmp/vmstat
}

# background the vmstat run
vmstat &
