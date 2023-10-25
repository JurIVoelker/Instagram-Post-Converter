from tkinter import *
from tkinter import filedialog
import math
from PIL import ImageTk, Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import json
import webbrowser
import os


# Blur Radius
# Brightness
# Margin Left
# Margin Top
# Item_spacing
# Font Family
# Font Size
# Font RGB Value
# Lens Rename
# Camera Name

# Basic settins
settings = Tk()
settings.title("Settings")
posx, posy = (settings.winfo_screenwidth() - 500) // 2, (
    settings.winfo_screenheight() - 700
) // 2
settings.geometry("500x700+" + str(posx + 502) + "+" + str(posy))
settings.resizable(0, 0)

# Methods


def writeJson(dictSetting, value):
    with open("resources/config.json", "r") as f:
        data = json.load(f)
    f.close()

    data[dictSetting] = value

    with open("resources/config.json", "w") as outfile:
        json.dump(data, outfile)
    outfile.close()


def validateInteger(inpt):
    try:
        intInpt = int(inpt)
        if str(intInpt) == inpt and intInpt >= 0:
            return True
        else:
            return False
    except:
        return False


def validateFloat(inpt):
    try:
        floatInpt = float(inpt)
        if str(floatInpt) == inpt and floatInpt > 0 and floatInpt <= 1:
            return True
        else:
            return False
    except:
        return False


def validateRGB(inpt):
    try:
        l = inpt.split(",")
        print(l)
        if l[0][0] == "(" and l[2][-1] == ")":
            print(l[0][1:])
            print(l[1])
            print(l[2][:-1])
            if (
                validateInteger(l[0][1:])
                and validateInteger(l[1])
                and validateInteger(l[2][:-1])
                and int(l[0][1:]) <= 255
                and int(l[0][1:]) >= 0
                and int(l[1]) <= 255
                and int(l[1]) >= 0
                and int(l[2][:-1]) <= 255
                and int(l[2][:-1]) >= 0
            ):
                return True
            else:
                return False
        else:
            return False

    except:
        return False


def loadSettings():
    global BLUR_RADIUS, BRIGHTNESS, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, FONT_SIZE, ITEM_SPACING, FONT_FAMILY, FONT_RGB_VALUE, FONT, LENS_RENAME, CAMERA_RENAME
    try:
        with open("resources/config.json", "r") as f:
            data = json.load(f)

        # Load Image Effects
        BLUR_RADIUS = data.get("BLUR_RADIUS")
        BRIGHTNESS = data.get("BRIGHTNESS")

        # Load Layout settings
        MARGIN_LEFT = data.get(
            "MARGIN_LEFT"
        )  # distance of every left aligned item to the right left
        MARGIN_RIGHT = (
            1080 - MARGIN_LEFT
        )  # [Do not edit value] distance of every right aligned item to the right side
        MARGIN_TOP = data.get("MARGIN_TOP")  # move everything by y-Axis
        ITEM_SPACING = data.get("ITEM_SPACING")  # distance between every item

        # Load Font settings
        FONT_FAMILY = data.get("FONT_FAMILY")
        FONT_SIZE = data.get("FONT_SIZE")
        FONT_RGB_VALUE = tuple(data.get("FONT_RGB_VALUE"))
        FONT = ImageFont.truetype(FONT_FAMILY, FONT_SIZE)  # Font family and font size

        # Load Lens metadata finder
        LENS_RENAME = data.get("LENS_RENAME")
        CAMERA_RENAME = data.get("CAMERA_RENAME")
        return True
    except:
        return False


# Button events


def saveBlurRadius():
    value = blurEntry.get()
    if validateInteger(value):
        writeJson("BLUR_RADIUS", int(value))
        blurLabel.config(text="Blur radius (whole number): " + blurEntry.get())
    else:
        print("alert")
    blurEntry.delete(0, END)


def saveBrightness():
    value = brightnessEntry.get()
    if validateFloat(value):
        writeJson("BRIGHTNESS", float(value))
        brightnessLabel.config(
            text="Brightness (Number between 1 and 0): " + brightnessEntry.get()
        )
    else:
        print("alert")
    brightnessEntry.delete(0, END)


def saveMarginLeft():
    value = marginLeftEntry.get()
    if validateInteger(value):
        writeJson("MARGIN_LEFT", int(value))
        marginLeftLabel.config(
            text="Margin left (whole number): " + marginLeftEntry.get()
        )
    else:
        print("alert")
    marginLeftEntry.delete(0, END)


def saveMarginTop():
    value = marginTopEntry.get()
    if validateInteger(value):
        writeJson("MARGIN_TOP", int(value))
        marginTopLabel.config(text="Margin top (whole number): " + marginTopEntry.get())
    else:
        print("alert")
    marginTopEntry.delete(0, END)


