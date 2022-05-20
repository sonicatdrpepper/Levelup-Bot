import configparser
import discord
from discord.ext import commands
from time import sleep
#Custom Modules
from Image_Manip import CreateStatCard,CreateLevelCard
from MySQL_Functions import CheckSQLUser, DeleteSQLrow, InsertSQLrow, ReadSQL, WriteSQL

#Initial setup for Discord.py
TOKEN = "Your Token Here"
client = commands.Bot(command_prefix='/',case_insensitive=True)
PossibleRoles=["Common Traveler","Hardened wastelander","Yuis travel companion","Legendary hero"]

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
    ToNextLevel=5*((10*(3*L))**1.3)
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
    role=discord.utils.get(ctx.guild.roles,name=str(name))
    if name in PossibleRoles:
        await ctx.message.author.remove_roles(role)
        print(f"Removed role {name} from user {ctx.message.author}")

#Returns role based on level of user
def RoleManagement(ID):
    L = ReadSQL(ID,"level","data")
    L=int(L)
    #Handles what role should be assigned based on the level of the given user 
    #ID should be user ID and should be present in database
    if L >= 1 and L < 35:
        return PossibleRoles[0]
    elif L >= 35 and L < 55:
        return PossibleRoles[1]
    elif L >= 55 and L < 75:
        return PossibleRoles[2]
    elif L > 75:
        return PossibleRoles[3]
    else:
        return PossibleRoles[4]


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


#Allows you to generate stat cards for other users
@client.command(name="getinfo")
async def getinfo(ctx,arg=0):
    if CheckSQLUser(arg) == 0:
       await ctx.send("That user is not in the database")
    user = await client.fetch_user(arg)
    await user.avatar_url_as(format="png").save(fp="Assets/Userpic.png")
    CreateStatCard(user.name,arg)
    f=discord.File("Assets/Usercard.png")
    await ctx.send(file=f)
#This code runs everytime a message is "seen" by the bot
@client.event
async def on_message(message):
    ctx = await client.get_context(message)

    #Keeps the bot from responding to it's own messages
    if message.author == client.user:
        return
    else:
        await client.process_commands(message)
    
    #LevelUp script
    #I put the code up here because it was easier to work with when it's in its own function
    async def LevelUpScript(LevelUp):
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
                await RemoveRole(ctx,PossibleRoles[PrevRole])
                await AddRole(ctx,RoleName)
                WriteSQL("CurrentRole",'"'+RoleName+'"',str(ctx.author.id),"data")
            
            WriteSQL("CurrentEXP","0",str(ctx.author.id),"data")
            await ctx.message.author.avatar_url_as(format="png").save(fp="Assets/Userpic.png")
            CreateLevelCard(message.author.name,message.author.id)
            await ctx.send(f"Level Up! | :tada:")
            f=discord.File("Assets/Usercard.png")
            await ctx.send(file=f)
            LevelUp = 0
        
    #Updates data in the DB
    ExistsInDB = CheckSQLUser(ctx.author.id)
    if ExistsInDB == 1:
        data=ReadSQL(str(ctx.author.id),"Messages","data")
        data = int(data)+1
        WriteSQL("Messages",data,ctx.author.id,"data")
        LevelUp=CalcXP(ctx.author.id,len(message.content))
        await LevelUpScript(LevelUp)
        LevelUp=0
    else:
        #Sets up default values, if a user is not present in the database
        InsertSQLrow(str(ctx.author.id),"data","ID")
        WriteSQL("Messages","0",str(ctx.author.id),"data")
        WriteSQL("level","1",str(ctx.author.id),"data")
        WriteSQL("EXP","0",str(ctx.author.id),"data")
        WriteSQL("CurrentEXP","0",str(ctx.author.id),"data")
        WriteSQL("Background",'"Assets/Backgrounds/BG1.png"',str(ctx.author.id),"data")
        RoleName=RoleManagement(str(ctx.author.id))
        WriteSQL("CurrentRole",'"'+RoleName+'"',str(ctx.author.id),"data")
        await AddRole(ctx,RoleName)

#Reads and parses config file
INI()
#Runs the client
client.run(TOKEN)