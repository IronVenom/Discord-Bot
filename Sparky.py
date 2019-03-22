import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from datetime import datetime
import math
import imdb
import os
import random
import requests
import wikipedia as wk
import safygiphy
from newsapi import NewsApiClient
from googletrans import Translator
from googletrans import LANGUAGES
from gsearch.googlesearch import search
import ast
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import operator
import json
import urbandictionary as ud

newsapi = NewsApiClient(api_key=os.getenv('API_KEY'))
ia=imdb.IMDb()
Client = discord.Client()
client = commands.Bot(command_prefix="!")
translator = Translator()

@client.event
async def on_ready():
	await client.change_presence(game=discord.Game(name='with Iron Man.'))
	print("Badum tss, I am ready!")
  
#Commands.
@client.event
async def on_message(message):
	
	# Experience System

	with open('users.json','r') as f:
		users = json.load(f)

	await update_data(users,message.author)
	await add_experience(users, message.author, 5)
	await level_up(users, message.author, message.channel)

	with open('users.json','w') as f:
		json.dump(users, f)
	
	#Add Topic Based Roles

	if message.content.upper().startswith('TOPICROLE!'):
		topic_role_channel = client.get_channel(os.getenv('TOPIC_ROLE_CHANNEL_ID'))
		if message.channel.id == topic_role_channel.id:
			arg = ' '.join(message.content.split(' ')[1:])
			server=client.get_server(os.getenv('SERVER_ID'))
			role_member = None
			if arg.upper() == 'MACHINE LEARNING' or arg.upper() == 'ARTIFICIAL INTELLIGENCE' or arg.upper() == 'INTERNET OF THINGS' or arg.upper() == 'CYBER SECURITY':
				for role in server.roles:
					if role.name.upper() == arg.upper():
						await client.add_roles(message.author,role)
						role_member = role
						break
				await client.delete_message(message)
				embed = discord.Embed(title=message.author.name,description='You have been alloted the {} role!'.format(role_member.mention),colour=role_member.colour)
				await client.send_message(message.channel,embed=embed)
			else:
				embed = discord.Embed(title='WARNING',description='You are not allowed to add this role.',colour=discord.Colour.red())
				await client.send_message(message.channel,embed=embed)
		else:
			embed = discord.Embed(title='Warning',description='You can use this command only in {}'.format(topic_role_channel.mention),colour=discord.Colour.red())
			await client.send_message(message.channel,embed=embed)


	#Remove Topic Based Roles	

	if message.content.upper().startswith('TOPICROLEREMOVE!'):
		topic_role_channel = client.get_channel(os.getenv('TOPIC_ROLE_CHANNEL_ID'))
		if message.channel.id == topic_role_channel.id:
			arg = ' '.join(message.content.split(' ')[1:])
			server=client.get_server(os.getenv('SERVER_ID'))
			role_member = None
			if arg.upper() == 'MACHINE LEARNING' or arg.upper() == 'ARTIFICIAL INTELLIGENCE' or arg.upper() == 'INTERNET OF THINGS' or arg.upper() == 'CYBER SECURITY':
				for role in server.roles:
					if role.name.upper() == arg.upper():
						await client.remove_roles(message.author,role)
						role_member = role
						break
				await client.delete_message(message)
				embed = discord.Embed(title=message.author.name,description='You have removed the {} role!'.format(role_member.mention),colour=role_member.colour)
				await client.send_message(message.channel,embed=embed)
			else:
				embed = discord.Embed(title='WARNING',description='You are not allowed to remove this role.',colour=discord.Colour.red())
				await client.send_message(message.channel,embed=embed)
		else:
			embed = discord.Embed(title='Warning',description='You can use this command only in {}'.format(topic_role_channel.mention),colour=discord.Colour.red())
			await client.send_message(message.channel,embed=embed)

	#TOPIC Based Roles Help

	if message.content.upper().startswith('TPHELP!'):
		embed = discord.Embed(title='Topic Based Roles Help',description='Machine Learning/ Artificial Intelligence/ Internet of Things/ Cyber Security',colour=discord.Colour.purple())
		embed.add_field(name='TOPICROLE! name of role from above 4',value='Adds the role',inline=False)
		embed.add_field(name='TOPICROLEREMOVE! removes role from above 4',value='Removes the role',inline=False)
		await client.send_message(message.channel,embed=embed)

		
	# Urban Dictionary
	
	if message.content.upper().startswith('URBAN!'):
		args = ' '.join(message.content.split(' ')[1:])
		defs = ud.define(args)
		embed = discord.Embed(title = 'Urban Dictionary',description='Hit or Miss',color = discord.Color.dark_orange())
		for d in defs[0:3]:
			embed.add_field(name = '-->', value = d.definition, inline = False)
		await client.send_message(message.channel,embed = embed)

	# Suggest
		
	if message.content.upper().startswith('SUGGEST!'):
		args = ' '.join(message.content.split(' ')[1:])
		name = message.author.name
		timemsg = message.timestamp
		embed = discord.Embed(title='Iron Man\'s Dropbox',description='Suggestion created by {}'.format(message.author.mention),color = discord.Color.dark_blue())
		embed.add_field(name='Time of creation:',value='{}-{}-{}'.format(timemsg.day,timemsg.month,timemsg.year),inline= False)
		embed.add_field(name='Suggestion',value=args,inline= False)
		suggestion_channel = client.get_channel(os.getenv('SUGGEST_CHANNEL_ID'))
		await client.send_message(suggestion_channel,embed = embed)
		embed =  discord.Embed(title = "Suggestion",description = "Your suggestion has been recorded, please check {} for follow up.".format(suggestion_channel.mention),color = discord.Color.blue())
		await client.send_message(message.channel,embed = embed)
		await client.delete_message(message)
		
		
	# Leaderboard command

	if message.content.upper().startswith('LEADERBOARD!'):
		server=client.get_server(os.getenv('SERVER_ID'))
		mems = server.members
		lis = []
		for j in mems:
			if j.id in users and j.id != os.getenv('BOT'):
				lis.append([j,j.id])
		for i in lis:
			i.append(users[i[1]]['experience'])
		lead = [[i[0],i[2]] for i in lis]
		lead.sort(key=operator.itemgetter(1),reverse = True)
		embed = discord.Embed(title = 'Leaderboard',description='Monthly Experience System',color = discord.Color.dark_blue())
		if len(lead)>5:
			msg = '\n'
			for j,i in enumerate(lead[:5],1):
				msg = msg + '{}.)  {}  :  {}'.format(j,i[0].mention,i[1]) + '\n'
			embed.add_field(name = 'TOP 5 Members', value =msg,inline = False)
		else:
			msg = '\n'
			for j,i in enumerate(lead,1):
				msg = msg + '{}.)  {}  :  {}'.format(j,i[0].mention,i[1]) + '\n'
			embed.add_field(name = 'TOP {} Members'.format(len(lead)), value =msg,inline = False)
		await client.send_message(message.channel,embed = embed)


	# Google Search

	if message.content.upper().startswith('GOOGLE!'):
		args = ' '.join(message.content.split(' ')[1:])
		query = search(args)
		embed = discord.Embed(title='Google Search', description='Results for the query',colour=discord.Color.orange())
		for item in query[:5]:
			embed.add_field(name='-->',value=item,inline=False)
		await client.send_message(message.channel,embed=embed)
	
	#Greetings and Cookies and Random Stuff
	
	if message.content.upper().startswith('HELLO!'):
		userID = message.author.id
		await client.send_message(message.channel,"Hello <@%s>!" % (userID))
	if message.content.upper().startswith('YO!'):
		userID = message.author.id 
		await client.send_message(message.channel,"Yo to you too, <@%s>!" % (userID))
	if message.content.upper().startswith('WAZZ POPPIN!'):
		userID = message.author.id 
		await client.send_message(message.channel,"Not much, <@%s>!" % (userID))
	if message.content.upper().startswith('COOKIE!'):
		cookies=['choco chip','vanilla','caramel','butterscotch','almond','chunky coconut','marmalade','choco lava','butter']
		index_cookie=random.randint(0,len(cookies)-1)
		cookie_send=cookies[index_cookie]
		cookie_message='{} , {} gave you a nice {} cookie :cookie: !'.format(message.content.split(' ')[1],message.author.mention,cookie_send)
		await client.send_message(message.channel, cookie_message)
		
	#Movies,TV Series and Video Games plot summaries
	
	if message.content.upper().startswith('MOVIE!'):
		userID = message.author.id 
		args = message.content.split(" ")
		moviename=" ".join(args[1:])
		movie=ia.search_movie(moviename)
		movie1=movie[0]
		movieid=ia.get_imdbID(movie1)
		movieinfo=ia.get_movie(movieid)
		plot=movieinfo['plot'][0]
		embed=discord.Embed(title='PLOT SUMMARY',description='',colour=discord.Colour.teal())
		embed.add_field(name=moviename,value=plot,inline=False)
		await client.send_message(message.channel,embed=embed)
		
	#Wikipedia Search
	
	if message.content.upper().startswith('WIKI!'):
		args = message.content.split(" ")
		item_search_title=" ".join(args[1:])
		item_summary=wk.summary(item_search_title,sentences=4)
		embed=discord.Embed(title='Wikipedia Summary',description='',colour=discord.Colour.teal())
		embed.add_field(name=item_search_title.capitalize(),value=item_summary,inline=False)
		await client.send_message(message.channel,embed=embed)
	
	#Server Info
	
	# 1.) Roles information
	
	if message.content.upper().startswith('ROLES!'):
		server=client.get_server(os.getenv('SERVER_ID'))
		roles_list=server.role_hierarchy
		for role in roles_list:
			if not role.is_everyone:
				embed=discord.Embed(title=role.name,description='',colour=role.colour)
				await client.send_message(message.channel,embed=embed)
				
	# 2.) Server information
	
	if message.content.upper().startswith('INFO!'):
		server=client.get_server(os.getenv('SERVER_ID'))
		people_count=server.member_count
		time_of_creation=server.created_at
		owner_name=server.owner.name
		icon=server.icon_url
		embed=discord.Embed(title=server.name,description='SERVER INFO',colour=discord.Colour.teal())
		embed.set_thumbnail(url=icon)
		embed.add_field(name='Member count:',value='Humans : {}\nBots : 1'.format(people_count-1),inline=False)
		embed.add_field(name='Time of Origin:',value='{}-{}-{}'.format(time_of_creation.day, time_of_creation.month, time_of_creation.year),inline=False)
		embed.add_field(name='Owner:',value=owner_name,inline=False)
		await client.send_message(message.channel,embed=embed)
	
	# Server Data Analysis
	
	# Bar Plot depicting statuses of people 
	
	if message.content.upper().startswith("STATUS!"):
		server=client.get_server(os.getenv('SERVER_ID'))
		mem_list = server.members
		online = 0
		offline = 0
		idle = 0
		do_not_disturb = 0
		invisible = 0
		for mem in mem_list:
			if str(mem.status) == "online":
				online += 1
			elif str(mem.status) == "offline":
				offline += 1
			elif str(mem.status) == "idle":
				idle += 1
			elif str(mem.status) == "dnd":
				do_not_disturb += 1
			else:
				invisible += 1 
		stats = ('Online', 'Offline', 'Idle', 'Do Not Disturb')
		y_pos = np.arange(len(stats))
		status_mems = [online,offline,idle,do_not_disturb]
		plt.bar(y_pos, status_mems, align='center', alpha=0.5, color = ['green','grey','yellow','red'])
		plt.xticks(y_pos, stats)
		plt.yticks(np.arange(0,max(status_mems)+1, step=1))
		plt.ylabel('Members')
		plt.title('Status Statistics')
		plt.savefig('stats.png')
		await client.send_file(message.channel,'stats.png')
		plt.clf()
	
	# Message Database Analysis 
	
	if message.content.upper().startswith("MESSAGES!"):
		server=client.get_server(os.getenv('SERVER_ID'))
		mem_list = server.members
		freq ={}
		for mem in mem_list:
			freq[mem.name] = 0
		async for message in client.logs_from(message.channel,limit = 10000000000000000000000000000000000000000000000000000000000000000000000000000000, before = datetime.now()):
			try:
				freq[message.author.name] += 1
			except KeyError:
				continue
		if len(sorted(freq.items(), key=operator.itemgetter(1),reverse = True)) > 5:
			freq = dict(sorted(freq.items(), key=operator.itemgetter(1),reverse = True)[:5])
		else:
			freq = dict(sorted(freq.items(), key=operator.itemgetter(1),reverse = True))
		count = 0
		for i,j in freq.items():
			if j != 0: 
				count += 1
		if count > 5:
			embed = discord.Embed(title="Message Database",description="Top 5 Active Members for {}".format(message.channel.mention),color = discord.Color.blue())
		else:
			embed = discord.Embed(title="Message Database",description="Top {} Active Members for {}".format(count,message.channel.mention),color = discord.Color.blue())
		for i,j in freq.items():
			if j != 0: 
				embed.add_field(name = i , value = j,inline = False)
		await client.send_message(message.channel,embed = embed)
		members = []
		messages = []
		for i,j in freq.items():
			if j != 0:
				messages.append(j)
				members.append(i)
		members = tuple (members)
		membs = np.arange(len(members))
		colors = ['green','blue','orange','yellow','purple']
		if len(sorted(freq.items(), key=operator.itemgetter(1),reverse = True)) > 5:
			plt.bar(membs,messages, align='center', alpha=0.5, color = colors)
		else:
			plt.bar(membs,messages, align='center', alpha=0.5, color =colors [:len(members)])
		plt.xticks(membs,members)
		plt.yticks(np.arange(0,max(messages)+1,step = (max(messages)//2)))
		plt.ylabel('Frequency of Messages')
		plt.title('TOP {} Members'.format(len(members)))
		plt.savefig('msg_Stats.png')
		await client.send_file(message.channel,'msg_Stats.png')
		plt.clf()
	
	#Moderation Commands

	# 1.) Kick a user
	if message.content.upper().startswith("KICK!"):
		server=client.get_server(os.getenv('SERVER_ID'))
		flag=False
		if message.author.server_permissions.kick_members == True and message.author.server_permissions.ban_members ==  True:
			flag=True
		if flag == True:
			for mem_ber in server.members:
				if mem_ber.mentioned_in(message) ==  True:
					await client.kick(mem_ber)
					embed=discord.Embed(title='Kicked',description="{} has been kicked from the server".format(mem_ber.mention),colour=discord.Colour.red())
					await client.send_message(message.channel,embed=embed)
					break

		else:
			embed=discord.Embed(title='Warning',description='{} You are not allowed to use this command!'.format(message.author.mention),colour=discord.Colour.red())
			await client.send_message(message.channel,embed=embed)
	# 2.) Ban a user
	if message.content.upper().startswith("BAN!"):
		server=client.get_server(os.getenv('SERVER_ID'))
		flag=False
		if message.author.server_permissions.kick_members == True and message.author.server_permissions.ban_members ==  True:
			flag=True
		if flag == True:
			for mem_ber in server.members:
				if mem_ber.mentioned_in(message) ==  True:
					await client.ban(mem_ber,0)
					embed=discord.Embed(title='Banned',description="{} has been banned from the server".format(mem_ber.mention),colour=discord.Colour.red())
					await client.send_message(message.channel,embed=embed)
					break

		else:
			embed=discord.Embed(title='Warning',description='{} You are not allowed to use this command!'.format(message.author.mention),colour=discord.Colour.red())
			await client.send_message(message.channel,embed=embed)


	#Bot Commands Help
	
	if message.content.upper().startswith('HELP!'):
		embed=discord.Embed(title='SPARKY TO YOUR RESCUE!',description='COMMANDS [Note that the commands are case insensitive.] -->',colour=discord.Colour.teal())
		embed.add_field(name='help!',value='Gives this list',inline=False)
		embed.add_field(name='psrules!',value='Rules of Practice Sessions',inline=False)
		embed.add_field(name='modhelp!',value='Moderation Commands',inline=False)
		embed.add_field(name='translatehelp!',value='Translation Commands',inline=False)
		embed.add_field(name='lrhelp!',value='Language Based Roles Commands',inline=False)
		embed.add_field(name='tphelp!',value='Topic Based Roles Commands',inline=False)
		embed.add_field(name='calchelp!',value='Calculator Commands',inline=False)
		embed.add_field(name='servhelp!',value='Server Commands',inline=False)
		embed.add_field(name='funhelp!',value='Fun Commands',inline=False)
		embed.add_field(name='utilhelp!',value='General Utility Commands help',inline=False)
		embed.add_field(name='datahelp!',value='Data Analysis Commands help',inline=False)
		await client.send_message(message.channel,embed=embed)
		
	# Data Analysis Commands
	
	if message.content.upper().startswith('DATAHELP!'):
		embed=discord.Embed(title='Data Analysis Commands',description='COMMANDS [Note that the commands are case insensitive.] -->',colour=discord.Colour.blue())
		embed.add_field(name='status!',value='Gives a bar plot depicting the statuses of people on the server.',inline=False)
		embed.add_field(name='messages!',value='Gives the database and bar plot for Top 5 Active members for the channel in which the command was typed',inline=False)
		await client.send_message(message.channel,embed = embed)
	
	# General Utility Commands 

	if message.content.upper().startswith('UTILHELP!'):
		embed = discord.Embed(title='General Utility Help', description='General Commands that dont belong in any other categories',colour=discord.Color.dark_grey())
		embed.add_field(name='stackov! Query',value='Search for solutions to programming doubts.',inline=False)
		embed.add_field(name='embed! text to be embedded',value = 'Embeds text.',inline = False)
		embed.add_field(name='google! Query',value = 'Search google',inline = False)
		await client.send_message(message.channel,embed=embed)
	
	#Server Related Commands

	if message.content.upper().startswith('SERVHELP!'):
		embed=discord.Embed(title='Server Commands',description='COMMANDS [Note that the commands are case insensitive.] -->',colour=discord.Colour.gold())
		embed.add_field(name='roles!',value='Gives all the roles present in the server.',inline=False)
		embed.add_field(name='info!',value='Gives server info.',inline=False)
		embed.add_field(name='profile!',value='Check out your profile card.',inline=False)
		embed.add_field(name='profile mention member!',value='Check out profile card of any member.',inline=False)
		embed.add_field(name='ping!',value='Ping Sparky.',inline=False)
		embed.add_field(name='suggest! suggestion',value='Create a suggestion for the server',inline=False)
		embed.add_field(name='leaderboard!',value='Check the leaderboard.',inline=False)
		await client.send_message(message.channel,embed=embed)
	
	#Fun Commands

	if message.content.upper().startswith('FUNHELP!'):
		embed=discord.Embed(title='Fun Commands',description='COMMANDS [Note that the commands are case insensitive.] -->',colour=discord.Colour.magenta())
		embed.add_field(name='wiki!',value='Gives brief summary from Wikipedia of the queried item',inline=False)
		embed.add_field(name='coin! type heads or tails',value='Make Sparky toss a coin and see if you win',inline=False)
		embed.add_field(name='slot!',value='Test your luck on Sparky\'s slot machine!',inline=False)
		embed.add_field(name='joke!',value='Cheeky and nerdy Chuck Norris jokes',inline=False)
		embed.add_field(name='movie! name of Movie / TV Series /  Video Game',value='Gives the plot summary of the Movie/ TV series / Video Game',inline=False)
		embed.add_field(name='hello! / yo! / wazz poppin!',value='Sparky says hi to you', inline=False)
		embed.add_field(name='cookie! mention user',value='Give someone a delicious cookie', inline=False)
		embed.add_field(name='sparkygif! gif topic',value='Posts a GIF on the mentioned topic', inline=False)
		embed.add_field(name='poll! item1-without-spaces item2-without-spaces',value='Creates a 2 item poll', inline=False)
		embed.add_field(name='trivia!',value='Answer Sparky\'s CS trivia questions!', inline=False)
		embed.add_field(name='fight! mention user you want to fight',value='Get into Sparky\'s Arena and fight!', inline=False)
		embed.add_field(name='urban! word to be searched',value='Check out the urban dictionary for the meaning of a word.', inline=False)
		await client.send_message(message.channel,embed=embed)
		
	#MOD Commands Help

	if message.content.upper().startswith('MODHELP!'):
		if message.author.server_permissions.kick_members == True and message.author.server_permissions.ban_members ==  True:
			embed=discord.Embed(title='MOD COMMANDS',description='Can be used only by Admins.',colour=discord.Colour.red())
			embed.add_field(name='purge! number of messages',value='Purges through a given number of messages.', inline=False)
			embed.add_field(name='kick! user',value='Kicks the mentioned user from the server.', inline=False)
			embed.add_field(name='ban! user',value='Bans the mentioned user from the server.', inline=False)
			embed.add_field(name='technews!',value='Release tech news.', inline=False)
			await client.send_message(message.channel,embed=embed)
		else:
			embed=discord.Embed(title='Warning',description='{} You are not allowed to use this command!'.format(message.author.mention),colour=discord.Colour.red())
			await client.send_message(message.channel,embed=embed)
			
	#Practice Session Rules

	if message.content.upper().startswith('PSRULES!'):
		channel_CP = client.get_channel(os.getenv('CP_CHANNEL_ID'))
		role_id_list=[]
		for role in message.server.roles:
			if role.name.upper() == 'PROGRAMMERS':
				role_id_list.append(role.mention)
			if role.name.upper() == 'CODERS':
				role_id_list.append(role.mention)
		embed = discord.Embed(title='Practice Session Rules',description='To be followed by everyone who is participating',colour=discord.Colour.red())
		embed.add_field(name='Rule-1',value='Post your solutions in {} using appropriate discord markdown.'.format(channel_CP),inline='False')
		embed.add_field(name='Rule-2',value='If you have a doubt, ping anyone of the support staff mentioned below. Don\'t ping the entire role',inline='False')
		embed.add_field(name='Rule-3',value='Try to make your code as efficient as possible. If you don\'t know about efficiency, leave this point.',inline='False')
		embed.add_field(name='Rule-4',value='Do not cheat or copy.',inline='False')
		embed.add_field(name='Rule-5',value='Use logic along with the in-built functions to get the most output.',inline='False')
		embed.add_field(name='Rule-6',value='Use C++ / C /Python / Java. If you feel excited, use Haskell or Erlang at your own risk.',inline='False')
		embed.add_field(name='Link for Discord Markup',value='https://support.discordapp.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-',inline='False')
		embed.add_field(name='Support Staff',value=role_id_list[0]+'\n'+role_id_list[1],inline='False')
		await client.send_message(message.channel,embed=embed)
	#PING
		
	if message.content.upper().startswith('PING!'):
		start = time.time() * 1000
		msg = await client.send_message(message.channel,'PONG! :ping_pong:')
		end = time.time() * 1000
		await client.edit_message(message = msg, new_content = ':ping_pong: `{} ms`'.format('{0:.3f}'.format(end - start)))
			
	#Coin Flip Game
	if message.content.upper().startswith('COIN!'):
		args=message.content.split(" ")
		result_list=["Heads","Tails"]
		choice=random.randint(0,1)
		if args[1].upper()==result_list[choice].upper():
			result="{} it is! You win!".format(result_list[choice])
			embed=discord.Embed(title='Coin Flip',description=result,colour=discord.Colour.teal())
			await client.send_message(message.channel,embed=embed)
		else:
			result=" Uh oh, its {}! Better luck next time!".format(result_list[choice])
			embed=discord.Embed(title='Coin Flip',description=result,colour=discord.Colour.teal())
			await client.send_message(message.channel,embed=embed)

	#Slot Machine Game
	if message.content.upper().startswith('SLOT!'):
		result_list=[':apple:',':pear:',':tangerine:']
		result_list2=[':grapes:',':strawberry:',':cherries:']
		result_list3=[':hotdog:',':icecream:',':taco:']
		choice1=random.randint(0,2)
		choice2=random.randint(0,2)
		choice3=random.randint(0,2)
		e11=result_list[choice1]
		e12=result_list[choice2]
		e13=result_list[choice3]
		e21=result_list2[choice1]
		e22=result_list2[choice2]
		e23=result_list2[choice3]
		e31=result_list3[choice1]
		e32=result_list3[choice2]
		e33=result_list3[choice3]
		result=e11+" | "+e12+" | "+e13+"\n"+e21+" | "+e22+" | "+e23+"\n"+e31+" | "+e32+" | "+e33
		row1=False
		row2=False
		row3=False
		row_count=0
		if (e11==e12) and (e12==e13) and (e13==e11):
			row1=True
			row_count+=1
		if (e21==e22) and (e22==e23) and (e23==e21):
			row2=True
			row_count+=1
		if (e31==e32) and (e32==e33) and (e33==e31):
			row3=True
			row_count+=1
		if row_count==0:
			res_mes="Better luck next time!"
		if row_count==1:
			res_mes="You got 1 row! Nice work!"
		if row_count==2:
			res_mes="You got 2 rows! Awesome!"
		if row_count==3:
			res_mes="Hattrick!"
		embed=discord.Embed(title='Slot Machine',description=result,colour=discord.Colour.teal())
		embed.add_field(name='Result',value=res_mes, inline=False)
		await client.send_message(message.channel,embed=embed)
	
	#Joke
	
	if message.content.upper().startswith('JOKE!'):
		l=requests.get('http://api.icndb.com/jokes/random?limitTo=[nerdy]')
		l.text.split(' ')
		joke = eval(l.text)['value']['joke']
		embed = discord.Embed(title='Joke',description=joke,colour=discord.Colour.blue())
		await client.send_message(message.channel,embed=embed)
	
	#Purge Deleting Messages

	if message.content.upper().startswith('PURGE!'):
		flag=False
		if message.author.server_permissions.kick_members == True and message.author.server_permissions.ban_members ==  True:
			flag=True
		if flag == True:
			args = int(message.content.split(' ')[1])
			print(args)
			await client.purge_from(message.channel,limit=args)
		else:
			embed = discord.Embed(title="Warning!",description='You are not allowed to use this command',colour=discord.Colour.red())
			await client.send_message(message.channel,embed=embed)
			
	#Language Based Roles Help

	if message.content.upper().startswith('LRHELP!'):
		embed = discord.Embed(title='Language Based Roles Help',description='C/C++/Java/Python',colour=discord.Colour.purple())
		embed.add_field(name='LANGROLE! name of role from above 4',value='Adds the role',inline=False)
		embed.add_field(name='LANGROLEREMOVE! removes role from above 4',value='Removes the role',inline=False)
		await client.send_message(message.channel,embed=embed)

	#Add Language Based Roles

	if message.content.upper().startswith('LANGROLE!'):
		lang_role_channel = client.get_channel(os.getenv('LANG_ROLE_ID'))
		if message.channel.id == lang_role_channel.id:
			arg = message.content.split(' ')[1]
			server=client.get_server(os.getenv('SERVER_ID'))
			role_member = None
			if arg.upper() == 'C++' or arg.upper() == 'PYTHON' or arg.upper() == 'C' or arg.upper() == 'JAVA':
				for role in server.roles:
					if role.name.upper() == arg.upper():
						await client.add_roles(message.author,role)
						role_member = role
						break
				await client.delete_message(message)
				embed = discord.Embed(title=message.author.name,description='You have been alloted the {} role!'.format(role_member.mention),colour=role_member.colour)
				await client.send_message(message.channel,embed=embed)
			else:
				embed = discord.Embed(title='WARNING',description='You are not allowed to add this role.',colour=discord.Colour.red())
				await client.send_message(message.channel,embed=embed)
		else:
			embed = discord.Embed(title='Warning',description='You can use this command only in {}'.format(lang_role_channel.mention),colour=discord.Colour.red())
			await client.send_message(message.channel,embed=embed)

	#Remove Language Based Roles	

	if message.content.upper().startswith('LANGROLEREMOVE!'):
		lang_role_channel = client.get_channel(os.getenv('LANG_ROLE_ID'))
		if message.channel.id == lang_role_channel.id:
			arg = message.content.split(' ')[1]
			server=client.get_server(os.getenv('SERVER_ID'))
			role_member = None
			if arg.upper() == 'C++' or arg.upper() == 'PYTHON' or arg.upper() == 'C' or arg.upper() == 'JAVA':
				for role in server.roles:
					if role.name.upper() == arg.upper():
						await client.remove_roles(message.author,role)
						role_member = role
						break
				await client.delete_message(message)
				embed = discord.Embed(title=message.author.name,description='You have removed the {} role!'.format(role_member.mention),colour=role_member.colour)
				await client.send_message(message.channel,embed=embed)
			else:
				embed = discord.Embed(title='WARNING',description='You are not allowed to remove this role.',colour=discord.Colour.red())
				await client.send_message(message.channel,embed=embed)
		else:
			embed = discord.Embed(title='Warning',description='You can use this command only in {}'.format(lang_role_channel.mention),colour=discord.Colour.red())
			await client.send_message(message.channel,embed=embed)
	
	#GIFs

	if message.content.upper().startswith('SPARKYGIF!'):
		g = safygiphy.Giphy()
		target = message.content.split(' ')[1]
		gif = g.random(tag=target)['data']['url']
		await client.send_message(message.channel,gif)
		
	#Profile

	if message.content.upper().startswith('PROFILE!'):
		if message.content.upper() == "PROFILE!":
			server=client.get_server(os.getenv('SERVER_ID'))
			name = message.author.name
			pfp = message.author.avatar_url
			joindate = message.author.joined_at
			roles = message.author.roles
			level = users[message.author.id]['level']
			experience = users[message.author.id]['experience']
			nextexp = (level+1)**4
			string = []
			for item in roles:
				if item.name!='@everyone':
					string.append(item.mention)
			if len(string) == 0:
				string = '-'
			string = list(reversed(string))
			string='  '.join(string)
			embed = discord.Embed(title='PROFILE',description=server.name,colour=discord.Colour.teal())
			embed.set_thumbnail(url=pfp)
			embed.add_field(name='Name:',value=name,inline=True)
			embed.add_field(name='Joined the server on:',value='{}-{}-{}'.format(joindate.day,joindate.month,joindate.year),inline=True)
			embed.add_field(name='Level:',value=level,inline=True)
			embed.add_field(name='Experience:',value='[**{}/{}**]'.format(experience,nextexp),inline=True)
			embed.add_field(name='Roles:',value=string,inline=False)
			await client.send_message(message.channel,embed=embed)
		else:
			server=client.get_server(os.getenv('SERVER_ID'))
			for mem in server.members:
				if mem.mentioned_in(message) ==  True:
					name = mem.name
					pfp = mem.avatar_url
					joindate = mem.joined_at
					roles = mem.roles
					level = users[mem.id]['level']
					experience = users[mem.id]['experience']
					nextexp = (level+1)**4
					string = []
					for item in roles:
						if item.name!='@everyone':
							string.append(item.mention)
					if len(string) == 0:
						string = '-'
					string = list(reversed(string))
					string='  '.join(string)
					embed = discord.Embed(title='PROFILE',description=server.name,colour=discord.Colour.teal())
					embed.set_thumbnail(url=pfp)
					embed.add_field(name='Name:',value=name,inline=True)
					embed.add_field(name='Joined the server on:',value='{}-{}-{}'.format(joindate.day,joindate.month,joindate.year),inline=True)
					embed.add_field(name='Level:',value=level,inline=True)
					embed.add_field(name='Experience:',value='[**{}/{}**]'.format(experience,nextexp),inline=True)
					embed.add_field(name='Roles:',value=string,inline=False)
					await client.send_message(message.channel,embed=embed)
					break
					
	#Translate Commands

	if message.content.upper().startswith('TRANSLATE!'):
		args = ' '.join(message.content.split(' ')[2::])
		lang = message.content.split(' ')[1]
		translations = translator.translate(args, dest=lang)
		embed = discord.Embed(title='SPARKY TRANSLATE',description='Sparky Translates for you!',colour=discord.Colour.teal())
		embed.add_field(name='Original Message:',value=args,inline='False')
		embed.add_field(name='Translated Message:',value=translations.text,inline='False')
		await client.send_message(message.channel,embed=embed)

	if message.content.upper().startswith('TRANSLATELANGS!'):
		msg = dict(map(reversed, LANGUAGES.items()))
		args = message.content.split(' ')[1]
		languages = list(msg.keys())
		if args.lower() in languages:
			embed=discord.Embed(title=args.lower(),description='The Code is: {}'.format(msg[args.lower()]),colour = discord.Colour.teal())
			await client.send_message(message.channel,embed=embed)
		else:
			embed=discord.Embed(title='Warning!',description='This language is not available',colour = discord.Colour.teal())
			await client.send_message(message.channel,embed=embed)

	if message.content.upper().startswith('TRANSLATEHELP!'):
		embed = discord.Embed(title='Sparky Translation Help',description='Commands',colour=discord.Colour.teal())
		embed.add_field(name='translatelangs! language',value='Gives the code of the language asked',inline='False')
		embed.add_field(name='translate! languagecode message to be translated',value='Translates the given message into the selected language.',inline='False')
		await client.send_message(message.channel,embed=embed)
	
	#Calculator

	if message.content.upper().startswith('CALC!'):
		args = message.content.split(' ')
		res = 0
		if args[1].upper() == 'SIN':
			res = math.sin(math.radians(float(args[2])))
		elif args[1].upper() == 'COS':
			res = math.cos(math.radians(float(args[2])))
		elif args[1].upper() == 'TAN':
			res = math.tan(math.radians(float(args[2])))
		elif args[1].upper() == 'EXP':
			res = math.exp(float(args[2]))
		elif args[1].upper() == 'POW':
			res = math.pow(float(args[2]),float(args[3]))
		elif args[1].upper() == 'SQRT':
			if float(args[2])>=0:
				res = math.sqrt(float(args[2]))
			else:
				res = "Mathematical Error!"
		elif args[1].upper() == 'LOG':
			if float(args[2]) > 0 and float(args[3])>0:
				res = math.log(float(args[2]),float(args[3]))
			else:
				res = "Mathematical Error!"
		elif args[1].upper() == 'EVAL':
			s = ''.join(args[2:])
			res = eval(s)
		else:
			res = 'Wrong Command!'
		embed = discord.Embed(title='Sparky\'s Calculator',description='Answer',colour=discord.Colour.orange())
		embed.add_field(name=' '.join(args[1:]),value=res,inline='False')
		await client.send_message(message.channel,embed=embed)

	if message.content.upper().startswith('CALCHELP!'):
		embed=discord.Embed(title='Sparky\'s Calculator',description='Quick Maths',colour=discord.Colour.orange())
		embed.add_field(name='calc! sin/cos/tan angle',value='Sine/Cosine/Tangent of the given angle',inline='False')
		embed.add_field(name='calc! exp number',value='Exp(number)',inline='False')
		embed.add_field(name='calc! log value base',value='Log of value to the given base',inline='False')
		embed.add_field(name='calc! sqrt number',value='Square root of number',inline='False')
		embed.add_field(name='calc! pow number exponent',value='Value of number raised to exponent',inline='False')
		embed.add_field(name='calc! eval expression_without_spaces',value='Value of the expression',inline='False')
		await client.send_message(message.channel,embed=embed)
	
	#Poll
	
	if message.content.upper().startswith('POLL!'):
		args = message.content.split(' ')[1:]
		item1 = args[0] 
		item2 = args[1]
		embed = discord.Embed(title = 'POLL', description='A poll has been created by {}!'.format(message.author.mention),colour=discord.Colour.blue())
		embed.add_field(name = ':one: {}'.format(item1.upper()), value= 'React with :one: to vote', inline = False)
		embed.add_field(name = ':two: {}'.format(item2.upper()), value= 'React with :two: to vote', inline = False)
		msg = await client.send_message(message.channel, embed=embed)
		await client.add_reaction(msg,'\U00000031\U000020e3')
		await client.add_reaction(msg,'\U00000032\U000020e3')
		
	# Stackoverflow Search

	if message.content.upper().startswith('STACKOV!'):
		args = ' '.join(message.content.split(' ')[1:])
		query = search('Stackoverflow ' + args)
		embed = discord.Embed(title='StackOverflow Search', description='Results for the query',colour=discord.Color.orange())
		for item in query[:5]:
			embed.add_field(name='-->',value=item,inline=False)
		await client.send_message(message.channel,embed=embed)
	
	# Embed Text

	if message.content.upper().startswith('EMBED!'):
		args = ' '.join(message.content.split(' ')[1:])
		embed = discord.Embed(title='Embedded by {}'.format(message.author.name),description=args,colour = discord.Color.dark_orange())
		await client.delete_message(message)
		await client.send_message(message.channel,embed=embed)
	
	#Trivia
	
	if message.content.upper().startswith("TRIVIA!"):
		req = requests.get("https://opentdb.com/api.php?amount=1&category=18&type=multiple")
		texts = ast.literal_eval(req.text)
		question = texts["results"][0]["question"]
		cor_ans = texts["results"][0]["correct_answer"]
		incorrect_answers = texts["results"][0]["incorrect_answers"]
		incorrect_answers.append(cor_ans)
		answers_lis = incorrect_answers
		random.shuffle(answers_lis)
		embed = discord.Embed(title="CS TRIVIA by Sparky",description="Type a number between 1 and 4 to choose your answer.",colour=discord.Color.dark_teal())
		embed.add_field(name='Question',value = question,inline = False)
		embed.add_field(name=':one:',value = answers_lis[0],inline = False)
		embed.add_field(name=':two:',value = answers_lis[1],inline = False)
		embed.add_field(name=':three:',value = answers_lis[2],inline = False)
		embed.add_field(name=':four:',value = answers_lis[3],inline = False)
		await client.send_message(message.channel,embed = embed)
		msg = await client.wait_for_message(author = message.author,channel = message.channel)
		options = ["1","2","3","4"]
		if msg.content in options:
			if answers_lis[int(msg.content)-1] == cor_ans:
				embed = discord.Embed(title="Correct Answer!",description="{} has answered the question correctly, the answer is Option-{} : {}!".format(message.author.name,msg.content,cor_ans),colour=discord.Color.green())
				await client.send_message(message.channel,embed = embed)
			else:
				embed = discord.Embed(title="Wrong Answer!",description="{} has answered the question wrong, the correct answer is Option-{} : {}!".format(message.author.name,answers_lis.index(cor_ans)+1,cor_ans),colour=discord.Color.red())
				await client.send_message(message.channel,embed = embed)
		else:
			embed = discord.Embed(title="Warning!",description="Type a number between 1 and 4 only (both inclusive)!",colour=discord.Color.red())
			await client.send_message(message.channel,embed=embed)
			
	# Fight
	
	if message.content.upper().startswith("FIGHT!"):
		turns = random.randint(3,14)
		fights = ["used the infinity gauntlet against","used the one ring against","used their shoes against","gave a bomb to","used their mental energy to kill","went super saiyan mode and blasted",
		"ate ice cream and threw the empty cone at","used the elder wand and cursed","used a dead meme against","said meep and ran away from"]
		person_1 = message.author.mention
		person_2 = message.content.split(' ')[1]
		embed = discord.Embed(title='SPARKY\'S ARENA',description="Let the fight begin!",color=discord.Color.blue())
		for i in range(1,turns):
			if i%2 == 0:
				embed.add_field(name='Round {}'.format(i),value="{} {} {}".format(person_2,random.choice(fights),person_1),inline = False)
			else:
				embed.add_field(name='Round {}'.format(i),value="{} {} {}".format(person_1,random.choice(fights),person_2),inline = False)
		await client.send_message(message.channel,embed=embed)
		wlt = ["{} has defeated {}".format(person_1,person_2),"{} has defeated {}".format(person_2,person_1),"It's a tie!"]
		embed = discord.Embed(title="Result of the battle",description=random.choice(wlt),color=discord.Color.green())
		await client.send_message(message.channel,embed=embed)
	
	# Tech News

	if message.content.upper().startswith('TECHNEWS!'):
		if message.author.id == os.getenv('OWNER'):
			th1=newsapi.get_top_headlines(q='technology',sources='ars-technica',language='en')
			th2=newsapi.get_top_headlines(q='technology',sources='engadget',language='en')
			th3=newsapi.get_top_headlines(q='technology',sources='hacker-news',language='en')
			th4=newsapi.get_top_headlines(q='technology',sources='recode',language='en')
			th5=newsapi.get_top_headlines(q='technology',sources='techcrunch',language='en')
			th6=newsapi.get_top_headlines(q='technology',sources='techradar',language='en')
			th12=newsapi.get_top_headlines(q='tech',sources='ars-technica',language='en')
			th22=newsapi.get_top_headlines(q='tech',sources='engadget',language='en')
			th32=newsapi.get_top_headlines(q='tech',sources='hacker-news',language='en')
			th42=newsapi.get_top_headlines(q='tech',sources='recode',language='en')
			th52=newsapi.get_top_headlines(q='tech',sources='techcrunch',language='en')
			th62=newsapi.get_top_headlines(q='tech',sources='techradar',language='en')
			s=[]
			if (len(th1['articles'])!=0):
				s.append(th1['articles'][0]['url'])
			if (len(th2['articles'])!=0):
				s.append(th2['articles'][0]['url'])
			if (len(th3['articles'])!=0):
				s.append(th3['articles'][0]['url'])
			if (len(th4['articles'])!=0):
				s.append(th4['articles'][0]['url'])
			if (len(th5['articles'])!=0):
				s.append(th5['articles'][0]['url'])
			if (len(th6['articles'])!=0):
				s.append(th6['articles'][0]['url'])
			if (len(th12['articles'])!=0):
				s.append(th12['articles'][0]['url'])
			if (len(th22['articles'])!=0):
				s.append(th22['articles'][0]['url'])
			if (len(th32['articles'])!=0):
				s.append(th32['articles'][0]['url'])
			if (len(th42['articles'])!=0):
				s.append(th42['articles'][0]['url'])
			if (len(th52['articles'])!=0):
				s.append(th52['articles'][0]['url'])
			if (len(th62['articles'])!=0):
				s.append(th62['articles'][0]['url'])
			headlines=list(set(s))
			embed=discord.Embed(title='Tech News',description='The latest Tech News of the day.',colour=discord.Colour.teal())
			embed.set_footer(text='Powered by NewsAPI')
			technews = client.get_channel(os.getenv('TECH_NEWS_ID'))
			if(len(headlines)!=0):
				for i in range(1,len(headlines)+1):
					news_number='News-{}'.format(i)
					embed.add_field(name=news_number,value=headlines[i-1],inline=False)
			else:
				embed.add_field(name='Sorry!',value='No news available right now',inline=False)
			await client.send_message(technews, embed=embed)
		else:
			embed = discord.Embed(title = 'WARNING',description='You are not allowed to use this command!',color = discord.Color.red())
			await client.send_message(message.channel, embed=embed)
	
# EXPERIENCE SYSTEM

async def update_data(users, user):
	if not user.id in users:
		users[user.id]={}
		users[user.id]['experience'] = 0
		users[user.id]['level'] = 1

async def add_experience(users,user,exp):
	users[user.id]['experience'] += exp 

async def level_up(users, user, channel) :
	experience = users[user.id]['experience']
	lvl_start = users[user.id]['level']
	lvl_end = int(experience**(1/4))

	if lvl_start < lvl_end and user.id != os.getenv('BOT'):
		embed = discord.Embed(title = 'Congrats!',description='{} has leveled up to level {}'.format(user.mention,lvl_end),color=discord.Color.blue())
		await client.send_message(channel,embed = embed)
		users[user.id]['level'] = lvl_end

	role1 = "Regular"
	role2 = "Super Regular"
	role3 = "Super Duper Regular"
	role4 = "Amazingly Regular"
	role5 = "Super Duper Amazingly Regular"
	role6 = "Omega Member"
 
	server=client.get_server(os.getenv('SERVER_ID'))
	for role in server.roles:
		if role.name == role1:
			role1 = role
		if role.name == role2:
			role2 = role
		if role.name == role3:
			role3 = role
		if role.name == role4:
			role4 = role
		if role.name == role5:
			role5 = role
		if role.name == role6:
			role6 = role

	if users[user.id]['level'] == 10:
		await client.add_roles(user,role1)
		embed = discord.Embed(title = 'Congrats!',description='{}, You have {} role now!'.format(user.mention,role1.mention),color=discord.Color.blue())
		await client.send_message(channel,embed = embed)

	if users[user.id]['level'] == 20:
		await client.add_roles(user,role2)
		embed = discord.Embed(title = 'Congrats!',description='{}, You have {} role now!'.format(user.mention,role2.mention),color=discord.Color.blue())
		await client.send_message(channel,embed = embed)

	if users[user.id]['level'] == 40:
		await client.add_roles(user,role3)
		embed = discord.Embed(title = 'Congrats!',description='{}, You have {} role now!'.format(user.mention,role3.mention),color=discord.Color.blue())
		await client.send_message(channel,embed = embed)

	if users[user.id]['level'] == 50:
		await client.add_roles(user,role4)
		embed = discord.Embed(title = 'Congrats!',description='{}, You have {} role now!'.format(user.mention,role4.mention),color=discord.Color.blue())
		await client.send_message(channel,embed = embed)

	if users[user.id]['level'] == 80:
		await client.add_roles(user,role5)
		embed = discord.Embed(title = 'Congrats!',description='{}, You have {} role now!'.format(user.mention,role5.mention),color=discord.Color.blue())
		await client.send_message(channel,embed = embed)

	if users[user.id]['level'] == 100:
		await client.add_roles(user,role6)
		embed = discord.Embed(title = 'Congrats!',description='{}, You have {} role now!'.format(user.mention,role6.mention),color=discord.Color.blue())
		await client.send_message(channel,embed = embed)
	
		
#Introduction of a new user. Note that in asyncio the ids are strings.	

@client.event
async def on_member_join(member):
	userid=member.mention
	channel = client.get_channel(os.getenv('INTRO_CHANNEL_ID'))
	channel_rules=client.get_channel(os.getenv('RULES_CHANNEL_ID'))
	language_role_channel = client.get_channel(os.getenv('LANG_ROLE_ID'))
	topic_role_channel = client.get_channel(os.getenv('TOPIC_ROLE_CHANNEL_ID'))
	msg='Welcome to Sparks and Glory {}! Please look at {} before proceeding, and assign yourself language roles in {} and topic roles in {}! Have fun!'.format(userid,channel_rules.mention,language_role_channel.mention,topic_role_channel.mention)
	await client.send_message(channel,msg)
	
	# Creating an user account for exp system.

	with open('users.json','r') as f:
		users = json.load(f)

	await update_data(users,member)

	with open('users.json','w') as f:
		json.dump(users, f)

#Bidding goodbye when a member leaves.

@client.event
async def on_member_remove(member):
	userid=member.mention
	channel=client.get_channel(os.getenv('INTRO_CHANNEL_ID'))
	msg='Farewell {}! Best of luck for the future!'.format(userid)
	await client.send_message(channel,msg)

# #Tech News.

# async def send_news():
# 	await client.wait_until_ready()
# 	while not client.is_closed:
# 		th1=newsapi.get_top_headlines(q='technology',sources='ars-technica',language='en')
# 		th2=newsapi.get_top_headlines(q='technology',sources='engadget',language='en')
# 		th3=newsapi.get_top_headlines(q='technology',sources='hacker-news',language='en')
# 		th4=newsapi.get_top_headlines(q='technology',sources='recode',language='en')
# 		th5=newsapi.get_top_headlines(q='technology',sources='techcrunch',language='en')
# 		th6=newsapi.get_top_headlines(q='technology',sources='techradar',language='en')
# 		th12=newsapi.get_top_headlines(q='tech',sources='ars-technica',language='en')
# 		th22=newsapi.get_top_headlines(q='tech',sources='engadget',language='en')
# 		th32=newsapi.get_top_headlines(q='tech',sources='hacker-news',language='en')
# 		th42=newsapi.get_top_headlines(q='tech',sources='recode',language='en')
# 		th52=newsapi.get_top_headlines(q='tech',sources='techcrunch',language='en')
# 		th62=newsapi.get_top_headlines(q='tech',sources='techradar',language='en')
# 		s=[]
# 		if (len(th1['articles'])!=0):
# 			s.append(th1['articles'][0]['url'])
# 		if (len(th2['articles'])!=0):
# 			s.append(th2['articles'][0]['url'])
# 		if (len(th3['articles'])!=0):
# 			s.append(th3['articles'][0]['url'])
# 		if (len(th4['articles'])!=0):
# 			s.append(th4['articles'][0]['url'])
# 		if (len(th5['articles'])!=0):
# 			s.append(th5['articles'][0]['url'])
# 		if (len(th6['articles'])!=0):
# 			s.append(th6['articles'][0]['url'])
# 		if (len(th12['articles'])!=0):
# 			s.append(th12['articles'][0]['url'])
# 		if (len(th22['articles'])!=0):
# 			s.append(th22['articles'][0]['url'])
# 		if (len(th32['articles'])!=0):
# 			s.append(th32['articles'][0]['url'])
# 		if (len(th42['articles'])!=0):
# 			s.append(th42['articles'][0]['url'])
# 		if (len(th52['articles'])!=0):
# 			s.append(th52['articles'][0]['url'])
# 		if (len(th62['articles'])!=0):
# 			s.append(th62['articles'][0]['url'])
# 		headlines=list(set(s))
# 		embed=discord.Embed(title='Tech News',description='Tech News of the Week, brought to you by Sparky.',colour=discord.Colour.teal())
# 		embed.set_footer(text='Powered by NewsAPI')
# 		technews = client.get_channel(os.getenv('TECH_NEWS_ID'))
# 		if(len(headlines)!=0):
# 			for i in range(1,len(headlines)+1):
# 				news_number='News-{}'.format(i)
# 				embed.add_field(name=news_number,value=headlines[i-1],inline=False)
# 		else:
# 			embed.add_field(name='Sorry!',value='No news available right now',inline=False)
# 		await client.send_message(technews, embed=embed)
# 		await asyncio.sleep(172800)

# client.loop.create_task(send_news())
client.run(os.getenv('TOKEN'))
