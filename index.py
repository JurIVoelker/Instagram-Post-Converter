from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL.ExifTags import TAGS
import math
import glob
import os
import json

### Code ###

# Methods
def loadDefaultSettings():
    """
    Loads Default Values
    """

    # Background Image Effects
    BLUR_RADIUS = 15
    BRIGHTNESS = 0.7

    # Layout settings
    MARGIN_LEFT = 75 # distance of every left aligned item to the right left
    MARGIN_RIGHT = 1080 - MARGIN_LEFT # [Do not edit value] distance of every right aligned item to the right side
    MARGIN_TOP = 300 # move everything by y-Axis
    ITEM_SPACING = 110 # distance between every item

    # Font settings
    FONT_FAMILY = "resources/LGC.ttf"
    FONT_SIZE = 55
    FONT_RGB_VALUE = (255,255,255)

    # Lens metadata finder
    LENS_RENAME = [("TAMRON 35-150mm F/2.8-4.0 Di VC OSD A043", "Tamron 35-150mm F/2.8-4"), ("TAMRON 17-35mm F/2.8-4 Di OSD A037", "Tamron 17-35mm F/2.8-4"), ("20.7 mm", "DJI Mini 2")]
    CAMERA_RENAME = [["FC7303", "DJI Mini 2"]]
    return BLUR_RADIUS, BRIGHTNESS, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, ITEM_SPACING, FONT_FAMILY, FONT_SIZE, FONT_RGB_VALUE, LENS_RENAME, CAMERA_RENAME

def checkResolution(i):
    """
    Checks if image needs to be extendet to fit 4x5 aspect ratio
    """
    print(i.size)
    if i.size[0] > i.size[1]:
        bg = Image.new('RGB', (1080, 1350), (35, 35, 35))
        bg.paste(i, (0, 1350//2 - int(i.size[1]/2)))
        return bg
    else:
        return i

def imageSetup(i, blurRadius, brightness):
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
        width = font.getsize(text)[0]
    draw.text((position[0] - width, position[1]), text, color, font=font, align=align)
    
    return i

def readMetadata(i):
    global err
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
        print(lens)
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

def main(i): 
    """
    Main Function takes img name as parameter, edits and saves image 
    """
    # Open image
    img = Image.open(i)
    
    # get all needed metadata
    camera, lens, shutter, aperture, iso, zoom = readMetadata(img)

    # Save image to correct aspect ratio if needed
    img = checkResolution(img)

    # Save image to new location
    img.save("finished/" + i)

    # Blur Background and lower Exposure
    img = imageSetup(img, BLUR_RADIUS, BRIGHTNESS)

    # Paste Metadata
    img = writeText(img, camera, (MARGIN_RIGHT, MARGIN_TOP + ITEM_SPACING * 0), FONT_RGB_VALUE, "right") # Camera
    img = writeText(img, lens, (MARGIN_RIGHT, MARGIN_TOP + ITEM_SPACING * 1), FONT_RGB_VALUE, "right") # Lens

    # Draw Seperator between <Camera|Lens> and Settings
    line = ImageDraw.Draw(img)  
    x, y, w, h = MARGIN_LEFT, MARGIN_TOP + ITEM_SPACING * 2, MARGIN_RIGHT, 3
    corrector = 45
    line.rectangle([(x, y + corrector), (w, y - h + corrector)], fill ="#ffffff")

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

    img.save("finished/" + i[0:len(i) - 4] + "-finished.jpg")


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

    # Load Lens metadata finder
    LENS_RENAME = data.get("LENS_RENAME")
    CAMERA_RENAME = data.get("CAMERA_RENAME")
except:
    input("Loading settings from \"resources/config.json\" file failed! Please redownload file or try to fix it yourself! \n\n Using default values now. Press [ENTER] to continue!")
    BLUR_RADIUS, BRIGHTNESS, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, ITEM_SPACING, FONT_FAMILY, FONT_SIZE, FONT_RGB_VALUE, LENS_RENAME, CAMERA_RENAME = loadDefaultSettings()

font = ImageFont.truetype(FONT_FAMILY, FONT_SIZE) # Font family and font size
err = False

# Find every file with .jpg / .png ending
jpgFiles = glob.glob('*.jpg')
jpgFiles.append(glob.glob('*.png'))

# Run programme with every file in folder
for f in jpgFiles:
    print(f)
    main(f)
    os.remove(f)

# If metadata is missing on one or more items
if err:
    input("An error has occured on one or more items. Please check them individually!")