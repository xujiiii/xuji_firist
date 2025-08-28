import threading
import socket
import pickle as pk

class Client:
    def __init__(self,host="192.168.1.42", port=12454):
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

    # 接收消息
    def receive_msg(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode("utf-8")
                if not data:
                    break
                print(data)
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

if __name__ == "__main__":
    client = Client()
    client.connect()