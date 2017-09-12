from scapy.utils import PcapReader
import scapy.layers.inet
filename = "textfile.pcap"

xs = [x for x in PcapReader(filename)]
ys = [x for x in xs if "TCP" in x and "Raw" in x]
ws = [x for x in xs if "TCP" in x and "Raw" not in x]