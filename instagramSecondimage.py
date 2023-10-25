from tkinter import *
from tkinter import filedialog
import math
from PIL import ImageTk, Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import json
import webbrowser
import os

# Basic settings
root = Tk()
root.title("Instagram image converter")
posx, posy = (root.winfo_screenwidth()-500)//2, (root.winfo_screenheight()-700)//2
root.geometry("500x700+"+str(posx)+"+"+str(posy))
root.resizable(0, 0)

# Button events
def browseFiles():
    global fileList
    root.filenames = filedialog.askopenfilenames(initialdir="/", title="Select the images to be converted", filetypes=(("jpg files", "*.jpg"), ("jpeg files", "*.jpeg")))
    for f in root.filenames:
        if f not in fileList:
            fileList.append(f)
    renderFileList()

def convertImages():
    global fileList
    if loadSettings():
        print("Settings loaded successfully")
        for i in range(len(fileList)):
            processImage(fileList[i])
            listEntrys[i][1].config(bg="green")
            listEntrys[i][2].destroy()
        fileList = []
        webbrowser.open("\\finished")
    else:
        alert = Tk()
        alert.title("Alert")
        alert.geometry("300x100")
        Label(alert, text="\"./ressources/config.json\" file broken.").pack()
        Label(alert, text="Please redownload the file.").pack()     

def settings():
    os.system(f'python {"settings.py"}')

def deleteEntry(i):
    global fileList
    fileList.remove(listEntrys[i][0])
    renderFileList()

def writeJson(dictSetting, value):
    with open('resources/config.json', 'r') as f:
        data = json.load(f)
    f.close()

    data[dictSetting] = value

    with open('resources/config.json', "w") as outfile:
        json.dump(data, outfile)
    outfile.close()

# Programme methods
def renderFileList():
    global listEntrys
    destroyAllEntrys()

    for i in range(len(fileList)):
        l = Label(wrapper, text=extractFileName(fileList[i]), bg=checkCompatibility(fileList[i]), anchor="w", justify="left", width=61)
        l.grid(row=i, column=0)
        d = Button(wrapper, text="delete", bg="lightgray", fg="red", command=lambda i=i: deleteEntry(i))
        d.grid(row=i, column=1, sticky=E)
        
        listEntrys.append([fileList[i], l, d])

def destroyAllEntrys():
    global listEntrys
    for i in listEntrys:
        i[1].destroy()
        i[2].destroy()
    listEntrys = []

def extractFileName(l):
    l = l.split("/")
    return l[-1]

def checkCompatibility(image):
    img = Image.open(image)
    b, l, c = containsMetadata(img)
    if(b):
        checkCameraLensRegistration(l,c)
        return "lightgreen"
    else:
        return "red"

def checkCameraLensRegistration(c, l):
    
    isRegistered = False
    for i in LENS_RENAME:
        if l == i[0]:
            isRegistered = True
            break
    if isRegistered == False:
        LENS_RENAME.append([l,l])

    
    isRegistered = False
    for i in CAMERA_RENAME:
        if c == i[0]:
            isRegistered = True
            break
    if isRegistered == False:
        CAMERA_RENAME.append([c,c])

    writeJson("LENS_RENAME", LENS_RENAME)
    writeJson("CAMERA_RENAME", CAMERA_RENAME)



# Calculation methods
def containsMetadata(image):
    exif = image._getexif()
    try:
        model = str(exif.get(272)) # Camera Model
        lens = str(exif.get(42036)) # Lens
        aperture = (int(math.sqrt(math.pow(2, exif.get(37378)))*10))/10 # Aperture
        if float(int(aperture)) != aperture and str(aperture)[-1] == "9":
            aperture = int(aperture) + 1
        zoom = str(int(exif.get(37386))) + "mm" # Focal lenght
        iso = str(exif.get(34855)) # Iso
        shutter = math.pow(2, exif.get(37377)) # Shutter speed
        return True, model, lens
    except:
        return False, "error", "error"

