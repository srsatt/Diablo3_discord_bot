#!/usr/local/bin/Python3.5
import discord
import d3api
import pymongo
import json
import othercommands
token="add your token"
#discord token https://discordapp.com/developers/docs/intro - for getting token
MONGO_ADDRESS='127.0.0.1'
MONGO_PORT=27017
server_name='your server name'
#Discord app server name
client = discord.Client()

def get_server(server_name):
    for server in client.servers:
        if server.name==server_name:
            return server
def get_member(name):
    for server in client.servers:
        for member in server.members:
            if member.name==name:
                return member
def hero_print(hero):
    msg="Class: "+hero['class']+"\n"
    msg+="Name: "+hero['name']+"\n"
    msg+="Paragon level: "+str(hero['paragonLevel'])+"\n"
    msg+="battle.net link: "+hero['link']+"\n"
    msg+="Hero ID: "+str(hero['hero_id'])+"\n"
    try:
        msg+="Hero alias: "+hero['alias']+"\n"
    except KeyError:
        pass
    try:
        msg+="Hero description: "+hero['hero_text']+"\n"
    except KeyError:
        pass
    msg+="\n"
    return msg

def update_profile(message,nick,code):
    profile=d3api.get_profile(nick,code)
    #await client.send_message(message.channel, "your bTag is "+profile["battleTag"]+"\n and your paragon is "+str(profile["paragonLevel"]))
    conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
    db=conn['d3b']
    users=db['d3b_users']
    heroes=db['d3b_heroes']
    user={
        'user_name':message.author.name,
        'battleTag':profile['battleTag'],
        'paragonLevel':profile['paragonLevel'],
        'paragonLevelHardcore':profile['paragonLevelHardcore'],
        'paragonLevelSeason':profile['paragonLevelSeason'],
        'paragonLevelSeasonHardcore':profile['paragonLevelSeasonHardcore'],
        'heroes':profile['heroes_id'],
        'inParty':False,
        }
    for hero_id in user['heroes']:
        hero=d3api.get_hero_info(nick,code,hero_id)
        if heroes.find_one({'hero_id':hero_id}):
            for key in hero.keys():
                heroes.update_one({'hero_id':hero_id},{"$set":{key:hero[key]}})
        else:
            heroes.insert(hero)
    if users.find_one({'user_name':message.author.name}):
        users.update({'user_name':message.author.name},user)
    else:
        users.save(user)
    conn.close()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_channel_create(channel):
    pass

