import json
import sys

from scapy.utils import PcapReader
import scapy.layers.inet

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <filename.pcap>\n\n" % sys.argv[0])
    filename = sys.argv[1]
    messages = [seg for seg in PcapReader(filename) if "TCP" in seg]
    segments = []
    last_ack = {}
    for m in messages:
        segment = {}
        segment["src"] = m.sprintf("%IP.src%:%TCP.sport%")
        segment["dst"] = m.sprintf("%IP.dst%:%TCP.dport%")
        flags = m.sprintf("%TCP.flags%")
        segment["syn"] = "S" in flags
        segment["fin"] = "F" in flags
        segment["rst"] = "R" in flags
        # Acks are special. Not only the A bit must be set, but also the seq number should increase
        if "A" in flags:
            conn_key = (segment["src"], segment["dst"])
            if conn_key in last_ack:
                old_ack = last_ack[conn_key]
            else:
                old_ack = m["TCP"].ack-1
            last_ack[conn_key] = m["TCP"].ack
            segment["ack"] = old_ack != m["TCP"].ack
        else:
            segment["ack"] = False
        segments.append(segment)
    sys.stdout.write("[\n    ")
    sys.stdout.write(",\n    ".join(str(seg) for seg in segments))
    sys.stdout.write("\n]")

if __name__=="__main__":
    main()