def loadSettings():
    global BLUR_RADIUS, BRIGHTNESS,MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, ITEM_SPACING, FONT_RGB_VALUE, FONT, LENS_RENAME, CAMERA_RENAME
    try: 
        with open('resources/config.json', 'r') as f:
            data = json.load(f)

        # Load Image Effects
        BLUR_RADIUS = data.get("BLUR_RADIUS")
        BRIGHTNESS = data.get("BRIGHTNESS")

        # Load Layout settings
        MARGIN_LEFT = data.get("MARGIN_LEFT") # distance of every left aligned item to the right left
        MARGIN_RIGHT = 1080 - MARGIN_LEFT # [Do not edit value] distance of every right aligned item to the right side
        MARGIN_TOP = data.get("MARGIN_TOP") # move everything by y-Axis
        ITEM_SPACING = data.get("ITEM_SPACING") # distance between every item

        # Load Font settings
        FONT_FAMILY = data.get("FONT_FAMILY")
        FONT_SIZE = data.get("FONT_SIZE")
        FONT_RGB_VALUE = tuple(data.get("FONT_RGB_VALUE"))
        FONT = ImageFont.truetype(FONT_FAMILY, FONT_SIZE) # Font family and font size

        # Load Lens metadata finder
        LENS_RENAME = data.get("LENS_RENAME")
        CAMERA_RENAME = data.get("CAMERA_RENAME")
        return True
    except:
        return False

def readMetadata(i):
    """
    Reads Metadata from exif and converts aperture and shutterspeed to the right values. 
    Also adds 1/s to shutter, F/ to Aperture and mm to zoom
    Removes .0: F/7.0 --> F/7 
    Rounds up value if it's not calulated correctly
    returns model, lens, shutter, aperture, iso, zoom
    """
    exif = i._getexif()

    try:
        model = str(exif.get(272)) # Camera Model
        lens = str(exif.get(42036)) # Lens
        aperture = (int(math.sqrt(math.pow(2, exif.get(37378)))*10))/10 # Aperture
        if float(int(aperture)) != aperture and str(aperture)[-1] == "9":
            aperture = int(aperture) + 1
        zoom = str(int(exif.get(37386))) + "mm" # Focal lenght
        iso = str(exif.get(34855)) # Iso
        shutter = math.pow(2, exif.get(37377)) # Shutter speed
    except: # If one value could not be calculated
        err = True
        model = "error, no metadata found"
        lens = "error, no metadata found"
        aperture = "error, no metadata found"
        zoom = "error, no metadata found"
        iso = "error, no metadata found"
        shutter = "error, no metadata found"

    for r in LENS_RENAME:
        if (lens == r[0]):
            lens = r[1]
            break

    for r in CAMERA_RENAME:
        if (model == r[0]):
            model = r[1]
            break

    if(shutter <= 1):
        if round(shutter, 4) == 0.0333:
            shutter = "30"
        elif round(shutter, 4) == 0.04:
            shutter = "25"
        elif round(shutter, 4) == 0.05:
            shutter = "20"
        elif round(shutter, 4) == 0.0667:
            shutter = "15"
        elif round(shutter, 4) == 0.0769:
            shutter = "13"
        elif round(shutter, 4) == 0.1:
            shutter = "10"
        elif round(shutter, 4) == 0.125:
            shutter = "8"
        elif round(shutter, 4) == 0.1667:
            shutter = "6"
        elif round(shutter, 4) == 0.2:
            shutter = "5"
        elif round(shutter, 4) == 0.25:
            shutter = "4"
        elif round(shutter, 4) == 0.3125:
            shutter = "3.2"
        elif round(shutter, 4) == 0.4000:
            shutter = "2.5"
        elif round(shutter, 4) == 0.5:
            shutter = "2"
        elif round(shutter, 4) == 0.625:
            shutter = "1.6"
        elif round(shutter, 4) == 0.7692:
            shutter = "1.3"
        elif round(shutter, 4) == 1.0:
            shutter = "1"
    else:
        shutter = "1/" + str(int(round(shutter, 0)))

    shutter = str(shutter)+"s"
    
    if float(int(aperture) == aperture):
        aperture = int(aperture)
    aperture = "F/"+str(aperture)

    return model, lens, shutter, aperture, iso, zoom

