import ipaddress


def is_private_ip(ip):
    return ipaddress.ip_address(ip).is_private

# print(is_private_ip('10.10.10.10'))
