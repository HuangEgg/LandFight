#simple websockets brocaster
import asyncio
import websockets
clients = [] #to store all connected cleints
playerName = []
playerWebsocInfo = []
lockSign=0
owner=None
game = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

#handler for socket message activities
async def handler(websocket, path):
    global lockSign, owner, playerName, playerWebsocInfo,game   # 叫他用外面的全域變數
    #print(path) #path is not used currently
    userName='unknown'  # 預設的使用者名稱
    if websocket not in clients:
        clients.append(websocket) #append new cleint to the array
        print(websocket)

    async for message in websocket:   #收到訊息時
        print(message,'received from client') #print to console
        msg = message.split("###")
        if msg[0]=='Ready':
            userName=msg[1]
            playerName.append(userName)
            playerWebsocInfo.append(dict([("name", userName), ("websoc", websocket)]))
            strdata = ""
            strdata = strdata + playerName[0]
            print("set client name,", msg[1])
            for i in range(len(playerName)-1):
                strdata = strdata + "#" + playerName[1]
            await brocast(strdata+"###IN")
        elif msg[0]=='START':
            await brocast("Play###SS")
        elif msg[0]=="check":   # 在遊戲畫面告訴你是誰
            print("Gamepre")
            for i in range(len(playerWebsocInfo)):
                if playerWebsocInfo[i]["websoc"] == websocket:
                    await brocast(str(i+1)+"###WHO_RES")
        elif (msg[0] == playerName[0]) or (msg[0] == playerName[1]):
            if len(msg[1]) == 1:
                listPos1 = 0
                listPos2 = int(msg[1])
            else :
                listPos1 = int(msg[1][0:1])
                listPos2 = int(msg[1][1:2])
            print("1:",type(msg[0]),type(msg[1]))
            print(listPos1,"//",listPos2)
            print(game[listPos1][listPos2])
            # msg[1] = msg[1]  # 將要準備查找 game 的 索引值 變成 str 形態
            if msg[0] == playerName[0]:   # player1 預設是+1
                game[listPos1][listPos2] = game[listPos1][listPos2] + 1
            elif msg[0] == playerName[1]:   # player2 預設是-1
                game[listPos1][listPos2] = game[listPos1][listPos2] - 1
            print("pos:",msg[1],"landValue:",game[listPos1][listPos2])
            await brocast(str(listPos1)+str(listPos2)+"###"+str(game[listPos1][listPos2]))  # 廣播回去 （位置###值）

        else:
            await brocast(userName+"###"+message)
    
async def brocast(msg):
    print(msg,' brocasting') #print to console

    #iterate the clients
    for websock in clients:
        try:
            await websock.send(msg) #send message to each client
        except websockets.exceptions.ConnectionClosed:
            #remove the client when it disconnects
            print("Client disconnected.  Do cleanup")
            clients.remove(websock)
            #pass

#starts the service and run forever
loop = asyncio.new_event_loop() #get an event loop
asyncio.set_event_loop(loop) #set the event loop to asyncio

loop.run_until_complete(
    websockets.serve(handler, '', 4545) #setup the websocket service and handler
    ) #hook to localhost:4545
loop.run_forever() #keep it running
