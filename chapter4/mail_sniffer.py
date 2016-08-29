from scapy.all import *

# our packet callback
def packer_callback(packet):
	print packet.show()

# fire up out sniffer
sniff(prn=packer_callback, count=1)
