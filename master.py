import socket
import threading
import pickle as pk
import re


# 获取主机名
hostname = socket.gethostname()

# 根据主机名解析 IP
ip_address = socket.gethostbyname(hostname)

class Master:
    def __init__(self,host=ip_address, port=12454):
        #{file1:[file1:[chunk1,chunk2.chunk3...]]} nv
        self.filename=set(['aa'])
        self.chunk_name={}
        #{chunk1:[chunksever1,chunkserver2,chunksever3...]} v
        self.map={'aa':['chunk1','chunk2','chunk3']} 
        self.chunksever_space=set(['chunk1','chunk2','chunk3'])
        

        #设置通讯地址参数,通讯协议，主机，端口
        self.master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host=host
        self.port=port
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
                #持续接收client信息并反应
                msg = conn.recv(1024).decode("utf-8")
                
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
                #4.聊天，并向所有clients广播聊天内容
                else:
                    self.broadcast(addr,msg)
                    print(f"[{addr}] {msg}")
    
            except ConnectionResetError:
                print(f"[异常] {addr} 异常断开")
                del self.clients[addr]
                conn.close()
                break

    def create_file(self,data):
        pass
        
        
    def check_file(self,conn):
        conn.send(self.filename.encode('utf-8'))
    
    
    def broadcast(self,addr,msg):
        for j in self.clients.keys():
            if j!=addr:
                self.clients[j].send(f'{addr}:{msg}'.encode('utf-8'))


    def heartbit(self):
        a=1


    def read_file(self,filename,outfit,conn):
        print(outfit)
        print(self.filename)
        #find file in filename
        if filename in self.filename:
            a=f'You can find {filename} in {str(self.map[filename])}'
            conn.send(a.encode('utf-8'))
        else:
            conn.send('No such file exist'.encode('utf-8'))
        
    def receive_control_server(self,control):
        pass

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