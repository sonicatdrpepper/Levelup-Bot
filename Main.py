import configparser,discord,datetime,requests,shutil
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
ExcludedUsers=["UserID Here"]

#Reads the INI config file for settings
config = configparser.ConfigParser()
config.read("Config.ini")
Roles = config.get('Settings','AssignRoles')

#Gets the current time and formats it nicely
def UpdateTime():
    time=datetime.datetime.now().strftime("%m/%d/%Y, %I:%M %p")
    return time

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
    ToNextLevel=15*((10*(4*L))**1.25)
    EXP=.2*float(M)+(int(MesgLEN)/4)
    EXP=EXP/15
    EXP=EXP+float(E)
    EXP=round(EXP,2)
    WriteSQL("EXP",str(EXP),str(ID),"data")
    EXP=EXP-float(E)
    EXP=EXP+CE
    EXP=round(EXP,2)
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
    if L >= 1 and L < 35:
        return PossibleRoles[0]
    elif L >= 35 and L < 45:
        return PossibleRoles[1]
    elif L >= 45 and L < 69:
        return PossibleRoles[2]
    elif L == 69:
        return PossibleRoles[8]
    elif L > 69 and L < 75:
        return PossibleRoles[3]
    elif L >= 75 and L < 90:
        return PossibleRoles[4]
    elif L >= 90 and L < 100:
        return PossibleRoles[5]
    elif L >= 100 and L < 115:
        return PossibleRoles[6]
    elif L >= 125:
        return PossibleRoles[7]
    else:
        return PossibleRoles[0]


@client.event
#Prints to console when bot successfully connects to API
async def on_ready():
    print("Connected to the API")


#Bot Commands

#Shows stats of the user who sent the message
@client.slash_command(name="stats",description="Show your current stats")
async def stats(ctx):
    #Save Discord User Avatar
    AvatarURL = ctx.author.avatar.url#(format="png").save(fp="Assets/Userpic.png")
    Avatar = requests.get(AvatarURL, stream = True)
    if Avatar.status_code == 200:
        with open("Assets/Userpic.png",'wb') as f:
            shutil.copyfileobj(Avatar.raw, f)

    CR = ReadSQL(str(ctx.author.id),"CurrentRole","data")
    Error = CreateStatCard(ctx.author.name,ctx.author.id,CR)
    if Error == 1:
        await ctx.send("Something went wrong when creating the image, probably something with your pfp")
    f=discord.File("Assets/Usercard.png")
    await ctx.respond(file=f)
    
#Clears the stats of the user who sent the message, and resets their role(s)
@client.slash_command(name="clearstats",description="Resets your EXP, Levels, and Roles")
async def ClearStats(ctx,arg="noConfirm"):
    if arg == "noConfirm":
        await ctx.respond("This command will reset `ALL` of your stats, if you are certain you want to continue, type `/clearstats confirm`")
    if arg == "confirm":
        DeleteSQLrow(ctx.message.author.id,"data")
        for i in range(len(PossibleRoles)):
            await RemoveRole(ctx,PossibleRoles[i])
            sleep(.1)
        await ctx.respond(f"The data for {ctx.message.author} has been deleted.")
    else:
        return


