import requests
import os
import json
import simplejson
import time

class BungieData(object):
    '''
    For the API calls below, no authentication is needed. You'll just need to have your Bungie API key exported in your bash profile
    and named as BUNGIE_API_KEY to run the script as-is.
    '''
    #%%variables that you might want to change on different runs
    user_platform = 'psn'  #either 'psn' or 'ps4' or 'xbone' or 'xbox'  (pc is busted)
    save_to_file = 0  #flag: set to 1 if you want certain bits saved to file to peruse
    baseurl = 'https://bungie.net/Platform/Destiny2/'
    baseurl_groupv2 = 'https://bungie.net/Platform/GroupV2/'
    membership_types = {'xbox': '1',  'xbone': '1', 'psn': '2', 'pc': '4', 'ps4': '2'}

    #Following conversions have names that Cortical-IV used for user summary stats as keys,
    #and names that bungie uses as values for when he extracted from end points.
    #May be useful later
    pveKeyConversion = {'numEventsPve': 'activitiesEntered',
                 'kdPve': 'killsDeathsRatio',
                 'durationPlayedPve': 'totalActivityDurationSeconds',
                 'favoriteWeaponPve': 'weaponBestType',
                 'longestKillDistancePve': 'longestKillDistance',
                 'orbsGeneratedPve': 'orbsDropped',
                 'suicideRatePve': 'suicides',
                 'longestKillSpreePve': 'longestKillSpree'}

    pvpKeyConversion = {'numEventsPvp': 'activitiesEntered',
                 'numWinsPvp': 'activitiesWon',
                 'winLossRatioPvp': 'winLossRatio',
                 'kdPvp': 'killsDeathsRatio',
                 'durationPlayedPvp': 'totalActivityDurationSeconds',
                 'favoriteWeaponPvp': 'weaponBestType',
                 'mostKillsPvp': 'bestSingleGameKills',
                 'longestKillSpreePvp': 'longestKillSpree',
                 'suicideRatePvp': 'suicides'}

    def __init__(self, api_key):
        '''
        api_key (str): The api key given to you by Bungie when you registered your app with them
        '''
        self.api_key = api_key

    def get_PSNplayerByTagName(self, gamertag):
        '''gamertag (str): The PSN gamertag a player uses on Destiny 2'''
        site_call = "https://bungie.net/Platform/Destiny2/SearchDestinyPlayer/2/" + gamertag
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_XboxplayerByTagName(self, gamertag):
        '''gamertag (str): The Xbox gamertag a player uses on Destiny 2'''
        site_call = "https://bungie.net/Platform/Destiny2/SearchDestinyPlayer/1/" + gamertag
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_PSNDestinyUserId(self, gamertag):
        '''gamertag (str): The PSN gamertag a player uses on Destiny 2'''
        info = self.get_PSNplayerByTagName(gamertag)
        return int(info[0]['membershipId'])

    def get_XboxDestinyUserId(self, gamertag):
        '''gamertag (str): The Xbox gamertag a player uses on Destiny 2'''
        info = self.get_XboxplayerByTagName(gamertag)
        return int(info[0]['membershipId'])

    def get_BungieUserId(self, membership_id):
        '''
        membership_id (int): the Destiny membership_id of a player (the id returned by get_DestinyUserId)
        Uses old Destiny endpoint for a PSN user to get the BUNGIE membershipId
        '''
        site_call = "https://bungie.net/Platform/User/GetMembershipsById/" + str(membership_id) + "/2/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return int(request.json()['Response']['bungieNetUser']['membershipId'])

    def get_DestinyUserProfile(self, membership_id, platform, components=[100]):
        '''
        membership_id (int): the Destiny membership_id of a player (returned by get_DestinyUserId)
        components (list of ints): the type of info you want returned according the Bungie API docs.
          Defaults to 100: basic profile info ([100, 200] would also return more detailed info by Destiny character
        Uses new Destiny 2 endpoint for player using the Destiny membershipId
        '''
        components = "?components=" + ','.join([str(c) for c in components])
        site_call = "https://bungie.net/Platform/Destiny2/" + str(platform) + "/Profile/" + str(membership_id) + "/" + components
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_postGameStats(self, game_id):
        '''get_postGameStats

        inputs:
        game_id (int): The activityid, per the BungieAPI,

        returns:
        The JSON response from the BungieAPI'''

        site_call = "https://bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/" + str(game_id)
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_Manifest(self):
        site_call = "https://bungie.net/Platform/Destiny2/Manifest/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_PlayerStatsforAccount(self, membership_id, platform):
        '''
        Returns the Account-specific stats for the membership_id'''

        site_call = "https://bungie.net/Platform/Destiny2/" +str(platform) + "/Account/" + str(membership_id) + "/Stats/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_StatDefinitions(self):
        site_call = "https://bungie.net/Platform/Destiny2/Stats/Definition/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def printProfile(self, profilehash):
        '''printProfile
        Inputs: profilehash: the dictionary returned from the get_DestinyUserProfile method

        Returns: Nothing; Prints the User Profile
        '''
        print("Destiny Profile Info")
        print("-" * 40)
        for key in profilehash:
            print("Key ", key, " ||| ", profilehash[key], "\n")
        print("-" * 40)

    def get_historical_stats_url(self, user_name, user_platform, character_id, my_api_key, activity_modes = 'None'):
        """Return tons of useful stats about a character (or set character_id = '0' for
        all character data lumped together).
            https://bungie-net.github.io/multi/operation_get_Destiny2-GetHistoricalStats.html
        Note modes are from the same list as above with GetActivityHistory."""
        user_id = get_user_id(user_name, user_platform, my_api_key)
        membership_type = membership_types[user_platform]
        query_string = '?modes=' + activity_modes
        return baseurl + membership_type + '/Account/' + user_id + '/Character/' + \
               character_id + '/Stats/' + query_string

