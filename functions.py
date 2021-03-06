from ratelimit import limits,sleep_and_retry
import requests
import os
from dotenv import load_dotenv
import mysql.connector
import time

load_dotenv()

@sleep_and_retry
@limits(calls=45, period=30)
def api_call(mode, url, data=None, pin=None):
    #Mode 1 is for get requests
    if(mode == 1):
        headers = {"User-Agent": os.getenv("agent")}
        r = requests.get(url, headers=headers, allow_redirects=True)
    #Mode 2 is for post requests
    elif(mode == 2):
        headers = {"User-Agent": os.getenv("agent"), "X-Password": os.getenv("pass"), "X-Pin": pin}
        r = requests.post(url, headers=headers, data=data)
    elif(mode == 3):
        headers = {"User-Agent": os.getenv("agent"), "X-Password": os.getenv("pass")}
        r = requests.get(url, headers=headers)

    f = open("req.txt", "a")
    f.write(f"{int(time.time())}: {url}\n")
    f.close()

    if r.status_code != 200:
        print(r)
        print(r.headers)
        raise Exception(f'API Response: {r.status_code}')
    return r

def get_prefix(bot, msg):
    if msg.guild is None:
        return '!'
    else:
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f'SELECT prefix FROM guild WHERE serverid = "{msg.guild.id}" LIMIT 1')
        data = mycursor.fetchone()
        return str(data[0])

def get_cogs(id):
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT cogs FROM guild WHERE serverid = "{id}" LIMIT 1')
    data = mycursor.fetchone()
    return data[0]
    
def connector():
    mydb = mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )
    return mydb

def logerror(ctx, error):
    f = open("error.txt", "a")
    f.write(f"{int(time.time())}: {type(error)} occured from command invocation {ctx.message.content}\n")
    f.close()

def get_log(id):
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT logchannel FROM guild WHERE serverid = "{id}" LIMIT 1')
    data = mycursor.fetchone()
    return int(data[0])

async def log(bot, id, action):
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT logchannel FROM guild WHERE serverid = "{id}" LIMIT 1')
    data = int(mycursor.fetchone()[0])

    if not data:
        return

    channel = bot.get_channel(data)

    await channel.send(f"<t:{int(time.time())}:f>: {action}")

async def welcome(bot, member):
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT welcomechannel FROM guild WHERE serverid = '{member.guild.id}'")
    returned = mycursor.fetchone()
    if returned == None:
        return
    else: 
        welcome = bot.get_channel(int(returned[0]))

    mycursor.execute(f"SELECT welcome FROM guild WHERE serverid = '{member.guild.id}'")
    returned = mycursor.fetchone()
    if returned == None:
        return
    else: 
        text = returned[0].replace('<user>', member.mention)

    await welcome.send(text)
