import socket
import threading
import json
import re


# 获取主机名
hostname = socket.gethostname()

# 根据主机名解析 IP
ip_address = socket.gethostbyname(hostname)

class Master:
    def __init__(self,host=ip_address, port=12454):
        #{file1:[file1:[chunk1,chunk2.chunk3...]]} nv
        self.filename=set(['aa','bb'])
        self.chunk_name={'chunk1','chunk2','chunk3','chunk4','chunk5'}
        self.map={'aa':['chunk1','chunk2','chunk3'],'bb':['chunk4','chunk5']} 
        #{chunk1:[chunksever1,chunkserver2,chunksever3...]} v
        self.chunk_locations={
                            'chunk1':{'chunkserver2','chunkserver3'},
                            'chunk2':{'chunkserver1','chunkserver2'},
                            'chunk3':{'chunkserver1','chunkserver3'},
                            'chunk4':{'chunkserver1'},
                            'chunk5':{'chunkserver3'}
                            } 
        
        self.chunkserver_space={'chunkserver1':'11',
                               'chunkserver2':"22",
                               'chunkserver3':"33"
                               }
        
        #设置通讯地址参数,通讯协议，主机，端口
        self.master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host=host
        self.port=port
        #用于记录新用户,{addr:conn}
        self.clients={}

    #管理socket的启动和服务器与客户端的通讯
    def start(self):
        #绑定端口 主机，设置最高接受的用户
        self.master_socket.bind((self.host, self.port))
        self.master_socket.listen(5)
        print(f"[启动] 服务器已启动，监听 {self.host}:{self.port}")
        #持续监听用户的连接
        while True:
            #接受新client,没有时会堵塞
            conn, addr = self.master_socket.accept()
            #记录连接用户
            self.clients[addr]=conn
            print(f"[新连接] {addr} 已连接")
            #thread将接收的参数投入handle_client参数，成为新线程
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
                    self.heartbeat(conn,addr,data)

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
        #将信息制作为json文件
        metadata = {"type": "location", 
                    "chunk_index":outfit,
                    "filename":filename,
                    "chunk_handle":self.map[filename],
                    "chunk_locations":[list(self.chunk_locations[j]) for j in self.map[filename]],
                    "action":"read"}
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
        
    #heartbeat
    def heartbeat(self,conn,addr,data):
        for chunk in data['chunks']:
            self.chunk_locations[chunk].add(data["name"])
            self.chunkserver_space[data["name"]]=addr

    def log(fuc):
        def wrapper(self,*args, **kwargs):
            fuc(self,*args, **kwargs)

            return fuc(self,*args, **kwargs)
        
        return wrapper #包装后的函数

    def permition(fuc):
        def wrapper(self,*args, **kwargs):
            a=fuc(self,*args, **kwargs)

            return a
        
        return wrapper #包装后的函数

    @permition
    def receive_client(self,filename,outfit):
        #filename 和想看file的范围，即outfit(4,9)file的第4和9字节

        if filename in self.filename:
            pass
        else:
            print('error')
    
    def create(self,filename,data):
        if filename in self.filename:
            print('file exsists')
            return
        
        

if __name__ == "__main__":
    server = Master()
    server.start()

