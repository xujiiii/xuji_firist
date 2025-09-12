# xuji_firist
#This is project to modicate GFS by using 3 class object
to create Master,chunkserver and client

now just support sentence to create and add #running

client commend:

cf-filename-data #now data can just be string and number
  
client 发送信息类型(json)

1.msg,聊天用

2.control,用于向服务器和server传达请求

master 发送类型(json)

1.msg

2.location 文件的chunk handle和chunk handle对应位置和chunk index

server 发送的

1.register 注册，暨包含client的chunk handle，联系地址addr,通过addr联系server

2.data 暨clinet需要的数据
#server 123 is uncompleted ,now the main branch of servers is chunkserver8