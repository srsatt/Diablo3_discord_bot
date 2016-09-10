#!/usr/local/bin/Python3.5
import requests
import json

api_key="Your battle.net API key"
#https://dev.battle.net - registration in battle.net site


def get_profile(name,code):
    url="https://eu.api.battle.net/d3/profile/"+str(name)+"-"+str(code)+"/?locale=en_GB&apikey="+api_key
    r=requests.get(url)
    profile=json.loads(r.text)
    result={
         "battleTag":profile["battleTag"],
         "paragonLevel": profile["paragonLevel"],
         "paragonLevelHardcore": profile["paragonLevelHardcore"],
         "paragonLevelSeason": profile["paragonLevelSeason"],
         "paragonLevelSeasonHardcore": profile["paragonLevelSeasonHardcore"],
         "heroes_id":[hero["id"] for hero in profile["heroes"]],
    }
    return result

def get_hero_info(name,code,id):
    url="https://eu.api.battle.net/d3/profile/"+name+"-"+str(code)+"/hero/"+str(id)+"?locale=en_GB&apikey="+api_key
    #this is for EU battle.net sever.
    r=requests.get(url)
    result=json.loads(r.text)
    #print(json.dumps(profile,sort_keys=True,indent=4, separators=(',', ': ')))
    if result['class']:
        print("OK")
    else:
        print("DONGER!DONGER!")
    return {
        "hero_id":id,
        "class":result['class'],
        "name":result['name'],
        "seasonal":result['seasonal'],
        "hardcore":result['hardcore'],
        "paragonLevel":result['paragonLevel'],
        "link":link_for_hero(name,code,id),
        "battleTag":name+"#"+str(code),
    }

def link_for_hero(name,code,id):
    return "http://eu.battle.net/d3/ru/profile/"+name+"-"+str(code)+"/hero/"+str(id)
