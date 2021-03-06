#!/usr/bin/env python3
import sys
from ipaddress import IPv4Address, ip_network
from pathlib import Path

import toml

RESOLVE_FILE = Path("dns", "db.10.127")
ROUTE_FILE = Path("route")


def iter_route(route_type: str):
    items = []
    for f in ROUTE_FILE.iterdir():
        routes = toml.loads(f.read_text())
        items.extend(
            (entity["name"], ip_network(route).network_address)
            for route, entity in routes.items()
            if entity["type"] == route_type
        )
    return sorted(items, key=lambda item: item[1])


def main():
    orignal = RESOLVE_FILE.read_text()
    orignal = orignal[: orignal.find("\n; AUTOGENERATED")]
    records = [orignal, "; AUTOGENERATED", "", "; Loopback Addresses"]
    for name, address in iter_route("loopback"):
        if isinstance(address, IPv4Address):
            pointer = address.reverse_pointer.replace(".127.10.in-addr.arpa", "")
            records.append("%s\tIN\tPTR\t%s.neo." % (pointer, name))
    RESOLVE_FILE.write_text("\n".join(records))


if __name__ == "__main__":
    main()
