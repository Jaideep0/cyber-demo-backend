# app/tasks.py

from app.celery_app import celery
import nmap  # python-nmap wrapper

@celery.task(name="app.tasks.scan_nmap")
def scan_nmap(target: str):
    """
    Runs an Nmap service-version scan against the target and
    returns a dict mapping port → service info.
    """
    nm = nmap.PortScanner()
    nm.scan(target, arguments='-sV')
    # Check that the host was actually scanned
    hosts = nm.all_hosts()
    if target not in hosts:
        # Host unreachable or no scan results
        return {}
    # Return TCP port/services mapping
    return nm[target].get('tcp', {})
