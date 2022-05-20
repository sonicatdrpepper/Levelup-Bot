import configparser
import discord
from discord.ext import commands
from time import sleep
#Custom Modules
from Image_Manip import CreateStatCard,CreateLevelCard
from MySQL_Functions import CheckSQLUser, DeleteSQLrow, InsertSQLrow, ReadSQL, WriteSQL

#Initial setup for Discord.py
TOKEN = "YOUR TOKEN HERE"
client = commands.Bot(command_prefix='/',case_insensitive=True)
#List of assignable roles, is case sensititve and must be an EXACT match for role name in guild.
PossibleRoles=["Role1","Role2","Role3"]

#Reads the INI config file for settings
config = configparser.ConfigParser()
config.read("Config.ini")
Roles = config.get('Settings','AssignRoles')

def CalcXP(ID,MesgLEN):
    #Gets data from DB, and converts it to the correct type
    M = ReadSQL(str(ID),"Messages","data")
    L = ReadSQL(str(ID),"level","data")
    E = ReadSQL(str(ID),"EXP","data")
    CE = ReadSQL(str(ID),"CurrentEXP","data")
    M=int(M)
    L=int(L)
    E=float(E)
    CE=float(CE)
    #Actual calculations
    ToNextLevel=5*((10*(4*L))**1.15)
    EXP=.2*float(M)+(int(MesgLEN)/4)
    EXP=EXP/15
    EXP=EXP+float(E)
    EXP=round(EXP,2)
    WriteSQL("EXP",str(EXP),str(ID),"data")
    EXP=EXP-float(E)
    EXP=EXP+CE
    WriteSQL("CurrentEXP",str(EXP),str(ID),"data")
    LevelUp = 0
    #output
    if EXP >= ToNextLevel:
            L=L+1
            WriteSQL("level",str(L),str(ID),"data")
            LevelUp=1
            return LevelUp
    return LevelUp


async def AddRole(ctx,name):
    member=ctx.message.author
    role=discord.utils.get(ctx.guild.roles,name=str(name))
    if name in PossibleRoles:
        await member.add_roles(role)
        print(f"Added role {name} to user {ctx.message.author}")

async def RemoveRole(ctx,name):
    role=discord.utils.get(ctx.guild.roles, name=str(name))
    if name in PossibleRoles:
        await ctx.message.author.remove_roles(role)
        print(f"Removed role {name} from user {ctx.message.author}")

#Returns role based on level of user
def RoleManagement(ID):
    L = ReadSQL(ID,"level","data")
    L=int(L)
    #Handles what role should be assigned based on the level of the given user 
    #ID should be user ID and should be present in database
    if L >= 1 and L < 10:
        return PossibleRoles[0]
    elif L >= 10 and L < 20:
        return PossibleRoles[1]
    elif L >= 20 and L < 30:
        return PossibleRoles[2]
    else:
        return PossibleRoles[0]

@client.event
#Prints to console when bot successfully connects to API
async def on_ready():
    print("Connected to the API")

#Adds ID of guild into settings table upon joining
#Currently have no idea if this works, but its supposed to initialize a row in the second table in the Database upon joining a guild for the first time
#This was to be used for guild specific settings/options
async def on_guild_join(ctx):
    InsertSQLrow(str(ctx.guild.id),"Settings","GuildID")


#Bot Commands

#Shows stats of the user who sent the message
@client.command(name="stats")
async def stats(ctx):
    CR = ReadSQL(str(ctx.message.author.id),"CurrentRole","data")
    await ctx.author.avatar_url_as(format="png").save(fp="Assets/Userpic.png")
    CreateStatCard(ctx.message.author.name,ctx.message.author.id,CR)
    f=discord.File("Assets/Usercard.png")
    await ctx.send(file=f)

#Clears the stats of the user who sent the message, and resets their role(s)
@client.command(name="clearstats")
async def ClearStats(ctx,arg="noConfirm"):
    if arg == "noConfirm":
        await ctx.send("This command will reset `ALL` of your stats, if you are certain you want to continue, type `/clearstats confirm`")
    if arg == "confirm":
        DeleteSQLrow(ctx.message.author.id,"data")
        for i in range(len(PossibleRoles)):
            await RemoveRole(ctx,PossibleRoles[i])
            sleep(.1)
        await ctx.send(f"The data for {ctx.message.author} has been deleted.")
    else:
        return
#Sets the background for Levelup/Stat cards
@client.command(name="Background")
async def Background(ctx,name="list"):
    BG=["gradient","minecraft","fireside","kde","nekopara","sean"]
    memberid=ctx.message.author.id
    
    if name.lower() == BG[0]:
        WriteSQL("Background",'"Assets/Backgrounds/BG2.png"',str(memberid),"data")
        await ctx.send(f"Your background has been set to {BG[0]}")
    elif name.lower == BG[1]:
        WriteSQL("Background",'"Assets/Backgrounds/BG1.png"',str(memberid),"data")
        await ctx.send(f"Your background has been set to {BG[1]}")
    elif name.lower() == BG[2]:
        WriteSQL("Background",'"Assets/Backgrounds/BG3.png"',str(memberid),"data")
        await ctx.send(f"Your background has been set to {BG[2]}")
    elif name.lower() == BG[3]:
        WriteSQL("Background",'"Assets/Backgrounds/BG5.png"',str(memberid),"data")
        await ctx.send(f"Your background has been set to {BG[3]}")
    elif name.lower() == BG[4]:
        WriteSQL("Background",'"Assets/Backgrounds/BG6.png"',str(memberid),"data")
        await ctx.send(f"Your background has been set to {BG[4]}")
    elif name.lower() == BG[5]:
        WriteSQL("Background",'"Assets/Backgrounds/BG7.png"',str(memberid),"data")
        await ctx.send(f"Your background has been set to {BG[5]}")
    else:
        await ctx.send(f"The possible backgrounds are {BG[0]}, {BG[1]}, {BG[2]}, {BG[3]}, {BG[4]}, {BG[5]}")

