# app/utils/netdiscover.py

from scapy.all import ARP, Ether, srp
from typing import List, Dict

def arp_scan(network: str, timeout: float = 2) -> List[Dict[str, str]]:
    """
    Sends ARP requests to the given network (e.g. "192.168.1.0/24").
    Returns a list of { ip, mac } for each responsive host.
    """
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
    ans, _ = srp(packet, timeout=timeout, verbose=False)
    results = []
    for _, r in ans:
        results.append({"ip": r.psrc, "mac": r.hwsrc})
    return results
