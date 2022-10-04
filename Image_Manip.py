from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from MySQL_Functions import ReadSQL

#Draws a variable length line, based on values pulled from the database
def LevelBar(FP,User):
    User=str(User)
    M = ReadSQL(User,"Messages","data")
    L=ReadSQL(User,"level","data")
    E=ReadSQL(User,"CurrentEXP","data")
    E=float(E)
    L=int(L)
    M=int(M)
    img=Image.open(FP)
    MaxLength=img.width-5
    
    #Range is between 5 pixels and MaxLength variable
    #ETOP is equal to how the max amount of EXP before leveling up
    #E is current EXP
    #MaxLength is the maximum length the bar can be drawn
    ETOP=15*((10*(4*L))**1.25)
    E=E/ETOP*100
    draw=ImageDraw.Draw(img)
    MaxLength = E/100*MaxLength

    draw.rectangle((5,225,img.width-5,225),outline="grey",width=3)
    if ReadSQL(str(User),"Background","data") == "Assets/Backgrounds/BG7.png" or ReadSQL(str(User),"Background","data") == "Assets/Backgrounds/BG8.png"  or ReadSQL(str(User),"Background","data") == "Assets/Backgrounds/BG6.png":
        draw.rectangle((5,225,MaxLength,225),outline="black",width=3)
    else:
        draw.rectangle((5,225,MaxLength,225),outline="white",width=3)
    img.save("Assets/Usercard.png")

#Crops a given image down to 128x128
def SquareCrop(FP):
    img=Image.open(FP)
    img.thumbnail((128,128),Image.ANTIALIAS)
    w,h=img.size
    left = (w - 127)/2
    top = (h - 127)/2
    right = (w + 127)/2
    bottom = (h + 127)/2

    # Crop the center of the image
    img = img.crop((left, top, right, bottom))
    img.save(FP)

#Pastes a image onto a background, background is controlled by FP (file path)
def LevelCardComposite(FP,offset,User):
    img=Image.open(FP)
    img_w, img_h = img.size
    BGPATH=ReadSQL(str(User),"Background","data")
    background = Image.open(BGPATH)
    bg_w, bg_h = background.size
    if has_transparency(FP)==False:
        img.convert("RGBA")
        img.putalpha(255)
    background.convert("RGBA")
    background.putalpha(255)
    try:
        background.paste(img,offset,img)
    except:
        img=Image.open("Assets/Fallback.png")
        background.paste(img,offset,img)
        background.save('Assets/Usercard.png')
    background.save('Assets/Usercard.png')

#Draws text on top of a image, in path FP, RGB arguments control color
def DrawText(FP,Offset,Text,size,R,G,B,Font):
    img=Image.open(FP)
    Drawer=ImageDraw.Draw(img)
    CustomFont=ImageFont.truetype(Font, size)
    Drawer.text(Offset,Text,font=CustomFont,fill=(R,G,B))
    img.save(FP)

#Modifies the brightness of an image
def ModBrightness(FP,Factor):
    img2=ImageEnhance.Brightness(Image.open(FP))
    img2_output=img2.enhance(Factor)
    img2_output.save(FP)

#Checks if an image has alpha mask
def has_transparency(FP):
    img = Image.open(FP).convert("RGBA")
    alpha_range = img.getextrema()[-1]
    #if true image is not transparent
    if alpha_range == (255,255):
        return False
    else:
        return True

def CreateStatCard(User,UserID,Role="You shouldnt see this"):
    #Sets the correct text color for different backgrounds
    if ReadSQL(str(UserID),"Background","data") == "Assets/Backgrounds/BG7.png" or ReadSQL(str(UserID),"Background","data") == "Assets/Backgrounds/BG8.png"  or ReadSQL(str(UserID),"Background","data") == "Assets/Backgrounds/BG6.png":
        R=0
        G=0
        B=0
    else:
        R=255
        G=255
        B=255
    
    SquareCrop("Assets/Userpic.png")
    Error = LevelCardComposite("Assets/Userpic.png",(0,50),UserID)
    E=ReadSQL(str(UserID),"EXP","data")
    L=ReadSQL(str(UserID),"level","data")
    M = ReadSQL(str(UserID),"Messages","data")
    CE=ReadSQL(str(UserID),"CurrentEXP","data")
    L=int(L)
    E=float(E)
    M=int(M)
    CE=float(CE)
    EN=15*((10*(4*L))**1.25)
    EN=round(EN,2)
    Font=ReadSQL(str(UserID),"Font","data")
    DrawText("Assets/Usercard.png",(5,200),f"Current EXP: {round(CE,2)} out of {EN}",20,R,G,B,Font)
    DrawText("Assets/Usercard.png",(5,230),f"Global EXP: {round(E)}",20,R,G,B,Font)
    DrawText("Assets/Usercard.png",(125,85),str(L),75,R,G,B,Font)
    DrawText("Assets/Usercard.png",(5,5),f"{User} | {Role}",20,R,G,B,Font)
    LevelBar("Assets/Usercard.png",UserID)
    return Error

def CreateLevelCard(User,UserID,Role="You shouldnt see this"):
    #Sets the correct text color for different backgrounds
    if ReadSQL(str(UserID),"Background","data") == "Assets/Backgrounds/BG7.png" or ReadSQL(str(UserID),"Background","data") == "Assets/Backgrounds/BG8.png" or ReadSQL(str(UserID),"Background","data") == "Assets/Backgrounds/BG6.png":
        R=0
        G=0
        B=0
    else:
        R=255
        G=255
        B=255
    E=ReadSQL(str(UserID),"EXP","data")
    L=ReadSQL(str(UserID),"level","data")
    M = ReadSQL(str(UserID),"Messages","data")
    CE=ReadSQL(str(UserID),"CurrentEXP","data")
    CE=float(CE)
    E=float(E)
    M=int(M)
    Font=ReadSQL(str(UserID),"Font","data")
    EN=15*((10*(4*L))**1.25)
    SquareCrop("Assets/Userpic.png")
    Error = LevelCardComposite("Assets/Userpic.png",(0,50),UserID)
    DrawText("Assets/Usercard.png",(5,200),f"{User} has leveled up!",20,R,G,B,Font)
    DrawText("Assets/Usercard.png",(5,230),f"Current EXP: {round(CE,2)} out of {round(EN,2)}",20,R,G,B,Font)
    DrawText("Assets/Usercard.png",(125,85),str(L),75,R,G,B,Font)
    LevelBar("Assets/Usercard.png",UserID)
    DrawText("Assets/Usercard.png",(5,5),f"{Role}",20,R,G,B,Font)
