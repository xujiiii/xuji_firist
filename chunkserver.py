import threading
import socket
import json
import time

# 获取主机名.
hostname = socket.gethostname()

# 根据主机名解析 IP
ip_address = socket.gethostbyname(hostname)

class Server:
    def __init__(self,name,host=ip_address, port_master=12454,port_server=12222):
        #name to identify this server
        self.name=name
        #which chunks have in this server
        self.chunk=['chunk5','chunk4'] #[[chunkname,chunkdata,version]]

        #set the socket for connecting master and listenning clients
        self.host=host
        self.port_master=port_master
        self.port_server=port_server
        self.master=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #start two thread to deal with connections to master and clients separately 
    def start(self):
        self.master.connect((self.host, self.port_master))
        print(f"[连接] 已连接到服务器 {self.host}:{self.port_master}")
        # 开启线程与服务器注册及心跳
        thread1 = threading.Thread(target=self.heartbeat())
        thread1.daemon = True
        thread1.start()

        self.server.bind(self.host,self.port_server)
        self.server.listen(5)
        print(f"[启动] server已启动,监听 {self.host}:{self.port_server}")
        thread2 = threading.Thread(target=self.receive_msg())
        thread2.daemon = True
        thread2.start()

        
    # 接收clients消息,线程一直运行中
    def receive_msg(self):
        while True:
            try:
                length = self.server(8)
                leng=int.from_bytes(length)
                msg=self.server.recv(leng).decode('utf-8')
                data=json.loads(msg)
                if not data:
                    break
                if data['type']=='msg':
                    print(data['data'])
                elif data['type']=='location':
                    print(data)
                
            except:
                break
    
    #先发送给服务器，让服务器启动心跳机制，再定期发送心跳注册给服务器，该函数用于添加启动心跳机制功能到原心跳函数中
    def heartbeat_start(fuc):
        def wrapper(self,*args, **kwargs):
            #注册信息制作并发送
            metadata = {
                "type": "register_heartbeat", 
                "name":'chunkserver88',
                "chunks":self.chunk
                }
            data = json.dumps(metadata)
            data =data.encode('utf-8')
            self.master.sendall(len(data).to_bytes(8, "big"))
            self.master.sendall(data)

            a=fuc(self,*args, **kwargs)
            return a
        
        return wrapper
    
    #发送注册信息和心跳状态给服务器
    @heartbeat_start
    def heartbeat(self):
        
        while True:
            #心跳时间
            time.sleep(3)
            #将信息制作为json文件
            metadata = {
                "type": "register", 
                "name":'chunkserver88',
                "chunks":self.chunk
                }
            data = json.dumps(metadata)
            data =data.encode('utf-8')
            #先发大小，再发json encode的文件
            self.master.sendall(len(data).to_bytes(8, "big"))
            self.master.sendall(data)
            
        
        
        self.master.close()
        
if __name__ == "__main__":
    server = Server('chunkserver88')
    server.start()