@client.event
async def on_message(message):
#импортируем из отдельного файла различные команды
    for command in othercommands.commands.keys():
        if message.content.startswith(command):
            await client.send_message(message.channel,othercommands.commands[command])
            break
    if message.content.startswith('!help'):
        await client.send_message(message.channel,\
        "Welcome to the bot's guide\n"+\
        "All bot commands, except !help and some other commands you must write in private message to bot\n"+\
        "Available bot commands:\n"+\
        "!hi nick#code - This is registration in this system, you should add your nick and code from your battle.net account\n"+\
        "!heroes - lsit of your heroes. You can add filter for SC/HC and Season/Non-season (for example !heroes NS/SC и !heroes S/HC)\n"+\
        "!heroes all - list of all your heroes\n"+\
        "!heroes update - updating of your heres list\n"+\
        "!namehero id nick description - you can add description and alias for your hero. id - it's numbers in your link to battle.net"+\
        "Hero nick must be in 1 word and must be unique for any hero.\n"+\
        "!lfg nick label description - adds your hero to LFG queue. nick - it's nick wich you've made with !namehero command"+\
        "label - group label. It can be one of this list: fast,push,rift,uber,acts,other,boost. "+\
        "description - some text that other people can see\n")
        await client.send_message(message.channel,\
        "!pool nick label - displays all peple which are looking for same group.\n"+\
        "!partycreate nick label description - command for creating party. You are becoming party leader \n"+\
        "!parties nick label - list of groups available for your hero.\n"+\
        "!invite user_name user_nick - You can ivinte player with  user_name discord name and user_nick  - his hero nick\n"+\
        "!partyleave - command for leaving your group. If you are party leader, this party will disband.\n"+\
        "!request user_nick hero_nick - sending request for party leader.\n"+\
        "!partystart - when your group is set you can write this command to create private channel in Discord and send invitation for party members."+\
        "\n\n"+\
        


        return
#приватные команды боту
    if message.channel.is_private==True:
        if message.author == client.user:
                return

        if message.content.startswith('!hi'):

            d=message.content.split(" ")
            d=d[1].split("#")
            update_profile(message,d[0],d[1])
            await client.send_message(message.channel,"Congratulations, now Bot know your battle.net account, now you have access to another commands")
            return


        if message.content.startswith('!heroes'):
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            users=db['d3b_users']
            heroes=db['d3b_heroes']
            user=users.find_one({'user_name':message.author.name})
            if user:
                msg_body=""
                try:
                    if message.content.split(" ")[1]=="NS/SC":
                        for hero_id in user['heroes']:
                             hero=heroes.find_one({'hero_id':hero_id})
                             if hero['seasonal']==False and hero['hardcore']==False:
                                 msg_body+=hero_print(hero)
                    elif message.content.split(" ")[1]=="S/SC":
                        for hero_id in user['heroes']:
                             hero=heroes.find_one({'hero_id':hero_id})
                             if hero['seasonal']==True and hero['hardcore']==False:
                                 msg_body+=hero_print(hero)
                    elif message.content.split(" ")[1]=="NS/HC":
                        for hero_id in user['heroes']:
                             hero=heroes.find_one({'hero_id':hero_id})
                             if hero['seasonal']==False & hero['hardcore']==True:
                                 msg_body+=hero_print(hero)
                    elif message.content.split(" ")[1]=="S/HC":
                        for hero_id in user['heroes']:
                             hero=heroes.find_one({'hero_id':hero_id})
                             if hero['seasonal']==True & hero['hardcore']==True:
                                 msg_body+=hero_print(hero)
                    elif message.content.split(" ")[1]=="all":
                        for hero_id in user['heroes']:
                             hero=heroes.find_one({'hero_id':hero_id})
                             msg_body+=hero_print(hero)

                    elif message.content.split(" ")[1]=="update":
                        nick, code = user["battleTag"].split("#")
                        update_profile(message,nick, code)
                        msg_body="heroes list had been updated"
                except IndexError:
                    if message.content=="!heroes":
                        for hero_id in user['heroes']:
                             hero=heroes.find_one({'hero_id':hero_id})
                             msg_body+=hero_print(hero)
                #print(msg_body)
                if msg_body=="":
                    await client.send_message(message.channel,"No heroes in this category")
                else:
                    await client.send_message(message.channel,msg_body)
            else:
                await client.send_message(message.channel,"Bot doesn't know you yet, please write !hi your_battle_net_nick#battle_net_code")
            conn.close()

            return

        if message.content.startswith('!namehero'):
            #hero_id name text
            text=message.content.split(" ")
            hero_id=int(text[1])
            hero_alias=text[2]
            text=" ".join(text[3:])
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            users=db['d3b_users']
            heroes=db['d3b_heroes']
            user=users.find_one({'user_name':message.author.name})
            hero=heroes.find_one({'hero_id':hero_id})
            if hero_id in user['heroes']:
                result=heroes.update_one({'hero_id':hero_id}, {"$set" : {"alias":hero_alias}})
                result=heroes.update_one({'hero_id':hero_id},{"$set" : {"hero_text":text}})
                hero=heroes.find_one({'hero_id':hero_id})
                await client.send_message(message.channel,hero_print(hero))
            else:
                await client.send_message(message.channel,"Access Error")
            conn.close()
            return
        if message.content.startswith('!lfgleave'):
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            pool=db['pool']
            pool.delete_one({'user':message.author.name})
            await client.send_message(message.channel,"You left gruop find queue")
            conn.close()
            return
        if message.content.startswith('!lfg'):
            heroname, label = message.content.split(" ")[1], message.content.split(" ")[2]
            if label not in ["fast",'push','rift','uber','acts','other','boost']:
                  await client.send_message(message.channel,"There is no such group label, plese write another command")
                  return
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            users=db['d3b_users']
            heroes=db['d3b_heroes']
            pool=db['pool']
            user=users.find_one({'user_name':message.author.name})
            hero=heroes.find_one({'alias':heroname,'battleTag':user['battleTag']})
            if hero and hero['hero_id'] in user['heroes']:
                pass
            else:
                await client.send_message(message.channel,"No hero with this name. Try command !namehero")
                conn.close()
                return
            lfg={'user':message.author.name,
                'hero':hero['hero_id'],
                'label':label,
                'seasonal':hero['seasonal'],
                'hardcore':hero['hardcore'],
                'text':" ".join(message.content.split(' ')[3:]),}
            if pool.find_one({'user':message.author.name}):
                await client.send_message(message.channel,"You can't join queue because one of your heroes is in the queue. Try to leave with queue with !leavelfg command")

            elif user['inParty']:
                await client.send_message(message.channel,"You can't join queue because you are already in some group. Use command !leaveparty")

            else:
                 pool.insert_one(lfg)
                 await client.send_message(message.channel,"You have joined LFG queue")
            conn.close()
            return

        if message.content.startswith('!pool'):
            try:
                heroname = message.content.split(" ")[1]
            except IndexError:
                await client.send_message(message.channel,"You haven't chose hero name")
                return
            try:
                label=message.content.split(" ")[2]
            except IndexError:
                label='all'
            if label not in ["fast",'push','rift','uber','acts','other','all','boost']:
                  await client.send_message(message.channel,"There is no group label. Try again")
                  return
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            users=db['d3b_users']
            heroes=db['d3b_heroes']
            pool=db['pool']
            user=users.find_one({'user_name':message.author.name})
            hero=heroes.find_one({'alias':heroname,'battleTag':user['battleTag']})
            if hero and hero['hero_id'] in user['heroes']:
                pass
            else:
                await client.send_message(message.channel,"There is no hero with this name. Try command !namehero")
                conn.close()
                return
            msg_body=""
            for lfg in pool.find():
                #and lfg['user']!=message.author.name
                if (label==lfg['label'] or label=='all') and hero['seasonal']==lfg['seasonal'] and hero['hardcore']==lfg['hardcore'] :
                    lfg_hero=heroes.find_one({'hero_id':lfg['hero']})
                    msg_body+=lfg['user']+" is looking for group with hero:\nClass: "+lfg_hero['class']+'\nHero name: '+lfg_hero['alias']+'\nParagon level: '+str(lfg_hero['paragonLevel'])+'\n'+"Battle.net link: "+lfg_hero['link']+'\n'+'Party label: '+lfg['label']+'\nwith text: '+lfg['text']+' \n \n'
            if msg_body:
                await client.send_message(message.channel, "People which you can join:\n"+msg_body)
            else:
                await client.send_message(message.channel, "No people yet")
            conn.close()
        #!lfg heroname rift/grift/uber/acts/other

        if message.content.startswith('!partycreate'):
            try:
                heroname = message.content.split(" ")[1]
            except IndexError:
                await client.send_message(message.channel,"You haven't chose hero name for starting group.")
                return
            try:
                label=message.content.split(" ")[2]
            except IndexError:
                await client.send_message(message.channel,"You haven't chose group label. Please, try again later.")
                return
            if label not in ["fast",'push','rift','uber','acts','other','boost']:
               await client.send_message(message.channel,"There is no group label. Please try again.")
               return
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            users=db['d3b_users']
            heroes=db['d3b_heroes']
            parties=db['parties']
            pool=db['pool']
            user=users.find_one({'user_name':message.author.name})
            hero=heroes.find_one({'alias':heroname,'battleTag':user['battleTag']})
            users.update_one({'user_name':message.author.name},{"$set":{'inParty':True}})
            if user['inParty']:
                await client.send_message(message.channel,"Your are already in some group. Leave this group wuth command!partyleave")
                conn.close()
                return
            text=" ".join(message.content.split(" ")[3:])
            party={'leader':message.author.name,
                   'isStarted':False,
                   'users':[hero['hero_id']],
                   'user_names':[message.author.name],
                   'channel':None,
                   'text':text,
                   'label':label,
                   'hardcore':hero['hardcore'],
                   'seasonal':hero['seasonal']}
            pool.delete_one({'user':message.author.name})
            parties.insert_one(party)
            await client.send_message(message.channel,"You have created your group and now you can invite other people with !invite command. Also, you can start voice channel with command !partystart")
            conn.close()
            return

        if message.content.startswith('!parties'):
            try:
                heroname = message.content.split(" ")[1]
            except IndexError:
                await client.send_message(message.channel,"You haven't chose hero for finding your group.")
                return
            try:
                label=message.content.split(" ")[2]
            except IndexError:
                label="all"
            if label not in ["fast",'push','rift','uber','acts','other','all','boost']:
                  await client.send_message(message.channel,"There is no such group label. Please, try again later.")
                  return
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            heroes=db['d3b_heroes']
            parties=db['parties']
            users=db['d3b_users']
            user=users.find_one({'user_name':message.author.name})
            hero=heroes.find_one({'alias':heroname,'battleTag':user['battleTag']})
            if label=='all':
                party_list=parties.find({'hardcore':hero['hardcore'],'seasonal':hero['seasonal'],'isStarted':False})
            else:
                party_list=parties.find({'hardcore':hero['hardcore'],'seasonal':hero['seasonal'],'label':label,'isStarted':False})
            msg_body=""
            if party_list:
                for party in party_list:
                    msg_body+="Group label: "+party['label']+'\n'+"Group leader: "+party['leader']+'\n'+"Leader's group text: "+party['text']+'\n'+"Group members: \n\n"
                    for member_id in party['users']:
                        member=heroes.find_one({'hero_id':member_id})
                        msg_body+="    Class: "+member["class"]+'\n    Paragon: '+str(member['paragonLevel'])+'\n    BAttle.net link: '+member['link']+'\n'
                        try:
                            msg_body+="    Hero description: "+member['hero_text']+'\n\n'
                        except KeyError:
                            msg_body+='\n'
                await client.send_message(message.channel,"Available groups:\n"+msg_body)
            else:
                await client.send_message(message.channel,"There is no available groups for your hero.")
            conn.close()
            return

        if message.content.startswith('!partyleave'):
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            users=db['d3b_users']
            heroes=db['d3b_heroes']
            parties=db['parties']
            pool=db['pool']
            user=users.find_one({'user_name':message.author.name})
            party=parties.find_one({'user_names':message.author.name})
            if party['leader']==message.author.name:
                for name in party['user_names']:
                    users.update_one({'user_name':name},{"$set":{'inParty':False}})
                parties.delete_one({'leader':message.author.name})
                await client.send_message(message.channel,"You have been party leader and now your group had been disbanded.")
                delining_channel=None
                for ch in get_server(server_name).channels:
                    if ch.name==party['leader']+'\'s group':
                        deliting_channel=ch
                        break
                if deliting_channel:
                    await client.delete_channel(deliting_channel)
                #НАДО ДОБАВИТЬ РАСФОРМИРОВАНИЕ КАНАЛА
            else:
                users.update_one({'user_name':message.author.name},{"$set":{'inParty':False}})
                parties.update_one({'leader':party['leader']},{"$set":{'user_names':party['user_names'].remove(message.author.name)}})
                parties.update_one({'leader':party['leader']},{"$set":{'users':[hero for hero in party['users'] if hero not in user['heroes']]}})
                await client.send_message(message.channel,"You have left this group.")

            conn.close()
            return

        if message.content.startswith('!invite'):

            try:
                nick=message.content.split(' ')[1]
            except IndexError:
                await client.send_message(message.channel,"Enter your player nick for inviting.")
                return
            try:
                hero_nick=message.content.split(' ')[2]
            except IndexError:
                await client.send_message(message.channel,"Enter player's heroname.")
                return

            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']

            users=db['d3b_users']
            heroes=db['d3b_heroes']
            parties=db['parties']
            pool=db['pool']
            if users.find_one({"user_name":nick})['inParty']==True:
                await client.send_message(message.channel,"This player in already in party and you can't invite him.")
                conn.close()
                return
            party=parties.find_one({'leader':message.author.name})
            if party:
                pass
            else:
                await client.send_message(message.channel,"Вы не являетесь лидером ни одной группы и не пожете приглашать игроков")
                conn.close()
                return
            user=users.find_one({'user_name':nick})
            hero=heroes.find_one({'alias':hero_nick,'battleTag':user['battleTag']})
            if hero:
                pool.delete_one({"user":nick})
                users.update_one({"user_name":nick},{"$set":{'inParty':True}})
                parties.update_one({'leader':message.author.name},{'$addToSet':{'users':hero['hero_id']}})
                parties.update_one({'leader':message.author.name},{'$addToSet':{'user_names':nick}})
                users.update_one({'user_name':nick},{"$set":{"inParty":True}})
                await client.send_message(get_member(nick),"Player "+message.author.name+" has invited your in group. If you don't want to play with him write  !partyleave")
                conn.close()
                await client.send_message(message.channel,"You have invited playr in your group.")
                return
            else:
                await client.send_message(message.channel,"There is no player with such nick")
                conn.close()
                return
        if message.content.startswith('!request'):
            try:
                nick=message.content.split(' ')[1]
            except IndexError:
                await client.send_message(message.channel,"Enter party leader's nick.")
                return
            try:
                hero_nick=message.content.split(' ')[2]
            except IndexError:
                await client.send_message(message.channel,"Enter hero name for joining to party.")
                return

            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            users=db['d3b_users']
            heroes=db['d3b_heroes']
            parties=db['parties']
            user=users.find_one({'user_name':message.author.name})
            hero=heroes.find_one({'alias':heroname,'battleTag':user['battleTag']})
            if parties.find_one({'leader':nick}):
                await client.send_message(get_member(nick),"Player "+ message.author.name+" is asking for invitation for your party with this hero:\nClass: "+hero['class']+'\nPragon: '+str(hero['paragonLevel'])+'\n Battle.net link: '+ hero['link']+'\nFor inviting this player plese write !invite '+message.author.name+' '+hero_nick)
            else:
                await client.send_message(message.channel,"This player isn't party leader of any group.")
            conn.close()
            return

        if message.content.startswith('!partystart'):
            conn = pymongo.MongoClient(MONGO_ADDRESS,MONGO_PORT)
            db=conn['d3b']
            users=db['d3b_users']
            parties=db['parties']
            user=users.find_one({'user_name':message.author.name})
            party=parties.find_one({'leader':message.author.name})
            if party:
                parties.update_one({'leader':message.author.name},{"$set":{'isStarted':True}})
                channel=await client.create_channel(get_server(server_name), party['leader']+'\'s group', type='voice')
                deny = discord.Permissions.none()
                deny.connect = True
                allow=discord.Permissions.none()
                allow.connect= True
                await client.edit_channel_permissions(channel,get_server(server_name).default_role,deny=deny)
                invite=await client.create_invite(channel,temporary=True,xkcd=True)
                for name in party['user_names']:
                    await client.edit_channel_permissions(channel,get_member(name),allow=allow)
                    await client.send_message(get_member(name),"Invitation for voice chat: "+invite.url)
            else:
                await client.send_message(message.channel,"You are not party leader for cretating private channel")
            conn.close()


client.run(token)