#Sets the background for Levelup/Stat cards
@client.slash_command(name="background",description="Allows you to set your Background to one of several presets")
async def Background(ctx,name="list"):
    BG=["gradient","minecraft","fireside","kde","nekopara","sean"]
    memberid=ctx.author.id
    if name.lower() == BG[0]:
        WriteSQL("Background",'"Assets/Backgrounds/BG2.png"',str(memberid),"data")
        await ctx.respond(f"Your background has been set to {BG[0]}")
    elif name.lower() == BG[1]:
        WriteSQL("Background",'"Assets/Backgrounds/BG1.png"',str(memberid),"data")
        await ctx.respond(f"Your background has been set to {BG[1]}")
    elif name.lower() == BG[2]:
        WriteSQL("Background",'"Assets/Backgrounds/BG3.png"',str(memberid),"data")
        await ctx.respond(f"Your background has been set to {BG[2]}")
    elif name.lower() == BG[3]:
        WriteSQL("Background",'"Assets/Backgrounds/BG5.png"',str(memberid),"data")
        await ctx.respond(f"Your background has been set to {BG[3]}")
    elif name.lower() == BG[4]:
        WriteSQL("Background",'"Assets/Backgrounds/BG6.png"',str(memberid),"data")
        await ctx.respond(f"Your background has been set to {BG[4]}")
    elif name.lower() == BG[5]:
        WriteSQL("Background",'"Assets/Backgrounds/BG7.png"',str(memberid),"data")
        await ctx.respond(f"Your background has been set to {BG[5]}")
    else:
        await ctx.respond(f"The possible backgrounds are {BG[0]}, {BG[1]}, {BG[2]}, {BG[3]}, {BG[4]}, {BG[5]}")

@client.slash_command(name="font",description="Allows you to set the Font that appears on your stats image")
async def Font(ctx,name="list"):
    Fonts=["hack","pixel","impact","comicsans","combine","gwain-saga"]
    memberid=ctx.author.id
    name = name.lower()
    if name == Fonts[0]:
        WriteSQL("Font",'"Fonts/Hack-Regular.ttf"',str(memberid),"data")
        await ctx.respond(f"Your font has been set to {Fonts[0]}")
    elif name == Fonts[1]:
        WriteSQL("Font",'"Fonts/Power-Green-Regular.ttf"',str(memberid),"data")
        await ctx.respond(f"Your font has been set to {Fonts[1]}")
    elif name == Fonts[2]:
        WriteSQL("Font",'"Fonts/Impact.ttf"',str(memberid),"data")
        await ctx.respond(f"Your font has been set to {Fonts[2]}")
    elif name == Fonts[3]:
        WriteSQL("Font",'"Fonts/Comic-Sans.ttf"',str(memberid),"data")
        await ctx.respond(f"Your font has been set to {Fonts[3]}")
    elif name == Fonts[4]:
        WriteSQL("Font",'"Fonts/Combine.ttf"',str(memberid),"data")
        await ctx.respond(f"Your font has been set to {Fonts[4]}")
    elif name == Fonts[5]:
        WriteSQL("Font",'"Fonts/GwainSaga.ttf"',str(memberid),"data")
        await ctx.respond(f"Your font has been set to {Fonts[5]}")
    else:
        await ctx.respond(f"Available fonts are {Fonts[0]}, {Fonts[1]}, {Fonts[2]}, {Fonts[3]}, {Fonts[5]}, and {Fonts[4]}")

#/help command was reserved so its called /info
#Displays some basic info about the bot, and more detailed info on certain commands
@client.slash_command(name="info",description="/help was taken")
async def info(ctx,arg="default"):
    if arg == "default":
        await ctx.respond("This bot has a few different commands: \n '/stats \n /clearstats \n and /info \n and /Background`")
    elif arg.lower() == "clearstats":
        await ctx.respond("`This command resets your stats and roles to the default values`")
    elif arg.lower() == "background":
        await ctx.respond("`The background command is used to select which background you would like to be displayed on your stat image. \n The available background can be viewed with **/background list**`")
    else:
        await ctx.respond("That command does not have a help entry")


