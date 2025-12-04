# # ARP sweep single subport 
# import subprocess
# import platform

# def icmp_ping(ip):
#     # OS-specific flag (-n for windows, -c for linux/mac)
#     flag = "-n" if platform.system().lower() == "windows" else "-c"
    
#     command = ["ping", flag, "1", ip]  # send only one request
#     response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
#     if response.returncode == 0:
#         print(f"[+] {ip} is active")
#     else:
#         print(f"[-] {ip} did not respond")

# # Example usage: full network loop
# for i in range(1, 255):
#     icmp_ping(f"192.168.1.{i}")

# ARP sweep multiple subport range 0 to n 
# import ipaddress, subprocess, re, asyncio

# # ---------- Step 1: get local subnet automatically ----------
# def get_subnet_from_ifconfig():
#     text = subprocess.check_output("ifconfig", shell=True).decode()
#     match = re.search(r"inet\s+(192\.168\.\d+\.\d+)\s+netmask\s+0x(\w+)", text)
#     if match:
#         ip = match.group(1)               # → e.g. 192.168.0.107
#         mask_hex = match.group(2)
#         mask = ".".join(str(int(mask_hex[i:i+2],16)) for i in range(0,8,2))
#         return ip, mask
#     return None, None


# # ---------- Step 2: async ping for given subnet ----------
# async def ping(ip):
#     proc = await asyncio.create_subprocess_shell(
#         f"ping -c 1 -W 1 {ip} > /dev/null",
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE,
#     )
#     await proc.communicate()


# async def scan_subnet(subnet):
#     ips = [str(ip) for ip in ipaddress.ip_network(subnet, strict=False).hosts()]
#     tasks = [ping(ip) for ip in ips]
#     await asyncio.gather(*tasks)


# # ---------- Step 3: read ARP table ----------
# def read_arp_table():
#     out = subprocess.check_output("arp -a", shell=True).decode()
#     devices=[]
#     for line in out.splitlines():
#         m=re.search(r"\((192\.168\.\d+\.\d+)\)\sat\s([0-9a-f:]+)", line, re.I)
#         if m and m.group(2) != "ff:ff:ff:ff:ff:ff":
#             devices.append((m.group(1), m.group(2)))
#     return devices


# # ---------- Multi‑Subnet Scan Wrapper ----------
# async def multi_subnet_scan(range_start=0, range_end=3):
#     ip,mask = get_subnet_from_ifconfig()
#     if not ip: 
#         print("❌ No IP detected!")
#         return
    
#     base1, base2, _, _ = ip.split(".")            # 192.168.x.x → take 192.168

#     print(f"\n🌍 Multi‑Subnet Scan Range → {base1}.{base2}.{range_start}.0  ➝  {base1}.{base2}.{range_end-1}.255\n")

#     for i in range(range_start, range_end):        # scans x.x.0.x → x.x.2.x default
#         subnet = f"{base1}.{base2}.{i}.0/{mask}"
#         print(f"\n📡 Scanning subnet → {subnet}")
#         await scan_subnet(subnet)

#     print("\n📍 Devices Found (All Subnets):")
#     for ip, mac in read_arp_table():
#         print(f"{ip:15} → {mac}")


# # ---------- Run ----------
# asyncio.run(multi_subnet_scan(range_start=0, range_end=3))



# import ipaddress, subprocess, re, asyncio, time

# # ---------------- 1. Detect local subnet ----------------
# def get_subnet():
#     out = subprocess.check_output("ifconfig", shell=True).decode()
#     m = re.search(r"inet\s+(192\.168\.\d+\.\d+)\s+netmask\s+0x(\w+)", out)
#     if not m:
#         print("❌ No valid LAN interface found")
#         return None

#     ip = m.group(1)
#     mask_hex = m.group(2)
#     mask = ".".join(str(int(mask_hex[i:i+2],16)) for i in range(0,8,2))
#     return ip, mask


