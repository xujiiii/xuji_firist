class Master:
    def __init__(self):
        self.filename={}#{file1:[file1:[chunk1,chunk2.chunk3...]]}
        self.chunk_name={}# nv
        self.map={} #v
        #{chunk1:[chunksever1,chunkserver2,chunksever3...]}
        
        self.chunksever_space={}#v
    
    def start_up(self):
        pass    


    def heartbit(self):
        a=1


    def read_file(self,filename,outfit):
        try:
            print(1)
            #find file in filename

        except:
            print(f'error in finding {filename}')
            pass
            #not find file

    def receive_control_server(self,control):
        pass

    def action(fuc):
        def wrapper(self,*args, **kwargs):
            a=fuc(self,*args, **kwargs)

            return a
        return wrapper

    @action
    def receive_control_client(self,control):
        #control in ['w','c'] write and create
        return control
    

a=Master()

print(a.receive_control_client('w'))