#Sends a message with the stats of a given user
@client.command(name="getinfo")
async def getinfo(ctx,arg=0):
    if ctx.author.id != 367685478226460704:
        await ctx.send("This command is for debugging purposes, use /stats instead")
        return
    if CheckSQLUser(arg) == 0:
        await ctx.send("That user is not in the database")
        return
    print(ctx.author.id)
    CR =ReadSQL(str(arg),"CurrentRole","data")
    M =ReadSQL(str(arg),"Messages","data")
    E =ReadSQL(str(arg),"EXP","data")
    CE =ReadSQL(str(arg),"CurrentEXP","data")
    L =ReadSQL(str(arg),"level","data")
    L=int(L)
    L2 = {15*((10*(4*L))**1.25)}
    Font = ReadSQL(str(arg),"Font","data")
    user = await client.fetch_user(arg)
    await ctx.send(f"{user} font is {Font}")
    await ctx.send(f"{user}'s Current Role is: {CR}")
    await ctx.send(f"{user}'s Current Role `should` be {RoleManagement(str(arg))}")
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
        Messages=ReadSQL(str(ctx.author.id),"Messages","data")
        Messages = int(Messages)+1
        WriteSQL("Messages",Messages,ctx.author.id,"data")
        LevelUp=CalcXP(ctx.author.id,len(message.content))
        

        if LevelUp == 0:
            RoleName=RoleManagement(str(ctx.author.id))
            CurrentRoleName = ReadSQL(str(ctx.author.id),"CurrentRole", "data")
        
        elif LevelUp == 1:
            if ctx.message.author.id in ExcludedUsers:
                return
            print(f"{UpdateTime()} | {ctx.message.author.id} has leveled up!")
            L = ReadSQL(str(ctx.author.id),"level","data")
            
            if Roles == 'True':
                RoleName=RoleManagement(str(ctx.author.id))
                CurrentRoleName = ReadSQL(str(ctx.author.id),"CurrentRole", "data")
                PrevRole = PossibleRoles.index(CurrentRoleName)
                try:
                    await RemoveRole(ctx,CurrentRoleName)
                except:
                    user = await client.fetch_user(ctx.author.id)
                    print(f"{UpdateTime} | Something went wrong when attempting to remove the role {CurrentRoleName} from the user {user.display_name}")
                    await ctx.send("Something went wrong when trying to Modify your role, your role has not been updated")
                try:
                    await AddRole(ctx,RoleName)
                except:
                    user = await client.fetch_user(ctx.author.id)
                    print(f"{UpdateTime} | Something went wrong when attempting to add the role {CurrentRoleName} to the user {user.display_name}")
                    #await ctx.send("Something went wrong when trying to Modify your role, your role has not been updated")
                WriteSQL("CurrentRole",'"'+RoleName+'"',str(ctx.author.id),"data")
                
                #Check for Role changes
                if L == 35 or L == 45 or L == 70 or L == 75 or L == 90 or L == 100:
                    await ctx.send(f":tada: {ctx.message.author} has become a {RoleName}")
            #Check for Excluded channels
            if ctx.channel.id == 803113783777165322:
                ctx = client.get_channel(802021094244089889)

            #Check for Milestone Levels
            if L == 25 or L == 50 or L == 75 or L == 100 or L == 125:
                await ctx.send(f":tada: {ctx.message.author} has reached a milestone level! :tada:")
            
            #Reset ctx
            ctx = await client.get_context(message)
            WriteSQL("CurrentEXP","0",str(ctx.author.id),"data")
            #Save Users Avatar Pic
            AvatarURL = ctx.author.avatar.url
            Avatar = requests.get(AvatarURL, stream = True)
            if Avatar.status_code == 200:
                with open("Assets/Userpic.png",'wb') as f:
                    shutil.copyfileobj(Avatar.raw, f)
            #Create and send level card
            Error = CreateLevelCard(message.author.display_name,message.author.id,RoleName)
            if Error == 1:
                await ctx.send("Something went wrong when creating the image, probably something with your pfp")
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
        WriteSQL("Font",'"Fonts/Hack-Regular.ttf"',str(ctx.author.id),"data")
        RoleName=RoleManagement(str(ctx.author.id))
        WriteSQL("CurrentRole",'"'+RoleName+'"',str(ctx.author.id),"data")
        try:
            await AddRole(ctx,RoleName)
        except:
            print(f"{UpdateTime()} | Something went wrong when when adding a role, exception thrown while initializing a new user")

#Runs the client
client.run(TOKEN)