# # ---------------- 2. Async Ping ----------------
# async def ping(ip):
#     proc = await asyncio.create_subprocess_shell(
#         f"ping -c 1 -W 1 {ip} > /dev/null",
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE,
#     )
#     await proc.communicate()


# async def scan_single_subnet(subnet):
#     print(f"\n📡 Scanning {subnet}")
#     ips = [str(i) for i in ipaddress.ip_network(subnet, strict=False).hosts()]
#     await asyncio.gather(*[ping(ip) for ip in ips])


# # ---------------- 3. Pull ARP Table ----------------
# def get_devices():
#     arp_out = subprocess.check_output("arp -a", shell=True).decode()
#     devices = []

#     for line in arp_out.splitlines():
#         match = re.search(r"\((192\.168\.\d+\.\d+)\)\sat\s([0-9a-f:]+)", line, re.I)
#         if match and match.group(2) != "ff:ff:ff:ff:ff:ff":
#             devices.append((match.group(1), match.group(2)))

#     return devices


# # ---------------- 4. Multi‑Subnet Scan ----------------
# async def scan_multi(range_start=0, range_end=2):
#     ip, mask = get_subnet()
#     base1, base2, _, _ = ip.split(".")

#     print(f"\n🌍 Multi‑Subnet Range → {base1}.{base2}.{range_start}.0 ➝ {base1}.{base2}.{range_end-1}.255")

#     for n in range(range_start, range_end):
#         subnet = f"{base1}.{base2}.{n}.0/{mask}"
#         await scan_single_subnet(subnet)

#     # second pass ARP refresh for MAC missing devices
#     print("\n🔄 Refreshing ARP for accuracy...")
#     time.sleep(1)                    # let ARP update  

#     print("\n📍 Devices Found:")
#     for ip, mac in get_devices():
#         print(f"{ip:15} →  {mac}")


# # ---------------- RUN ----------------
# asyncio.run(scan_multi(0,2))





# ---------------------------------------------------------------------------------------------------------------
# Smart auto detect subnet scan without sudo 
import ipaddress, subprocess, re, asyncio

# ---------------------------------------
# Get Local Subnet Automatically
# ---------------------------------------
def get_subnet_from_ifconfig():
    txt = subprocess.check_output("ifconfig", shell=True).decode()
    match = re.search(r"inet\s+(192\.168\.\d+\.\d+)\s+netmask\s+0x(\w+)", txt)
    if match:
        ip = match.group(1)
        mask_hex = match.group(2)
        mask = ".".join(str(int(mask_hex[i:i+2],16)) for i in range(0,8,2))
        return ip, mask
    return None, None