def checkResolution(i):
    """
    Checks if image needs to be extended to fit 4x5 aspect ratio
    """
    if i.size[0] != 1080:
        i = i.resize(resizeResolution(i.size[0], i.size[1]))
    if i.size[0] > i.size[1]:
        bg = Image.new('RGB', (1080, 1350), (35, 35, 35))
        bg.paste(i, (0, 1350//2 - int(i.size[1]/2)))
        return bg
    else:
        return i

def resizeResolution(w, h):
    ratio = h / w
    new_width = 1080
    new_height = int(new_width * ratio)
    return (new_width, new_height)

def blurImage(i, blurRadius, brightness):
    """ 
    Blurs and lowers the brightness of the image by <blurRadius> and <brightness>
    """

    # Blur image
    i = i.filter(ImageFilter.GaussianBlur(radius = blurRadius))

    # Reduce brightness of image
    enhancer = ImageEnhance.Brightness(i)
    i = enhancer.enhance(brightness)

    return i

def writeText(i, text, position, color, align):
    """
    Writes Text <text> on image <i>, at position <position> with color <color> and aligned to <align>
    """
    draw = ImageDraw.Draw(i)
    width = 0
    if align == "right":
        width = FONT.getsize(text)[0]
    draw.text((position[0] - width, position[1]), text, color, font=FONT, align=align)
    
    return i

def processImage(i):
    # Open image
    img = Image.open(i)
    
    # get all needed metadata
    camera, lens, shutter, aperture, iso, zoom = readMetadata(img)

    # Save image to correct aspect ratio if needed
    img = checkResolution(img)

    # Save image to new location
    img.save("finished/" + extractFileName(i))

    # Blur Background and lower Exposure
    img = blurImage(img, BLUR_RADIUS, BRIGHTNESS)

    # Paste Metadata
    img = writeText(img, camera, (MARGIN_RIGHT, MARGIN_TOP + ITEM_SPACING * 0), FONT_RGB_VALUE, "right") # Camera
    img = writeText(img, lens, (MARGIN_RIGHT, MARGIN_TOP + ITEM_SPACING * 1), FONT_RGB_VALUE, "right") # Lens

    # Draw Seperator between <Camera|Lens> and Settings
    line = ImageDraw.Draw(img)  
    x, y, w, h = MARGIN_LEFT, MARGIN_TOP + ITEM_SPACING * 2, MARGIN_RIGHT, 3
    corrector = 45
    print((x, y + corrector), " ", (w, y - h + corrector))
    line.rectangle([(x, y + corrector), (w, y + h + corrector)], fill ="#ffffff")

    # Paste Metadata
    img = writeText(img, "ISO", (MARGIN_LEFT, MARGIN_TOP + ITEM_SPACING * 3), FONT_RGB_VALUE, "left") # Iso
    img = writeText(img, iso, (MARGIN_RIGHT, MARGIN_TOP + ITEM_SPACING * 3), FONT_RGB_VALUE, "right")
    img = writeText(img, "Shutter Speed", (MARGIN_LEFT, MARGIN_TOP + ITEM_SPACING * 4), FONT_RGB_VALUE, "left") # Shutterspeed
    img = writeText(img, shutter, (MARGIN_RIGHT, MARGIN_TOP + ITEM_SPACING * 4), FONT_RGB_VALUE, "right")
    img = writeText(img, "Aperture", (MARGIN_LEFT, MARGIN_TOP + ITEM_SPACING * 5), FONT_RGB_VALUE, "left") # Aperture
    img = writeText(img, aperture, (MARGIN_RIGHT, MARGIN_TOP + ITEM_SPACING * 5), FONT_RGB_VALUE, "right")
    img = writeText(img, "Zoom", (MARGIN_LEFT, MARGIN_TOP + ITEM_SPACING * 6), FONT_RGB_VALUE, "left") # Zoom
    img = writeText(img, zoom, (MARGIN_RIGHT, MARGIN_TOP + ITEM_SPACING * 6), FONT_RGB_VALUE, "right")

    # Open Camera and Lens Icon
    cameraIcon = Image.open("resources/camera.png") # 100x100px
    lensIcon = Image.open("resources/lens.png") # 100x100px

    # paste Camera and Lens Icon
    img.paste(cameraIcon, (MARGIN_LEFT, MARGIN_TOP + ITEM_SPACING * 0 - 15), cameraIcon)
    img.paste(lensIcon, (MARGIN_LEFT, MARGIN_TOP + ITEM_SPACING * 1 - 15), lensIcon)

    img.save("finished/" + extractFileName(i[0:len(i) - 4]) + "-finished.jpg")

fileList = []
listEntrys = []

loadSettings()

wrapper = LabelFrame(root,bg="lightgray")
wrapper.pack(fill="both", expand="yes", padx=10, pady=10)

browseFilesButton = Button(root, text="Browse files", command=browseFiles, width=28)        .pack(side=LEFT,  padx=(15,7.5), pady=(0,15))

convertImagesButton = Button(root, text="Convert Images", command=convertImages, width=28)  .pack(side=LEFT,  padx=7.5,      pady=(0,15))

settingsIcon = PhotoImage(file="resources/settings.png").subsample(4,4)
settingsButton = Button(root, image=settingsIcon, command=settings, width=22, height=22)    .pack(side=RIGHT, padx=(7.5,15), pady=(0,15))

root.mainloop()
