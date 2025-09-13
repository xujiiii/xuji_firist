import threading
import socket
import json

# 获取主机名.
hostname = socket.gethostname()

# 根据主机名解析 IP
ip_address = socket.gethostbyname(hostname)

class Client:
    def __init__(self,host=ip_address, port=12454):
        self.chunk=[] #[[chunkname,chunkdata,version]]
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servers_location={}

    # 连接服务器
    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print(f"[连接] 已连接到服务器 {self.host}:{self.port}")
        # 开启线程接收消息
        thread = threading.Thread(target=self.receive_msg)
        thread.daemon = True
        thread.start()
        # 开始发送消息
        self.send_msg()

    # 接收消息,线程一直运行中
    def receive_msg(self):
        while True:
            try:
                #接收长度
                length = self.client_socket.recv(8)
                leng=int.from_bytes(length)
                #接受json并转为dict
                msg=self.client_socket.recv(leng).decode('utf-8')
                data=json.loads(msg)
                #根据json类型分类操作  
                if not data:
                    break
                if data['type']=='msg':
                    print(data['data'])
                #receive file informations from master and do action indicated by the data
                elif data['type']=='file_information':
                    self.action(data)
                #model the process of store communication address in cache
                elif data["type"]=='servers_location':
                    self.servers_location=data
                    print(f"servers location is {self.servers_location}")
                elif data["type"]=="information_from_servers":
                    pass

            except:
                break
    
    #Do the corresponding action indicates by data,like after receive from master, thn connect,
    #this is processing, uncompleted
    def action(self,data):
        print("action starts based on data")
        print(data)
        print(self.servers_location)
        for i in data['chunk_locations']:
            for j in i:
                tem_conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tem_conn.connect((self.servers_location[j].split(":")[0],
                                  int(self.servers_location[j].split(":")[1])))
                metadata = {"type": "clients", "data": "hii"}
                data = json.dumps(metadata)
                data =data.encode('utf-8')
                #先发大小，再发json encode的文件
                tem_conn.sendall(len(data).to_bytes(8, "big"))
                tem_conn.sendall(data)
                length = tem_conn.recv(8)
                leng=int.from_bytes(length)
                #接受json并转为dict
                msg=tem_conn.recv(leng).decode('utf-8')
                data=json.loads(msg)
                print(data)
                tem_conn.close()
        
    #发送消息to master
    def send_msg(self):
        while True:
            #得到发送的信息
            msg=input()
            #将信息制作为json文件
            if 1==1:
                metadata = {"type": "msg", "data": msg}
                data = json.dumps(metadata)
                data =data.encode('utf-8')
                #先发大小，再发json encode的文件
                self.client_socket.sendall(len(data).to_bytes(8, "big"))
                self.client_socket.sendall(data)
                #退出服务器指令
                if msg.lower()=='exit':
                    break
        
        self.client_socket.close()
        
if __name__ == "__main__":
    client = Client()
    client.connect()