# ---------------------------------------
# Async Ping Faster
# ---------------------------------------
async def ping(ip):
    proc = await asyncio.create_subprocess_shell(
        f"ping -c 1 -W 1 {ip} >/dev/null",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()


async def scan_subnet(subnet):
    hosts = [str(ip) for ip in ipaddress.ip_network(subnet, strict=False).hosts()]
    await asyncio.gather(*[ping(h) for h in hosts])


# ---------------------------------------
# Read ARP Results
# ---------------------------------------
def get_arp_devices():
    out = subprocess.check_output("arp -a", shell=True).decode()
    found=[]
    for line in out.splitlines():
        m = re.search(r"\((192\.168\.\d+\.\d+)\)\sat\s([0-9a-f:]+)", line, re.I)
        if m: found.append((m.group(1), m.group(2)))
    return found


# ---------------------------------------
# SMART EXPANDING SCANNER
# ---------------------------------------
async def smart_scan():
    ip, mask = get_subnet_from_ifconfig()
    if not ip: return print("\n❌ No network detected\n")

    base1, base2, curr, _ = ip.split(".")
    curr = int(curr)

    print(f"\n🚀 SmartScan started from → {base1}.{base2}.{curr}.x\n")

    scanned=set()
    new_discovered=[]
    direction_offsets=[-1, +1]   # left, right

    # Start by scanning our own subnet
    subnet=f"{base1}.{base2}.{curr}.0/{mask}"
    print(f"📡 Scanning → {subnet}")
    await scan_subnet(subnet)
    scanned.add(curr)

    base_devices=len(get_arp_devices())
    print(f"🟢 {base_devices} known devices at start\n")

    # Expand outward until 2 empty-hit streak
    streak=0
    step=1

    while streak < 2:   # your rule
        any_new=False

        for d in direction_offsets:
            n = curr + (step*d)
            if n < 0 or n > 255 or n in scanned: continue

            subnet=f"{base1}.{base2}.{n}.0/{mask}"
            print(f"📡 Scanning → {subnet}")
            await scan_subnet(subnet)
            scanned.add(n)

            after=len(get_arp_devices())
            if after > base_devices:
                print(f"🟢 New devices found in {n}.x — continuing\n")
                base_devices = after
                any_new=True
            else:
                print(f"🔴 No new devices in {n}.x\n")

        if not any_new: streak+=1
        else: streak=0
        step+=1

    # Final Report
    print("\n────────── 📍 Final Discovered Devices ──────────")
    for ip,mac in get_arp_devices(): print(f"{ip:15} → {mac}")
    print("────────────────────────────────────────────────\n")


# ---------------------------------------
# Run
# ---------------------------------------
asyncio.run(smart_scan())


# platform indepentant works fine on macos


import os
import re
import ipaddress
import subprocess
import asyncio
import platform

# ===============================================================
# 🔍 OS Detection
# ===============================================================
IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"


# ===============================================================
# 🔥 macOS Network Scanner (Your Working Version)
# ===============================================================
def get_subnet_from_ifconfig_mac():
    txt = subprocess.check_output("ifconfig", shell=True).decode()
    match = re.search(r"inet\s+(192\.168\.\d+\.\d+)\s+netmask\s+0x(\w+)", txt)
    if match:
        ip = match.group(1)
        mask_hex = match.group(2)
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
        if m: devices.append((m.group(1), m.group(2)))
    return devices



# ===============================================================
# 🪟 WINDOWS SCANNER
# ===============================================================
def get_subnet_windows():
    try:
        txt = subprocess.check_output("ipconfig", shell=True).decode(errors="ignore")
        match = re.search(r"IPv4 Address.*?:\s*(192\.168\.\d+\.\d+)", txt)
        mask = re.search(r"Subnet Mask.*?:\s*(\d+\.\d+\.\d+\.\d+)", txt)

        if match and mask:
            return match.group(1), mask.group(1)
    except:
        pass
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
            ip = re.search(r"192\.168\.\d+\.\d+", line).group()
            mac = m.group(1).replace("-",":")
            devices.append((ip, mac))
    return devices



# ===============================================================
# 🚀 MASTER LAUNCHER
# ===============================================================
async def smartscan():
    print("\n🔍 Detected OS →", platform.system(), "\n")

    if IS_MAC:   # ---------------- MAC MODE -------------------
        ip, mask = get_subnet_from_ifconfig_mac()
        if not ip: return print("❌ No network detected")

        base1,base2,curr,_ = ip.split(".")
        curr=int(curr)

        print(f"\n🚀 SmartScan macOS start → {base1}.{base2}.{curr}.x")

        subnet=f"{base1}.{base2}.{curr}.0/{mask}"
        print("📡 Scanning:", subnet)
        await scan_subnet_mac(subnet)

        print("\n──────── Devices Found ────────")
        for ip,mac in get_arp_devices_mac(): print(f"{ip:15} → {mac}")
        print("───────────────────────────────\n")

    # ================= WINDOWS MODE =====================
    elif IS_WIN:
        ip,mask = get_subnet_windows()
        if not ip: return print("❌ No network detected")

        subnet=f"{ip}/{sum(bin(int(x)).count('1') for x in mask.split('.'))}"
        print(f"🚀 SmartScan Windows start → {subnet}")

        await scan_subnet_win(subnet)

        print("\n──────── Devices Found ────────")
        for ip,mac in get_arp_devices_win(): print(f"{ip:15} → {mac}")
        print("───────────────────────────────\n")


# EXECUTE
asyncio.run(smartscan())
