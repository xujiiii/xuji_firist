class Server:
    def __init__(self,master):
        self.master=master
        
        self.chunk=[] #[[chunkname,chunkdata,version]]
    