@client.command(name="Font")
async def Font(ctx,name="list"):
    Fonts=["hack","pixel","impact","comic sans"]
    memberid=ctx.message.author.id
    name = name.lower()
    if name == Fonts[0]:
        WriteSQL("Font",'"Fonts/Hack-Regular.ttf"',str(memberid),"data")
        await ctx.send(f"Your font has been set to {Fonts[0]}")
    if name == Fonts[1]:
        pass
    if name == Fonts[2]:
        pass
    if name == Fonts[3]:
        pass
#/help command was reserved so its called /info
#Displays some basic info about the bot, and more detailed info on certain commands
@client.command(name="info")
async def info(ctx,arg="default"):
    if arg == "default":
        await ctx.send("This bot has a few different commands: \n '/stats \n /clearstats \n and /info \n and /Background`")
    elif arg.lower() == "clearstats":
        await ctx.send("`This command resets your stats and roles to the default values`")
    elif arg.lower() == "background":
        await ctx.send("`The background command is used to select which background you would like to be displayed on your stat image. \n The available background can be viewed with **/background list**`")
    else:
        await ctx.send("That command does not have a help entry")


#Sends a message with the stats of a given user
@client.command(name="getinfo")
async def getinfo(ctx,arg=0):
	if CheckSQLUser(arg) == 0:
		await ctx.send("That user is not in the database")
	CR =ReadSQL(str(arg),"CurrentRole","data")
	M =ReadSQL(str(arg),"Messages","data")
	E =ReadSQL(str(arg),"EXP","data")
	CE =ReadSQL(str(arg),"CurrentEXP","data")
	L =ReadSQL(str(arg),"Level","data")
	L2 = {5*((10*(4*L))**1.15)}
	Font = ReadSQL(str(arg),"Font","data")
	
	user = await client.fetch_user(arg)
	await ctx.send(f"{user} font is {Font}")
	await ctx.send(f"{user}'s Current Role is: {CR}")
	await ctx.send(f"{user} has sent {M} Messages")
	await ctx.send(f"{user} has {E} EXP")
	await ctx.send(f"{user} has {CE} EXP For this Level, out of {L2} exp needed to level up")
	await ctx.send(f"{user} is level {L}")

#This code runs everytime a message is "seen" by the bot
@client.event
async def on_message(message):
    ctx = await client.get_context(message)

    #Keeps the bot from responding to it's own messages
    if message.author == client.user:
        return
    else:
        await client.process_commands(message)
    #Updates data in the DB
    if CheckSQLUser(ctx.author.id) == 1:
        data=ReadSQL(str(ctx.author.id),"Messages","data")
        data = int(data)+1
        WriteSQL("Messages",data,ctx.author.id,"data")
        LevelUp=CalcXP(ctx.author.id,len(message.content))
        

        if LevelUp == 0:
            if Roles == 'True':
                RoleName=RoleManagement(str(ctx.author.id))
            CurrentRoleName = ReadSQL(str(ctx.author.id),"CurrentRole", "data")
        
        elif LevelUp == 1:
            L = ReadSQL(str(ctx.author.id),"level","data")
            if Roles == 'True':
                RoleName=RoleManagement(str(ctx.author.id))
                CurrentRoleName = ReadSQL(str(ctx.author.id),"CurrentRole", "data")
                PrevRole = PossibleRoles.index(CurrentRoleName)
                await RemoveRole(ctx,CurrentRoleName)
                await AddRole(ctx,RoleName)
                WriteSQL("CurrentRole",'"'+RoleName+'"',str(ctx.author.id),"data")
                if L == 35 or L == 45 or L == 70 or L == 75 or L == 90 or L == 100 or L == 125:
                    await ctx.send(f":tada: {ctx.message.author} has become a {RoleName}")
            
            if L == 25 or L == 50 or L == 75 or L == 100 or L == 125:
                await ctx.send(f":tada: {ctx.message.author} has reached a milestone level! :tada:")
            elif L == 69:
                await ctx.send(f"{ctx.message.author} has reached a very ***nice*** level :sunglasses: :sunglasses: :sunglasses: :sunglasses: :100: :100: :100:")
            else:
                await ctx.send(f"Level Up! | :tada:")
            
            WriteSQL("CurrentEXP","0",str(ctx.author.id),"data")
            await ctx.message.author.avatar_url_as(format="png").save(fp="Assets/Userpic.png")
            CreateLevelCard(message.author.name,message.author.id)
            f=discord.File("Assets/Usercard.png")
            await ctx.send(file=f)
            LevelUp = 0
    else:
        #Sets up default values, if a user is not present in the database
        InsertSQLrow(str(ctx.author.id),"data","ID")
        WriteSQL("Messages","0",str(ctx.author.id),"data")
        WriteSQL("level","1",str(ctx.author.id),"data")
        WriteSQL("EXP","0",str(ctx.author.id),"data")
        WriteSQL("CurrentEXP","0",str(ctx.author.id),"data")
        WriteSQL("Background",'"Assets/Backgrounds/BG1.png"',str(ctx.author.id),"data")
        if Roles == 'True':
            RoleName=RoleManagement(str(ctx.author.id))
            WriteSQL("CurrentRole",'"'+RoleName+'"',str(ctx.author.id),"data")
            await AddRole(ctx,RoleName)

#Runs the client
client.run(TOKEN)