#Untested, pulled as an example from https://gist.github.com/cortical-iv/a22ef122e771b994454e02b6b4e481c3
    def summarize_pve(self, user_name, user_stats):
        """pull stats of interest from accounts pve history. Uses the user_stats
        dictionary created by GetHistoricalStats"""
        user_pve_summary = {}
        allPvE = user_stats['allPvE']
        if allPvE:
            pve_stats = allPvE['allTime']
            for newKey, oldKey in pveKeyConversion.items():
                if newKey == 'suicideRatePve':
                    user_pve_summary[newKey] = pve_stats[oldKey]['pga']['displayValue']
                else:
                    user_pve_summary[newKey] = pve_stats[oldKey]['basic']['displayValue']
        else:
            user_pve_summary['numEventsPve'] = None
        #Raid stats are stored separately
        raid_dat = user_stats['raid']
        if raid_dat:
            raid_stats = raid_dat['allTime']
            for newKey, oldKey in raidKeyConversion.items():
                user_pve_summary[newKey] = raid_stats[oldKey]['basic']['displayValue']
        else:
            user_pve_summary['raidAttempts'] = None
        user_pve_summary['userName'] = user_name
        return user_pve_summary

#Untested
    def summarize_pvp(self, user_name, user_stats):
        """pull stats of interest from accounts' pvp history. Uses user_stats structure returned
        by GetHistoricalStats."""
        user_pvp_summary = {}
        allPvP = user_stats['allPvP']
        if allPvP:  #if they have done any pvp
            pvp_stats = allPvP['allTime']
            for newKey, oldKey in pvpKeyConversion.items():
                if newKey == 'suicideRatePvp':
                    user_pvp_summary[newKey] = pvp_stats[oldKey]['pga']['displayValue']
                else:
                    user_pvp_summary[newKey] = pvp_stats[oldKey]['basic']['displayValue']
        else: #they have not done any pvp
            user_pvp_summary['numEventsPvp'] = None
        user_pvp_summary['userName'] = user_name
        return user_pvp_summary

if __name__ == '__main__':
    bungie = BungieData(api_key=os.environ["BUNGIE_API_KEY"]) # Never put your keys in code... export 'em!

    # Get Destiny MembershipId by PSN gamertag
    '''username = "BalancedSeeker6"

    my_destiny_id = bungie.get_PSNDestinyUserId(username)
    print("{}'s Destiny ID: {}".format(username, my_destiny_id))
    print("-----------------")

    #Get Destiny MembershipID by Xbox gamertag
    username = "Peruna"
    my_destiny_id = bungie.get_XboxDestinyUserId(username)
    print("{}'s Destiny ID: {}".format(username, my_destiny_id))
    print("-----------------")

    historicalstats = bungie.get_PlayerStatsforAccount(my_destiny_id, 1)'''

    #historicalstats_json = json.dumps(historicalstats, indent=4, sort_keys=True)
    #with open('formatted_account_data_peruna.json', 'w') as outfile:
    #    outfile.write(historicalstats_json)
    #print(historicalstats_json)

    # Get User's Profile info and more detailed Character info
    #my_profile = bungie.get_DestinyUserProfile(my_destiny_id, 1, components=[100,200])
    #bungie.printProfile(my_profile)

    # Get a a single game's post carnage stats
    '''game_stats = bungie.get_postGameStats(2719755381)

    game_stats_json = json.dumps(game_stats)
    print("Type is: ", type(game_stats_json))
    print(game_stats_json)

    #print("Random Destiny 2 game's post carnage game stats: \n{}".format(game_stats))
    with open('matchdata.json', 'w') as outfile:
        outfile.write(game_stats_json)
        #outfile.write(simplejson.dumps(simplejson.loads(game_stats), indent=4, sort_keys=True))
    '''

    #Scrape PGCRs
    '''
    game = 2719755381
    with open('./data/unfilteredpgcrdata.json', 'a+') as outfile:
        for i in range(100):
            print("Attempt #",i+1)
            game += i
            try:
                game_stats = bungie.get_postGameStats(game)
                #formatted for easier viewing, although it greatly increases filesize
                game_stats_json = json.dumps(game_stats, indent=4, sort_keys=True)
                outfile.write(game_stats_json)
            except:
                print("Something went wrong on game: ", game, "i: ",i)
            time.sleep(2)
    '''
    #Second attempt, pull 5k entries, unformatted.
    game = 2719755481 #note that this is 100 gameids higher than my IB PvP game
    with open('./data/unformatted_unfiltered_pgcrdata_5k.json', 'a+') as outfile:
        for i in range(5000):
            print("Attempt #",i+1)
            game += i
            try:
                game_stats = bungie.get_postGameStats(game)
                #formatted for easier viewing, although it greatly increases filesize
                game_stats_json = json.dumps(game_stats)
                outfile.write(game_stats_json)
            except:
                print("Something went wrong on game: ", game, "i: ",i)
            time.sleep(2)


    #for key in game_stats:
    #    print("Key ", key, " ||| ", game_stats[key])