def saveItemSpacing():
    value = itemSpacingEntry.get()
    if validateInteger(value):
        writeJson("ITEM_SPACING", int(value))
        itemSpacingLabel.config(
            text="Item spacing (whole number): " + itemSpacingEntry.get()
        )
    else:
        print("alert")
    itemSpacingEntry.delete(0, END)


def browseFontFamily():
    settings.filenames = filedialog.askopenfilenames(
        initialdir="/",
        title="Select the images to be converted",
        filetypes=(("True Type Font", "*.ttf"), ("True Type Font", "*.ttf")),
    )
    try:
        if settings.filenames[0] != "":
            writeJson("FONT_FAMILY", settings.filenames[0])
            fontFamilyLabel.config(
                text="Font family (Truetype): " + settings.filenames[0].split("/")[-1]
            )
    except:
        print("alert")


def saveFontSize():
    value = fontSizeEntry.get()
    if validateInteger(value):
        writeJson("FONT_SIZE", int(value))
        fontSizeLabel.config(text="Font size (whole number): " + fontSizeEntry.get())
    else:
        print("alert")
    fontSizeEntry.delete(0, END)


def saveFontRGB():
    value = fontRGBEntry.get()
    if validateRGB(value):
        v = value.split(",")
        value = [int(v[0][1:]), int(v[1]), int(v[2][:-1])]
        writeJson("FONT_RGB_VALUE", value)
        fontRGBLabel.config(text="Font Color (RGB): " + fontRGBEntry.get())
    else:
        print("alert")
    fontRGBEntry.delete(0, END)


def saveLensModel(i):
    value = renameList[i][1].get()
    if value != "":
        print(LENS_RENAME)
        LENS_RENAME[i] = [renameList[i][0].cget("text"), value]  #
        print(LENS_RENAME)
        writeJson("LENS_RENAME", LENS_RENAME)
    else:
        print("alert")


def saveCameraModel(i):
    value = renameList[i][1].get()
    if value != "":
        CAMERA_RENAME[i - rows + 1] = [renameList[i][0].cget("text"), value]
        writeJson("CAMERA_RENAME", CAMERA_RENAME)
    else:
        print("alert")


# Main
settings.grid_rowconfigure(0, weight=1)
settings.columnconfigure(0, weight=1)
loadSettings()

PADY = 5
WIDTH = 20

# Blur Radius
blurLabel = Label(
    settings, text="Blur radius (whole number): " + str(BLUR_RADIUS), anchor="w"
)
blurLabel.grid(row=0, column=0, sticky="nw", padx=10, pady=PADY)
blurEntry = Entry(settings, width=WIDTH)
blurEntry.grid(row=0, column=1, sticky="nw", padx=10, pady=PADY)
blurSave = Button(settings, text="Save", width=10, command=saveBlurRadius)
blurSave.grid(row=0, column=2, sticky="nw", pady=PADY - 3, padx=(5, 15))

# Brightness
brightnessLabel = Label(
    settings, text="Brightness (Number between 1 and 0): " + str(BRIGHTNESS), anchor="w"
)
brightnessLabel.grid(row=1, column=0, sticky="nw", padx=10, pady=PADY)
brightnessEntry = Entry(settings, width=WIDTH)
brightnessEntry.grid(row=1, column=1, sticky="nw", padx=10, pady=PADY)
brightnessSave = Button(settings, text="Save", width=10, command=saveBrightness)
brightnessSave.grid(row=1, column=2, sticky="nw", pady=PADY - 3, padx=(5, 15))

# Margin Left
marginLeftLabel = Label(
    settings, text="Margin left (whole number): " + str(MARGIN_LEFT), anchor="w"
)
marginLeftLabel.grid(row=2, column=0, sticky="nw", padx=10, pady=PADY)
marginLeftEntry = Entry(settings, width=WIDTH)
marginLeftEntry.grid(row=2, column=1, sticky="nw", padx=10, pady=PADY)
marginLeftSave = Button(settings, text="Save", width=10, command=saveMarginLeft)
marginLeftSave.grid(row=2, column=2, sticky="nw", pady=PADY - 3, padx=(5, 15))

# Margin Top
marginTopLabel = Label(
    settings, text="Margin top (whole number): " + str(MARGIN_TOP), anchor="w"
)
marginTopLabel.grid(row=3, column=0, sticky="nw", padx=10, pady=PADY)
marginTopEntry = Entry(settings, width=WIDTH)
marginTopEntry.grid(row=3, column=1, sticky="nw", padx=10, pady=PADY)
marginTopSave = Button(settings, text="Save", width=10, command=saveMarginTop)
marginTopSave.grid(row=3, column=2, sticky="nw", pady=PADY - 3, padx=(5, 15))

