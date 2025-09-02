import threading
import socket
import json

# 获取主机名
hostname = socket.gethostname()

# 根据主机名解析 IP
ip_address = socket.gethostbyname(hostname)

class Client:
    def __init__(self,host=ip_address, port=12454):
        self.chunk=[] #[[chunkname,chunkdata,version]]

        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
                length = self.client_socket.recv(8)
                leng=int.from_bytes(length)
                msg=self.client_socket.recv(leng).decode('utf-8')
                data=json.loads(msg)
                if not data:
                    break
                if data['type']=='msg':
                    print(data['data'])
                elif data['type']=='location':
                    print(data['chunk_locations'])
            except:
                break

    # 发送消息
    def send_msg(self):
        while True:
            msg = input()
            self.client_socket.send(msg.encode("utf-8"))
            if msg.lower() == "exit":
                break
        self.client_socket.close()
    #发送信息
    def send_message(self):
        while True:
            #得到发送的信息
            msg=input()
            #将信息制作为json文件
            metadata = {"type": "msg", "data": msg.encode('utf-8')}
            data = json.dumps(metadata).encode("utf-8")
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