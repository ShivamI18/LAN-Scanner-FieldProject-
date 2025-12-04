import ipaddress
import subprocess
import re
import asyncio
import platform
import json

IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"

# --------------------
# Device type detection
# --------------------
def detect_device(ip, mac):
    # Router detection by IP
    if ip.endswith(".1") or ip.endswith(".254"):
        return "Router"

    # Broadcast / unknown network
    if mac.lower() == "ff:ff:ff:ff:ff:ff":
        return "Network Broadcast / Unknown Device"

    # TTL detection
    ttl = None
    try:
        if IS_MAC:
            out = subprocess.check_output(f"ping -c 1 -W 1 {ip}", shell=True, timeout=2).decode(errors="ignore")
            ttl_match = re.search(r"ttl=(\d+)", out, re.IGNORECASE)
            if ttl_match:
                ttl = int(ttl_match.group(1))
        elif IS_WIN:
            out = subprocess.check_output(f"ping -n 1 -w 200 {ip}", shell=True, timeout=2).decode(errors="ignore")
            ttl_match = re.search(r"TTL[=|:](\d+)", out, re.IGNORECASE)
            if ttl_match:
                ttl = int(ttl_match.group(1))
    except:
        pass

    if ttl is not None:
        if ttl >= 200:
            return "Laptop / macOS / iOS"
        elif ttl >= 128:
            return "Laptop / Windows"
        elif ttl >= 64:
            return "Phone / Tablet / Android / Linux"

    # Fallback
    return "Unknown Device"


# ---------------- MAC ----------------
def get_subnet_mac():
    txt = subprocess.check_output("ifconfig", shell=True).decode()
    m = re.search(r"inet\s+(192\.168\.\d+\.\d+)\s+netmask\s+0x(\w+)", txt)
    if m:
        ip = m.group(1)
        mask_hex = m.group(2)
        mask = ".".join(str(int(mask_hex[i:i+2],16)) for i in range(0,8,2))
        return ip, mask
    return None, None

async def ping_mac(ip):
    proc = await asyncio.create_subprocess_shell(
        f"ping -c 1 -W 1 {ip} >/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()

async def scan_subnet_mac(subnet):
    hosts = [str(ip) for ip in ipaddress.ip_network(subnet, strict=False).hosts()]
    await asyncio.gather(*[ping_mac(h) for h in hosts])

def get_arp_devices_mac():
    out = subprocess.check_output("arp -a", shell=True).decode()
    devices=[]
    for line in out.splitlines():
        m = re.search(r"\((192\.168\.\d+\.\d+)\)\sat\s([0-9a-f:]+)", line, re.I)
        if m:
            ip  = m.group(1)
            mac = m.group(2)
            devices.append({
                "ip": ip,
                "mac": mac,
                "device_type": detect_device(ip, mac)
            })
    return devices


# ---------------- WINDOWS ----------------
def get_subnet_win():
    txt = subprocess.check_output("ipconfig", shell=True).decode(errors="ignore")
    ip = re.search(r"IPv4 Address.*?:\s*(192\.168\.\d+\.\d+)", txt)
    mask = re.search(r"Subnet Mask.*?:\s*(\d+\.\d+\.\d+\.\d+)", txt)
    if ip and mask: return ip.group(1), mask.group(1)
    return None, None

async def ping_win(ip):
    proc = await asyncio.create_subprocess_shell(
        f"ping -n 1 -w 200 {ip} >NUL",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()

async def scan_subnet_win(subnet):
    hosts=[str(ip) for ip in ipaddress.ip_network(subnet, strict=False).hosts()]
    await asyncio.gather(*[ping_win(h) for h in hosts])

def get_arp_devices_win():
    out = subprocess.check_output("arp -a", shell=True).decode(errors="ignore")
    devices=[]
    for line in out.splitlines():
        m = re.search(r"192\.168\.\d+\.\d+\s+dynamic\s+([0-9a-f-]+)", line, re.I)
        if m:
            ip  = re.search(r"192\.168\.\d+\.\d+", line).group()
            mac = m.group(1).replace("-",":")
            devices.append({
                "ip": ip,
                "mac": mac,
                "device_type": detect_device(ip, mac)
            })
    return devices


# ---------------- MASTER ----------------
async def main():
    if IS_MAC:
        ip, mask = get_subnet_mac()
        if not ip: return print(json.dumps([]))
        await scan_subnet_mac(f"{ip}/{mask}")
        devices = get_arp_devices_mac()

    elif IS_WIN:
        ip, mask = get_subnet_win()
        if not ip: return print(json.dumps([]))
        await scan_subnet_win(f"{ip}/{mask}")
        devices = get_arp_devices_win()

    else:
        return print(json.dumps([]))

    print(json.dumps(devices, indent=2))


asyncio.run(main())