# Item_spacing
itemSpacingLabel = Label(
    settings, text="Item spacing (whole number): " + str(ITEM_SPACING), anchor="w"
)
itemSpacingLabel.grid(row=4, column=0, sticky="nw", padx=10, pady=PADY)
itemSpacingEntry = Entry(settings, width=WIDTH)
itemSpacingEntry.grid(row=4, column=1, sticky="nw", padx=10, pady=PADY)
itemSpacingSave = Button(settings, text="Save", width=10, command=saveItemSpacing)
itemSpacingSave.grid(row=4, column=2, sticky="nw", pady=PADY - 3, padx=(5, 15))

# Font Family
fontFamilyLabel = Label(
    settings, text="Font family (Truetype): " + FONT_FAMILY.split("/")[-1], anchor="w"
)
fontFamilyLabel.grid(row=5, column=0, sticky="nw", padx=10, pady=PADY, columnspan=2)
fontFamilySave = Button(
    settings, text="Browse File", width=10, command=browseFontFamily
)
fontFamilySave.grid(row=5, column=2, sticky="nw", pady=PADY - 3, padx=(5, 15))

# Font Size
fontSizeLabel = Label(
    settings, text="Font size (whole number): " + str(FONT_SIZE), anchor="w"
)
fontSizeLabel.grid(row=6, column=0, sticky="nw", padx=10, pady=PADY)
fontSizeEntry = Entry(settings, width=WIDTH)
fontSizeEntry.grid(row=6, column=1, sticky="nw", padx=10, pady=PADY)
fontSizeSave = Button(settings, text="Save", width=10, command=saveFontSize)
fontSizeSave.grid(row=6, column=2, sticky="nw", pady=PADY - 3, padx=(5, 15))

# Font RGB Value
fontRGBLabel = Label(
    settings, text="Font Color (RGB): " + str(FONT_RGB_VALUE), anchor="w"
)
fontRGBLabel.grid(row=7, column=0, sticky="nw", padx=10, pady=PADY)
fontRGBEntry = Entry(settings, width=WIDTH)
fontRGBEntry.grid(row=7, column=1, sticky="nw", padx=10, pady=PADY)
fontRGBSave = Button(settings, text="Save", width=10, command=saveFontRGB)
fontRGBSave.grid(row=7, column=2, sticky="nw", pady=PADY - 3, padx=(5, 15))

# Camera and Lens Rename
frame_main = Frame(settings)
frame_main.grid(sticky="news", columnspan=3)
frame_canvas = Frame(frame_main)
frame_canvas.grid(row=2, column=0, pady=(5, 0), sticky="nw")
frame_canvas.grid_rowconfigure(0, weight=1)
frame_canvas.grid_columnconfigure(0, weight=1)
frame_canvas.grid_propagate(False)
canvas = Canvas(frame_canvas)
canvas.grid(row=0, column=0, sticky="news")
vsb = Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
vsb.grid(row=0, column=1, sticky="ns")
canvas.configure(yscrollcommand=vsb.set)
frame_buttons = Frame(canvas)
canvas.create_window((0, 0), window=frame_buttons, anchor="nw")
renameList = []
lensesLabel = Label(frame_buttons, text="Lens Rename:")
lensesLabel.grid(row=0, column=0, sticky="w")
rows = 1
for i in range(len(LENS_RENAME)):
    l = Label(
        frame_buttons, text=LENS_RENAME[i][0], width=35, justify="left", anchor="w"
    )
    l.grid(row=i + 1, column=0, sticky="w")
    t = Entry(frame_buttons, width=27)
    t.grid(row=i + 1, column=1, sticky="news")
    t.insert(0, LENS_RENAME[i][1])
    b = Button(
        frame_buttons, text="Save", width=6, command=lambda i=i: saveLensModel(i)
    )
    b.grid(row=i + 1, column=2, sticky="e", padx=(5, 0))
    renameList.append([l, t, b])
    rows += 1
cameraLabel = Label(frame_buttons, text="Camera Rename:")
cameraLabel.grid(row=rows, column=0, sticky="w", pady=(15, 0))
for i in range(len(CAMERA_RENAME)):
    l = Label(
        frame_buttons, text=CAMERA_RENAME[i][0], width=35, justify="left", anchor="w"
    )
    l.grid(row=i + 1 + rows, column=0, sticky="w")
    t = Entry(frame_buttons, width=27)
    t.grid(row=i + 1 + rows, column=1, sticky="news")
    t.insert(0, CAMERA_RENAME[i][1])
    b = Button(
        frame_buttons,
        text="Save",
        width=6,
        command=lambda i=i: saveCameraModel(i + rows - 1),
    )
    b.grid(row=i + 1 + rows, column=2, sticky="e", padx=(5, 0))
    renameList.append([l, t, b])


# Update buttons frames idle tasks to let tkinter calculate buttons sizes
frame_buttons.update_idletasks()

# Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar

frame_canvas.config(width=475 + vsb.winfo_width(), height=447)

# Set the canvas scrolling region
canvas.config(scrollregion=canvas.bbox("all"))

print("Hallo")
# Launch the GUI
settings.mainloop()
