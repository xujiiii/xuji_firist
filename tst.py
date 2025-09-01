def aa(fuc):
    def wrapper(*args, **kwargs):
        a=fuc(*args, **kwargs)+1
        
        
        return a
    
    
    return wrapper


@aa
def pp(a):

    return a

print(pp(2))

import re 

print(re.match(r'^cf-[A-Za-z0-9]+-.+','cf-pp-o0:@";o')[0].split('-')[1])

import socket

# 获取主机名
hostname = socket.gethostname()

# 根据主机名解析 IP
ip_address = socket.gethostbyname(hostname)

print(f"本机主机名: {hostname}")
print(f"本机 IPv4 地址: {ip_address}")
