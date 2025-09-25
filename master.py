import socket
import threading
import json
import re
import time

#gain hostname
hostname = socket.gethostname()

#gain IP from hostnem 
ip_address = socket.gethostbyname(hostname)

class Master:
    def __init__(self,host=ip_address, port=12454):
        #{file1:[file1:[chunk1,chunk2.chunk3...]]} nv
        self.filename=set(['aa','bb'])
        self.chunk_name={'chunk1','chunk2','chunk3','chunk4','chunk5'}
        self.map={'aa':['chunk1','chunk2','chunk3'],'bb':['chunk4','chunk5']} 
        #{chunk1:[chunksever1,chunkserver2,chunksever3...]} v
        self.chunk_locations={
                            'chunk1':set(),
                            'chunk2':set(),
                            'chunk3':set(),
                            'chunk4':set(),
                            'chunk5':set()
                            } 
        
        self.chunkserver_space={
                               }
        
        self.heart_record={}
        
        #设置通讯地址参数,通讯协议，主机，端口
        self.master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host=host
        self.port=port
        #{addr:conn} used to record new users
        self.clients={}

    #start the master
    def start(self):
        #basic setting for master socket
        self.master_socket.bind((self.host, self.port))
        self.master_socket.listen(10)
        print(f"[启动] 服务器已启动，监听 {self.host}:{self.port}")
        #continues to listennning
        while True:
            #accept new clients
            conn, addr = self.master_socket.accept()
            #record clients
            self.clients[addr]=conn
            print(f"[新连接] {addr} 已连接")
            #handle each client in a new thread
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[活跃连接] {threading.active_count() - 1} 个客户端")

    def handle_client(self, conn, addr):
        while True:
            try:
                #接收长度
                length = conn.recv(8)
                leng=int.from_bytes(length)
                #接受json并转为dict
                data=conn.recv(leng).decode('utf-8')
                data=json.loads(data)
                if data['type']=='msg':
                    msg=data['data']
                    #1.handle exit
                    if not msg or msg.lower() == "exit":
                        print(f"[断开] {addr} 断开连接")
                        conn.close()
                        del self.clients[addr]
                        break
                    #2.处理create file操作
                    elif re.match(r'^cf-[A-Za-z0-9]+-.+$',msg) is not None:
                        print('cf control is started')
                        self.create_file(msg)
                    #3.处理read file操作
                    elif re.match(r'^rf-[A-Za-z0-9]+-[0-9]+-[0-9]+$',msg):
                        print(f'{addr} is trying to read file')
                        self.read_file(msg.split('-')[1],[msg.split('-')[2],msg.split('-')[3]],conn)
                    #4处理server的注册信息
                    elif re.match(r'register',msg):
                        pass
                    #5.聊天，并向所有clients广播聊天内容
                    else:
                        self.broadcast(addr,msg)
                        print(f"[{addr}] {msg}")
    
                elif data['type']=='register':
                    self.register(conn,addr,data)

                elif data['type']=='register_heartbeat':
                    #thread 一定要加，不然心跳注册的time sleep会让整个程序停止，导致错误，所以需要再弄一个thread单独执行心跳
                    thread = threading.Thread(target=self.register_heartbeat,
                                              args=(conn, addr,data))
                    thread.start()

            except ConnectionResetError:
                print(f"[异常] {addr} 异常断开")
                del self.clients[addr]
                conn.close()
                break

    #广播信息to clients
    def broadcast(self,addr,msg):
        for j in self.clients.keys():
            if j!=addr:
                self.send_message(self.clients[j],f'{addr}:{msg}')

    #basic function to send message to clients
    def send_message(self,conn,msg):
        #将信息制作为json文件
        metadata = {"type": "msg", "data": msg}
        data = json.dumps(metadata)
        data=data.encode('utf-8')
        #先发大小，再发json encode的文件
        conn.sendall(len(data).to_bytes())
        conn.sendall(data)
    
    #basic function to send locations and chunk index to clients to help them find chunkservers
    def response_read_file(self,conn,outfit,filename):
        self.send_server_location(conn)
        #将信息制作为json文件
        metadata = {"type": "file_information", 
                    "chunk_index":outfit,
                    "filename":filename,
                    "chunk_handle":self.map[filename],
                    "chunk_locations":[list(self.chunk_locations[j]) for j in self.map[filename]],
                    "action":"read"
                    }
        data = json.dumps(metadata)
        data=data.encode('utf-8')
        #先发大小，再发json encode的文件
        conn.sendall(len(data).to_bytes(8,'big'))
        conn.sendall(data)

    #To check if file exist before response_read_file
    def read_file(self,filename,outfit,conn):
        #find file in filename
        if filename in self.filename:
            self.response_read_file(conn,outfit,filename)
        else:
            self.send_message(conn,'No such file')

    def send_server_location(self,conn):
        #将信息制作为json文件
        metadata = self.chunkserver_space
        metadata['type']="servers_location"
        data = json.dumps(metadata)
        data=data.encode('utf-8')
        #先发大小，再发json encode的文件
        conn.sendall(len(data).to_bytes(8,'big'))
        conn.sendall(data)

    #Register the heartbeat mechanism and start a separate timing heartbeat mechanism service for each server  
    def register_heartbeat(self,conn,addr,data):
        for chunk in data['chunks']:
            self.chunk_locations[chunk].add(data["name"])
            self.chunkserver_space[data["name"]]=addr
            self.heart_record[data['name']]=time.time()
        while True:
            a=time.time()-self.heart_record[data["name"]]
            #print(a)
            if a>8:
                for chunk in data['chunks']:
                    self.chunk_locations[chunk].discard(data['name'])
                del self.chunkserver_space[data['name']]
                break
            time.sleep(10)

        print(f'{addr} server is losing and heartbeat break')

    #accept register information from chunkserver in start and each heartbeat from server
    def register(self,conn,addr,data):
        self.chunkserver_space[data["name"]]=addr[0]+":"+str(data['location'])
        for chunk in data['chunks']:
            self.chunk_locations[chunk].add(data["name"])
        self.heart_record[data['name']]=time.time()
        print(f"{addr} is registering")

    #Todo
    def log(fuc):
        def wrapper(self,*args, **kwargs):
            fuc(self,*args, **kwargs)

            return fuc(self,*args, **kwargs)
        
        return wrapper 

    #Todo
    def permition(fuc):
        def wrapper(self,*args, **kwargs):
            a=fuc(self,*args, **kwargs)

            return a
        
        return wrapper

if __name__ == "__main__":
    server = Master()
    server.start()

