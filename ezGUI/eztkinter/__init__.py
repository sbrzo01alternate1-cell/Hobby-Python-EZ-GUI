import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math
import os
import subprocess
import threading
import time
import gc  # Add at the top of your file if not already imported
import inspect
import threading
import urllib.request
import zipfile
import io

global SaveWindowSize
SaveWindowSize = False
global PreviousTime
PreviousTime = time.time_ns()

global previous_keys_held
previous_keys_held = set()

class rglobals():
    #This is where our global variables are ACTUALLY declared. Not using "global variable", NO!!! It needs a CLASS!
    pass
rglobals.AllSounds = set()

def on_key_press(event):
    rglobals.keys_held.add(event.keysym)

def on_key_release(event):
    if event.keysym in rglobals.keys_held:
        rglobals.keys_held.remove(event.keysym)

# Mouse press/release handlers
def on_press(event):
    if event.num == 1:
        rglobals.mouse_held["left"] = True
        rglobals.mouse_clicked["left"] = True
    elif event.num == 2:
        rglobals.mouse_held["middle"] = True
        rglobals.mouse_clicked["middle"] = True
    elif event.num == 3:
        rglobals.mouse_held["right"] = True
        rglobals.mouse_clicked["right"] = True

def on_release(event):
    if event.num == 1:
        rglobals.mouse_held["left"] = False
        rglobals.mouse_released["left"] = True
    elif event.num == 2:
        rglobals.mouse_held["middle"] = False
        rglobals.mouse_released["middle"] = True
    elif event.num == 3:
        rglobals.mouse_held["right"] = False
        rglobals.mouse_released["right"] = True

def on_close():
    global rglobals
    AllItems = rglobals.AllItems.copy()
    AllSounds = rglobals.AllSounds.copy()
    for item in AllItems:
        item.delete()
    for sound in AllSounds:
        sound.stop()
        sound.delete()
    del AllItems
    del AllSounds
    rglobals.root.destroy()  # properly closes the app
    del rglobals
    gc.collect()
    os._exit(0) #In case python is being STUPID! FORCE TERMINATE!!!
    


class ezWindow():
    def __init__(self,width=0,height=0,background="#d9d9d9",title="unnamed tk window"):
        #Check if width and height are 0, set to previous ones:
        if width == 0 or height == 0:
            if os.path.exists("Saved_Window_Size.txt"):
                with open("Saved_Window_Size.txt", "r", encoding="utf-8") as file:
                    lines = file.read().strip().split("\n")
                    width = lines[0]
                    height = lines[1]
            else:
                width = 100
                height = 100
        #Setup initial window boundaries and stuff, you usually NEVER need to change any of this:
        self.width=width
        self.height=height
        self.background=background
        self.title=title
        rglobals.root = tk.Tk()
        rglobals.root.geometry(f"{self.width}x{self.height}")
        rglobals.canvas = tk.Canvas(rglobals.root, highlightthickness=0,bg=self.background)
        rglobals.canvas.pack(fill="both", expand=True)
        rglobals.root.update_idletasks()
        # Initial square reference stuff:
        rglobals.window_width = rglobals.canvas.winfo_width()
        rglobals.window_height = rglobals.canvas.winfo_height()
        rglobals.previous_window_width = rglobals.window_width
        rglobals.previous_window_height = rglobals.window_height
        rglobals.sq_size = min(rglobals.window_width, rglobals.window_height)
        rglobals.previous_sq_size = rglobals.sq_size
        rglobals.min_rel_size = 0.001
        #To get the maximum rglobals.font_scale:
        rglobals.font_scale = 1 / 71834.6
        rglobals.scroll_x = rglobals.canvas.canvasx(0)
        rglobals.scroll_y = rglobals.canvas.canvasy(0)
        rglobals.previous_scroll_x = rglobals.scroll_x
        rglobals.previous_scroll_y = rglobals.scroll_y
        rglobals.WindowChanged = (rglobals.sq_size != rglobals.previous_sq_size or rglobals.window_height != rglobals.previous_window_height or rglobals.window_width != rglobals.previous_window_width)
        rglobals.ScrollChanged = (rglobals.scroll_x != rglobals.previous_scroll_x or rglobals.scroll_y != rglobals.previous_scroll_y)
        rglobals.x_offset = 0
        rglobals.y_offset = 0
        rglobals.minimum_relx = -20000
        rglobals.maximum_relx = 30000
        rglobals.minimum_rely = -20000
        rglobals.maximum_rely = 30000
        if(rglobals.window_width > rglobals.window_height):
            rglobals.x_offset = int((rglobals.window_width-rglobals.window_height)/2)
        elif(rglobals.window_width < rglobals.window_height):
            rglobals.y_offset = int((rglobals.window_height-rglobals.window_width)/2)
        # ------------------- Keyboard states -------------------
        rglobals.keys_held = set()
        rglobals.keys_clicked = set()
        rglobals.keys_released = set()
        rglobals.root.bind("<KeyPress>", on_key_press)
        rglobals.root.bind("<KeyRelease>", on_key_release)
        # Mouse states
        rglobals.mouse_held = {"left": False, "middle": False, "right": False}
        rglobals.mouse_clicked = {"left": False, "middle": False, "right": False}
        rglobals.mouse_released = {"left": False, "middle": False, "right": False}
        rglobals.root.bind("<ButtonPress>", on_press)
        rglobals.root.bind("<ButtonRelease>", on_release)
        rglobals.AllItems = set()
        rglobals.root.protocol("WM_DELETE_WINDOW", on_close)
        rglobals.root.title(self.title)
    def SetBackground(self,background="#d9d9d9"):
        rglobals.canvas.configure(bg=background)
    def SetSize(self,width=600,height=600):
        rglobals.root.geometry(f"{width}x{height}")
    def SetTitle(self, title):
        self.title = title
        if hasattr(rglobals, "root") and rglobals.root:
            rglobals.root.title(self.title)
    def delete(self):
        # Destroy Tkinter root safely
        if hasattr(rglobals, "root") and rglobals.root:
            try:
                for event in ["<KeyPress>", "<KeyRelease>", "<ButtonPress>", "<ButtonRelease>"]:
                    rglobals.root.unbind(event)
                rglobals.root.destroy()
            except Exception:
                pass
        # Clear all instance attributes
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass
        # Clear rglobals references
        rglobals_vars = [
            "root", "canvas", "window_width", "window_height",
            "previous_window_width", "previous_window_height",
            "sq_size", "previous_sq_size", "min_rel_size", "font_scale",
            "scroll_x", "scroll_y", "previous_scroll_x", "previous_scroll_y",
            "WindowChanged", "ScrollChanged", "x_offset", "y_offset",
            "minimum_relx", "maximum_relx", "minimum_rely", "maximum_rely",
            "keys_held", "keys_clicked", "mouse_held", "mouse_clicked",
            "AllItems"
        ]
        for var in rglobals_vars:
            if hasattr(rglobals, var):
                try:
                    delattr(rglobals, var)
                except Exception:
                    pass
        # Encourage Python to free memory
        gc.collect()
    def __repr__(self):
        ReturnString = "\nThis is an ezWindow object! You typically only need one of these. This creates an easy window!\n"
        ReturnString = ReturnString + "You can create a window with this command:\n"
        ReturnString = ReturnString + "MyezWindow = ezWindow(width=600,height=600,background=\"#d9d9d9\",title=\"unnamed tk window\")\n"
        ReturnString = ReturnString + "The functions are:\n"
        ReturnString = ReturnString + "MyezWindow.SetBackground(self,background=\"#d9d9d9\") This function... sets the background color... pretty obvious...\n"
        ReturnString = ReturnString + "MyezWindow.SetSize(width=600,height=600) This function... sets the size... pretty obvious...\n"
        ReturnString = ReturnString + "MyezWindow.SetTitle(title): This function... sets the title... pretty obvious...\n"
        return ReturnString
    def __repr__(self):
            # Grab default values from the __init__ signature
            defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
            return f"""
This is an ezWindow object! You typically only need one of these. This creates an easy window!
You can create a window with this command:
MyezWindow = ezWindow(width={defaults['width']},height={defaults['height']},background=\"{defaults['background']}\",title=\"{defaults['title']}\")

A lot of this is self explanatory but I'll do it anyway:

width is the width of the window, duh
height is the height of the window, also duh

HOWEVER, if you do not plug in values for width and height, it will use the previous values. If these values do not exist, it will default to 100 width, and 100 height. Resize to save for any screen.

background is the color scheme of the window, kinda important
title is the name of the window title.

Here are the functions you need:

MyezWindow.SetBackground(self,background=\"{defaults['background']}\") This function... sets the background color... pretty obvious...
MyezWindow.SetSize(width={defaults['width']},height={defaults['height']}) This function... sets the size... pretty obvious...
MyezWindow.SetTitle(\"{defaults['title']}\"): This function... sets the title... pretty obvious...



Here are the important variables you'll need. Most of them are rglobals:

rglobals.keys_clicked: these are the current keys that are clicked on the keyboard. Similar to a mouse click. Here are the current values:
rglobals.keys_clicked = {rglobals.keys_clicked}

rglobals.keys_held: These are the most reliable, whatever keys you're holding on the keyboard. Here are the current values:
rglobals.keys_held = {rglobals.keys_held}

rglobals.keys_released: These are the keys you've just released, whatever keys you've released on the keyboard. Here are the current values:
rglobals.keys_released = {rglobals.keys_released}

rglobals.maximum_relx, rglobals.maximum_rely, rglobals.minimum_relx, rglobals.minimum_rely. Once any item is outside these bounds, it will no longer be drawn to save RAM and CPU
rglobals.maximum_relx: {rglobals.maximum_relx}
rglobals.maximum_rely: {rglobals.maximum_rely}
rglobals.minimum_relx: {rglobals.minimum_relx}
rglobals.minimum_rely: {rglobals.minimum_rely}

rglobals.min_rel_size is the minimum drawing size for images and whatever. If an image or something is smaller than this, it will not draw to save RAM and CPU.
rglobals.min_rel_size: {rglobals.min_rel_size}

rglobals.mouse_clicked means if the mouse buttons are clicked a single time:
rglobals.mouse_clicked = {rglobals.mouse_clicked}

rglobals.mouse_held means if the mouse is being held down.
rglobals.mouse_held = {rglobals.mouse_held}

rglobals.mouse_released means if the mouse was released
rglobals.mouse_released = {rglobals.mouse_released}

rglobals.scroll_x, and rglobals.scroll_y, these tell you how much the user scrolled by.
rglobals.scroll_x = {rglobals.scroll_x}
rglobals.scroll_y = {rglobals.scroll_y}

rglobals.sq_size is the size of the smallest side of the window. It is primarily used by me to make sure everything is "relative".
rglobals.sq_size = {rglobals.sq_size}

rglobals.window_height and rglobals.window_width are the pixels width and height of the window. You do not need to worry about these usually.
rglobals.window_height = {rglobals.window_height}
rglobals.window_width = {rglobals.window_width}

rglobals.x_offset and rglobals.y_offset. These variables help me with relative positions. Not necessary.
rglobals.x_offset = {rglobals.x_offset}
rglobals.y_offset = {rglobals.y_offset}
"""

class ezImage():
    def __init__(self, ImagePath, relx=500, rely=500, relwidth=-1, relheight=-1, angle=0, transparency=10000, anchor="nw", scrolling=True, quality=0):
        self.ImagePath = ImagePath
        self.original_img = Image.open(ImagePath).convert("RGBA")
        self.relx = relx
        self.rely = rely
        self.angle = angle
        self.transparency = transparency
        self.anchor = anchor
        self.scrolling = scrolling
        self.previous_anchor = self.anchor
        self.visibility = "normal"
        self.previous_visibility = self.visibility
        self.resized_base = None
        self.rotated_resized = None
        self.tk_img = None
        self.quality = quality
        # Precompute alpha LUTs for 0–100% transparency
        self.alpha_luts = [bytes([int(i * level / 100) for i in range(256)]) for level in range(101)]
        # Choose resampling type based on quality
        try:
            self.resample_type = {
                0: Image.Resampling.NEAREST,
                1: Image.Resampling.BILINEAR,
                2: Image.Resampling.HAMMING,
                3: Image.Resampling.BICUBIC,
                4: Image.Resampling.LANCZOS
            }[self.quality]
        except KeyError:
            print(f"ERROR: the quality can only be 0-4 and you put {self.quality}")
        # Compute initial width/height
        self.original_w, self.original_h = self.original_img.size
        if relwidth >= 0 and relheight >= 0:
            self.relwidth = relwidth
            self.relheight = relheight
        elif relwidth >= 0:
            self.relwidth = relwidth
            self.relheight = max(rglobals.min_rel_size, int((self.original_h / self.original_w) * self.relwidth))
        elif relheight >= 0:
            self.relheight = relheight
            self.relwidth = max(rglobals.min_rel_size, int((self.original_w / self.original_h) * self.relheight))
        else:
            self.relwidth = int((self.original_w * 10000) / rglobals.sq_size)
            self.relheight = int((self.original_h * 10000) / rglobals.sq_size)
        self.new_w = max(1, int((self.relwidth / 10000) * rglobals.sq_size))
        self.new_h = max(1, int((self.relheight / 10000) * rglobals.sq_size))
        # Initial resize
        self.resized_base = self.original_img.resize((self.new_w, self.new_h), self.resample_type)
        # Initial rotation
        self.rotated_resized = self._rotate_image(self.resized_base, self.angle)
        # Apply transparency
        self.tk_img = self._apply_transparency(self.rotated_resized, self.transparency)
        # Previous states
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_angle = self.angle
        self.previous_transparency = self.transparency
        # Create canvas image
        self.image_id = rglobals.canvas.create_image(
            ((self.relx / 10000) * rglobals.sq_size) + rglobals.x_offset,
            ((self.rely / 10000) * rglobals.sq_size) + rglobals.y_offset,
            image=self.tk_img,
            anchor=self.anchor
        )
        rglobals.AllItems.add(self)
    def move(self,XAmount=0,YAmount=0):
        # Get current rglobals.canvas size
        self.relx += XAmount 
        self.rely += YAmount
    def SetPosition(self,relx=0,rely=0):
        # Get current rglobals.canvas size
        self.relx = relx 
        self.rely = rely
    def rotate(self,DegreesToRotate):
        self.angle += DegreesToRotate
    def SetAngle(self,angle):
        self.angle = angle
    def ChangeSize(self, WidthBy=0, HeightBy=0):
        # Get current rglobals.canvas size
        self.relwidth = max(rglobals.min_rel_size, self.relwidth + WidthBy)
        self.relheight = max(rglobals.min_rel_size, self.relheight + HeightBy)
        w = self.relwidth
        h = self.relheight
        self.anchor_offsets = {
            "nw": (0,0),
            "n": (-w/2,0),
            "ne": (-w,0),
            "w": (0,-h/2),
            "center": (-w/2,-h/2),
            "e": (-w,-h/2),
            "sw": (0,-h),
            "s": (-w/2,-h),
            "se": (-w,-h)
        }
    def SetSize(self, relwidth=2500, relheight=2500):
        # Get current rglobals.canvas size
        self.relwidth = max(rglobals.min_rel_size, relwidth)
        self.relheight = max(rglobals.min_rel_size, relheight)
        w = self.relwidth
        h = self.relheight
        self.anchor_offsets = {
            "nw": (0,0),
            "n": (-w/2,0),
            "ne": (-w,0),
            "w": (0,-h/2),
            "center": (-w/2,-h/2),
            "e": (-w,-h/2),
            "sw": (0,-h),
            "s": (-w/2,-h),
            "se": (-w,-h)
        }
    def ChangeRatioWidth(self, WidthBy=2500):
        # ratio = original_h / original_w
        ratio = self.relheight/self.relwidth
        self.relwidth = max(rglobals.min_rel_size, self.relwidth + WidthBy)
        self.relheight = max(rglobals.min_rel_size, int(ratio * self.relwidth))
    def SetRatioWidth(self, relwidth=2500):
        # ratio = original_h / original_w
        ratio = self.relheight/self.relwidth
        self.relwidth = max(rglobals.min_rel_size, relwidth)
        self.relheight = max(rglobals.min_rel_size, int(ratio * self.relwidth))
    def ChangeRatioHeight(self, HeightBy=2500):
        # ratio = original_w / original_h
        ratio = self.relwidth/self.relheight
        self.relheight = max(rglobals.min_rel_size, self.relheight + HeightBy)
        self.relwidth = max(rglobals.min_rel_size, int(ratio * self.relheight))
    def SetRatioHeight(self, relheight=2500):
        # ratio = original_w / original_h
        ratio = self.relwidth/self.relheight
        self.relheight = max(rglobals.min_rel_size, relheight)
        self.relwidth = max(rglobals.min_rel_size, int(ratio * self.relheight))
    def ChangeTransparency(self, ChangeTransparencyBy=1):
        self.transparency = max(0, min(10000, self.transparency + ChangeTransparencyBy))
    def SetTransparency(self, transparency=10000):
        self.transparency = max(0, min(10000, transparency))
    def hide(self):
        self.visibility = "hidden"
    def show(self):
        self.visibility = "normal"
    def SetAnchor(self, anchor="nw"):
        self.anchor = anchor
    def SetScroll(self, scrolling=True):
        self.scrolling=scrolling
    def MouseHovering(self,additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0):
        w = self.relwidth
        h = self.relheight
        ox, oy = self.anchor_offsets.get(self.anchor,(0,0))
        x1 = self.relx + ox
        y1 = self.rely + oy
        x2 = x1 + w + additional_offset_x2
        y2 = y1 + h + additional_offset_y2
        x1 = x1 + additional_offset_x1
        y1 = y1 + additional_offset_y1
        return x1 < rglobals.relmouse_x < x2 and y1 < rglobals.relmouse_y < y2
    def MouseClicked(self,additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0):
        if(rglobals.mouse_clicked['left'] and self.MouseHovering(additional_offset_x1,additional_offset_y1,additional_offset_x2,additional_offset_y2)):
            return True
        else:
            return False
    def SetQuality(self,quality=0):
        self.quality=quality
        if self.quality == 0:
            # Fastest: No interpolation, looks pixelated when scaled up.
            self.resample_type = Image.Resampling.NEAREST
        elif self.quality == 1:
            # Fast: Basic linear interpolation, good for downscaling.
            self.resample_type = Image.Resampling.BILINEAR
        elif self.quality == 2:
            # Better: A bit slower, smoother than Bilinear.
            self.resample_type = Image.Resampling.HAMMING
        elif self.quality == 3:
            # Balanced: High quality, slightly sharper than Bilinear.
            self.resample_type = Image.Resampling.BICUBIC
        elif self.quality == 4:
            # Best: Highest quality for photographic images, but much slower.
            self.resample_type = Image.Resampling.LANCZOS
    # --- helper: rotate using fast 90° multiples when possible ---
    def _rotate_image(self, img, angle):
        if angle % 90 == 0:
            times = (angle // 90) % 4
            if times == 1:
                return img.transpose(Image.ROTATE_90)
            elif times == 2:
                return img.transpose(Image.ROTATE_180)
            elif times == 3:
                return img.transpose(Image.ROTATE_270)
            else:
                return img
        else:
            return img.rotate(angle, expand=True, fillcolor=(0,0,0,0), resample=self.resample_type)
    # --- helper: apply transparency using precomputed LUT ---
    def _apply_transparency(self, img, transparency):
        """
        Apply transparency using precomputed LUTs for 0–100% levels.
        Transparency: 0–10000 internally
        """
        if transparency >= 10000:
            # Fully opaque → no LUT needed
            return ImageTk.PhotoImage(img)
        # Map 0–10000 → 0–100 index for LUT
        level_index = max(0, min(100, transparency // 100))
        # Get precomputed LUT
        lut = self.alpha_luts[level_index]
        # Apply LUT efficiently
        img_copy = img.copy()
        alpha_channel = img_copy.getchannel('A')
        img_copy.putalpha(alpha_channel.point(lut))
        # Return Tkinter PhotoImage
        return ImageTk.PhotoImage(img_copy)
    # --- optimized update ---
    def Update(self):
        SizeChanged         = (self.relwidth != self.previous_relwidth or self.relheight != self.previous_relheight or rglobals.sq_size != rglobals.previous_sq_size)
        AngleChanged        = (self.angle != self.previous_angle)
        TransparencyChanged = (self.transparency != self.previous_transparency)
        PositionChanged     = (self.relx != self.previous_relx or self.rely != self.previous_rely or rglobals.sq_size != rglobals.previous_sq_size)
        AnchorChanged       = (self.anchor != self.previous_anchor)
        VisibilityChanged   = (self.visibility != self.previous_visibility)
        # Auto-show if in bounds
        in_bounds = (
            self.transparency > 0 and
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )
        if in_bounds and self.visibility == "hidden":
            self.show()
        # Update visibility
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.image_id, state=self.visibility)
            self.previous_visibility = self.visibility
        if self.visibility != "normal":
            self._store_previous()
            return
        # Update size if changed
        if SizeChanged:
            self.new_w = max(1, int((self.relwidth / 10000) * rglobals.sq_size))
            self.new_h = max(1, int((self.relheight / 10000) * rglobals.sq_size))
            self.resized_base = self.original_img.resize((self.new_w, self.new_h), self.resample_type)
        # Update rotation if size or angle changed
        if SizeChanged or AngleChanged:
            self.rotated_resized = self._rotate_image(self.resized_base, self.angle)
        # Update transparency if needed
        if SizeChanged or AngleChanged or TransparencyChanged:
            self.tk_img = self._apply_transparency(self.rotated_resized, self.transparency)
            rglobals.canvas.itemconfig(self.image_id, image=self.tk_img)
        # Update anchor
        if AnchorChanged:
            rglobals.canvas.itemconfig(self.image_id, anchor=self.anchor)
        # Update position
        if PositionChanged or rglobals.WindowChanged or rglobals.ScrollChanged:
            x = ((self.relx / 10000) * rglobals.sq_size) + rglobals.x_offset
            y = ((self.rely / 10000) * rglobals.sq_size) + rglobals.y_offset
            if not self.scrolling:
                x += rglobals.scroll_x
                y += rglobals.scroll_y
            rglobals.canvas.coords(self.image_id, x, y)
        # Auto-hide if out of bounds
        if not in_bounds and self.visibility == "normal":
            self.hide()
        # Store previous state
        self._store_previous()
    def _store_previous(self):
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_angle = self.angle
        self.previous_transparency = self.transparency
        self.previous_anchor = self.anchor
    def delete(self):
        # Remove from canvas
        try:
            if hasattr(self, "image_id") and self.image_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.image_id)
        except Exception:
            pass
        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass
        # Clear all image references
        attrs_to_clear = [
            "original_img", "resized_base", "rotated_resized",
            "tk_img", "alpha_luts"
        ]
        for attr in attrs_to_clear:
            if hasattr(self, attr):
                try:
                    delattr(self, attr)
                except Exception:
                    pass
        # Delete all other instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass
        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
            # Grab default values from the __init__ signature
            defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
            return f"""
This is an ezImage object! It creates an easy image and automatically handles putting it on the screen, changing it, and it is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy image like this:
MyezImage = ezImage(ImagePath={os.sep}path{os.sep}to{os.sep}image.png, relx={defaults['relx']}, rely={defaults['rely']}, relwidth={defaults['relwidth']}, relheight={defaults['relheight']}, angle={defaults['angle']}, transparency={defaults['transparency']}, anchor='{defaults['anchor']}', scrolling={defaults['scrolling']}, quality={defaults['quality']})
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
relx means relative x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely means relative y position.
relwidth means relative width.
relheight means relative height.
angle means rotating the image.
transparency means... exactly what it says, 10,000 is full transparency and 5,000 is half
anchor means north east south west. It must be n, ne, e, se, s, sw, w, nw, or center
scrolling means is it allowed to scroll or is it stuck to the screen position?
quality means how good the image looks. It can be 0-4.

Here are the functions you need:

MyezImage.move(XAmount=0,YAmount=0) This function moves the image by the set amount of relative input.
MyezImage.SetPosition(relx=0,rely=0) This function puts the image in a specific place, relative.
MyezImage.rotate(DegreesToRotate) This function rotates the image by the degrees. Simple...
MyezImage.SetAngle(angle) Similar to above, this function sets the specific degrees of rotation.
MyezImage.ChangeSize(WidthBy=0, HeightBy=0) This function changes the size of the image, relative again.
MyezImage.SetSize(relwidth=2500, relheight=2500) This function sets the size to a specific thing, relative again.
MyezImage.ChangeRatioWidth(WidthBy=2500) This function changes the relative width of the image, and then changes the relheight along with it.
MyezImage.SetRatioWidth(relwidth=2500) This function sets the relwidth, also relative to the height of the image.
MyezImage.ChangeRatioHeight(HeightBy=2500) This function changes the ratio height of the image. Relative to the relwidth.
MyezImage.SetRatioHeight(relheight=2500) This function sets the ratio height. And changes the relwidth as well.
MyezImage.ChangeTransparency(ChangeTransparencyBy=1) This function obviously... changes the transparency. between 0 and 10,000
MyezImage.SetTransparency(transparency=10000) This function obviously... sets the transparency. Between 0 and 10,000
MyezImage.hide() This function makes the image invisible. It does NOT delete it.
MyezImage.show() This function shows the image if it's invisible.
MyezImage.SetAnchor(anchor="nw") This function sets the "anchor". Could be "ne, nw, se, sw, n, w, s, e, or center."
MyezImage.SetScroll(scrolling=True) This function sets whether or not the image should scroll on the screen.
MyezImage.MouseHovering(additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0) This function checks if the mouse is hovering over the image, the offsets are relative again, but returns True if the mouse is hovering.
MyezImage.MouseClicked(additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0) This function returns true only if the mouse clicks the image, the offets are again relative.
MyezImage.SetQuality(quality=0) This sets how clear the image is, 0-4
MyezImage.delete() This deletes the image entirely and frees up space.

MyezImage.Update() Probably not needed. This applies our changes all at once. Takes a lot of cpu usage to do this every time we change one tiny thing so this runs after every frame only. Probably not needed...
"""

#I found that font_size scale hack by manually plugging in numbers for the font:
#x=5, y=39
#x=10, y=73
#x=15, y=111
#x=20, y=150
#x=25, y=184
#x=30, y=219
#x=35, y=257
#x=40, y=296
#x=45, y=325
#x=50, y=365
#x=55, y=399
#x=60, y=441
#x=65, y=472
#x=70, y=505
#x=75, y=544
#x=80, y=578
#x=85, y=613
#x=90, y=652
#x=95, y=686
#x=100, y=721
import inspect

class ezText():
    def __init__(self, MyText, relx=1500, rely=400, relfont_size=10000,
                 font_name="Arial", anchor="nw", scrolling=True, transparency=10000, color="black"):
        self.MyText = MyText
        self.relx = relx
        self.rely = rely
        self.relfont_size = relfont_size
        self.font_name = font_name
        self.anchor = anchor
        self.scrolling = scrolling
        self.transparency = transparency
        self.color = color
        self.visibility = "normal"
        # --- previous states ---
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relfont_size = self.relfont_size
        self.previous_anchor = self.anchor
        self.previous_text = self.MyText
        self.previous_font_name = self.font_name
        self.previous_transparency = self.transparency
        self.previous_color = self.color
        self.previous_visibility = self.visibility
        # --- compute initial font size ---
        self.font_size = int((rglobals.sq_size - 4.36842) *
                             rglobals.font_scale *
                             self.relfont_size)
        self.text_id = rglobals.canvas.create_text(
            int((self.relx/10000)*rglobals.sq_size)+rglobals.x_offset,
            int((self.rely/10000)*rglobals.sq_size)+rglobals.y_offset,
            text=self.MyText,
            font=(self.font_name, self.font_size),
            anchor=self.anchor,
            fill=self.color
        )
        rglobals.AllItems.add(self)
    def move(self,XAmount=0,YAmount=0):
        self.relx += XAmount
        self.rely += YAmount
    def SetPosition(self,relx=0,rely=0):
        self.relx = relx
        self.rely = rely
    def SetSize(self,relfont_size):
        self.relfont_size = relfont_size
    def ChangeSize(self,relfont_size_amount):
        self.relfont_size += relfont_size_amount
    def SetText(self,NewText):
        self.MyText = NewText
    def SetColor(self, color="black"):
        self.color = color
    def ChangeTransparency(self, amount):
        self.transparency = max(0, min(10000, self.transparency + amount))
    def SetTransparency(self, transparency):
        self.transparency = max(0, min(10000, transparency))
    def hide(self):
        self.visibility = "hidden"
    def show(self):
        self.visibility = "normal"
    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling
    # --- transparency helper ---
    def _get_stipple(self):
        if self.transparency >= 10000:
            return ""
        elif self.transparency >= 7500:
            return "gray12"
        elif self.transparency >= 5000:
            return "gray25"
        elif self.transparency >= 2500:
            return "gray50"
        else:
            return "gray75"
    def MouseHovering(self, additional_offset_x1=0, additional_offset_y1=0,
                      additional_offset_x2=0, additional_offset_y2=0):
        bbox = rglobals.canvas.bbox(self.text_id)
        if bbox is None:
            return False
        x1, y1, x2, y2 = bbox
        x1 = ((x1 - rglobals.x_offset) / rglobals.sq_size) * 10000
        y1 = ((y1 - rglobals.y_offset) / rglobals.sq_size) * 10000
        x2 = ((x2 - rglobals.x_offset) / rglobals.sq_size) * 10000
        y2 = ((y2 - rglobals.y_offset) / rglobals.sq_size) * 10000
        x1 += additional_offset_x1
        y1 += additional_offset_y1
        x2 += additional_offset_x2
        y2 += additional_offset_y2
        return x1 < rglobals.relmouse_x < x2 and y1 < rglobals.relmouse_y < y2
    def MouseClicked(self, *args):
        return rglobals.mouse_clicked['left'] and self.MouseHovering(*args)
    # --- optimized update ---
    def Update(self):
        PositionChanged = (
            self.relx != self.previous_relx or
            self.rely != self.previous_rely or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        SizeChanged = (
            self.relfont_size != self.previous_relfont_size or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        AnchorChanged = (self.anchor != self.previous_anchor)
        TextChanged = (self.MyText != self.previous_text)
        FontChanged = (self.font_name != self.previous_font_name)
        TransparencyChanged = (self.transparency != self.previous_transparency)
        ColorChanged = (self.color != self.previous_color)
        VisibilityChanged = (self.visibility != self.previous_visibility)
        # --- visibility update ---
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.text_id, state=self.visibility)
            self.previous_visibility = self.visibility
        if self.visibility != "normal":
            self._store_previous()
            return
        # --- auto bounds visibility ---
        in_bounds = (
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )
        if not in_bounds:
            self.hide()
        # --- position update ---
        if PositionChanged or rglobals.WindowChanged or rglobals.ScrollChanged:
            x = int((self.relx/10000)*rglobals.sq_size)+rglobals.x_offset
            y = int((self.rely/10000)*rglobals.sq_size)+rglobals.y_offset
            if not self.scrolling:
                x += rglobals.scroll_x
                y += rglobals.scroll_y
            rglobals.canvas.coords(self.text_id, x, y)
        # --- font size update ---
        if SizeChanged or AnchorChanged or FontChanged:
            self.font_size = int((rglobals.sq_size - 4.36842) *
                                 rglobals.font_scale *
                                 self.relfont_size)
            rglobals.canvas.itemconfig(
                self.text_id,
                font=(self.font_name, self.font_size),
                anchor=self.anchor
            )
        # --- text update ---
        if TextChanged:
            rglobals.canvas.itemconfig(self.text_id, text=self.MyText)
        # --- color update ---
        if ColorChanged:
            rglobals.canvas.itemconfig(self.text_id, fill=self.color)
        # --- transparency update ---
        if TransparencyChanged:
            rglobals.canvas.itemconfig(
                self.text_id,
                stipple=self._get_stipple()
            )
        # store previous
        self._store_previous()
    def _store_previous(self):
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relfont_size = self.relfont_size
        self.previous_anchor = self.anchor
        self.previous_text = self.MyText
        self.previous_font_name = self.font_name
        self.previous_transparency = self.transparency
        self.previous_color = self.color
    def delete(self):
        # Remove from canvas
        try:
            if hasattr(self, "text_id") and self.text_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.text_id)
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete all instance attributes
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezText object! It creates an easy text on screen and automatically handles putting it on the screen, changing it, and it is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy text like this:
MyezText = ezText(MyText="Text to place on screen", relx={defaults['relx']}, rely={defaults['rely']}, relfont_size={defaults['relfont_size']}, font_name="{defaults['font_name']}", anchor="{defaults['anchor']}", scrolling={defaults['scrolling']}, transparency={defaults['transparency']}, color="{defaults['color']}")
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
relx means relative x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely means relative y position.
relfont_size is the relative font size... this was difficult to figure out.
font_name is the type of font you want the text to have (like Arial or Comic Sans... if you're into that).
anchor means north east south west. It must be n, ne, e, se, s, sw, w, nw, or center. It changes where the text is anchored relative to its position!
scrolling means is it allowed to scroll or is it stuck to the screen position?
transparency means... exactly what it says, 10,000 is fully visible, and lower numbers stipple it out! (Tkinter text transparency is funky like that)
color can be standard color names like "red", "blue", "white", or hex codes like "#ff0055".

Here are the functions you need:

MyezText.move(XAmount=0, YAmount=0) This function moves the text position by the relative amount you specify.
MyezText.SetPosition(relx=0, rely=0) This function sets the text to an absolute relative position.
MyezText.SetSize(relfont_size) This function directly sets the font size to a specific relative value.
MyezText.ChangeSize(relfont_size_amount) This function changes the relative font size by adding or subtracting an amount.
MyezText.SetText(NewText) This function updates what the text actually says on the screen.
MyezText.SetColor(color="black") This function changes the color of the text. Supports names or Hex codes.
MyezText.ChangeTransparency(amount) This function changes the stipple transparency. Max is 10,000.
MyezText.SetTransparency(transparency) This function sets the stipple transparency to a specific value between 0 and 10,000.
MyezText.hide() This function makes the text invisible. It does NOT delete it.
MyezText.show() This function shows the text if it was hidden.
MyezText.SetScroll(scrolling=True) This function sets whether or not the text should move when the screen scrolls.
MyezText.MouseHovering(additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0) This checks if the user's mouse is hovering within the bounding box of the text! Handy for custom buttons. Returns True or False.
MyezText.MouseClicked(additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0) Returns True if the left mouse button clicks inside the text boundary.
MyezText.delete() This completely obliterates the text from the canvas and forces garbage collection to free up memory.

MyezText.Update() Probably not needed. This applies our position, sizing, text, and visibility updates all at once dynamically. It runs automatically behind the scenes per frame!
"""


class ezLine():
    def __init__(self, relx1=50, rely1=50, relx2=350, rely2=350,
                 fill="blue", relwidth=3, scrolling=True, transparency=10000):
        
        self.relx1 = relx1
        self.rely1 = rely1
        self.relx2 = relx2
        self.rely2 = rely2

        self.relwidth = relwidth
        self.fill = fill
        self.scrolling = scrolling
        self.transparency = transparency

        self.visibility = "normal"

        # --- previous states ---
        self.previous_relx1 = self.relx1
        self.previous_rely1 = self.rely1
        self.previous_relx2 = self.relx2
        self.previous_rely2 = self.rely2
        self.previous_relwidth = self.relwidth
        self.previous_fill = self.fill
        self.previous_transparency = self.transparency
        self.previous_visibility = self.visibility

        self.line_id = rglobals.canvas.create_line(
            int((self.relx1/10000)*rglobals.sq_size)+rglobals.x_offset,
            int((self.rely1/10000)*rglobals.sq_size)+rglobals.y_offset,
            int((self.relx2/10000)*rglobals.sq_size)+rglobals.x_offset,
            int((self.rely2/10000)*rglobals.sq_size)+rglobals.y_offset,
            fill=self.fill,
            width=int((rglobals.sq_size/600)*self.relwidth)
        )
        rglobals.AllItems.add(self)
    def SetPosition(self, relx1, rely1, relx2, rely2):
        self.relx1 = relx1
        self.rely1 = rely1
        self.relx2 = relx2
        self.rely2 = rely2

    def SetWidth(self, relwidth):
        self.relwidth = relwidth

    def ChangeWidth(self, amount):
        self.relwidth = max(0, min(10000, self.relwidth + amount))

    def SetColor(self, fill):
        self.fill = fill

    def ChangeTransparency(self, amount):
        self.transparency = max(0, min(10000, self.transparency + amount))

    def SetTransparency(self, transparency):
        self.transparency = max(0, min(10000, transparency))

    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetVisibility(self,visibility):
        self.visibility = visibility

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    # --- transparency helper ---
    def _get_stipple(self):
        if self.transparency >= 10000:
            return ""
        elif self.transparency >= 7500:
            return "gray12"
        elif self.transparency >= 5000:
            return "gray25"
        elif self.transparency >= 2500:
            return "gray50"
        else:
            return "gray75"

    def MouseHovering(self, tolerance=0):
        x1 = ((self.relx1/10000)*rglobals.sq_size)+rglobals.x_offset
        y1 = ((self.rely1/10000)*rglobals.sq_size)+rglobals.y_offset
        x2 = ((self.relx2/10000)*rglobals.sq_size)+rglobals.x_offset
        y2 = ((self.rely2/10000)*rglobals.sq_size)+rglobals.y_offset

        if not self.scrolling:
            x1 += rglobals.scroll_x
            y1 += rglobals.scroll_y
            x2 += rglobals.scroll_x
            y2 += rglobals.scroll_y

        mx = ((rglobals.relmouse_x/10000)*rglobals.sq_size)+rglobals.x_offset
        my = ((rglobals.relmouse_y/10000)*rglobals.sq_size)+rglobals.y_offset

        dx = x2-x1
        dy = y2-y1

        if dx == 0 and dy == 0:
            dist = math.hypot(mx-x1, my-y1)
        else:
            t = ((mx-x1)*dx + (my-y1)*dy)/(dx*dx+dy*dy)
            t = max(0,min(1,t))
            closest_x = x1+t*dx
            closest_y = y1+t*dy
            dist = math.hypot(mx-closest_x,my-closest_y)

        line_width = int((rglobals.sq_size/600)*self.relwidth)

        return dist <= (line_width/2 + tolerance)

    def MouseClicked(self, tolerance=0):
        return rglobals.mouse_clicked['left'] and self.MouseHovering(tolerance)

    # --- optimized update ---
    def Update(self):
        PositionChanged = (
            self.relx1 != self.previous_relx1 or
            self.rely1 != self.previous_rely1 or
            self.relx2 != self.previous_relx2 or
            self.rely2 != self.previous_rely2 or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        WidthChanged = (
            self.relwidth != self.previous_relwidth or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        ColorChanged = (self.fill != self.previous_fill)
        TransparencyChanged = (self.transparency != self.previous_transparency)
        VisibilityChanged = (self.visibility != self.previous_visibility)
        # visibility update
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.line_id, state=self.visibility)
            self.previous_visibility = self.visibility
        if self.visibility != "normal":
            self._store_previous()
            return
        # position update
        if PositionChanged or rglobals.WindowChanged or rglobals.ScrollChanged:
            x1 = int((self.relx1/10000)*rglobals.sq_size)+rglobals.x_offset
            y1 = int((self.rely1/10000)*rglobals.sq_size)+rglobals.y_offset
            x2 = int((self.relx2/10000)*rglobals.sq_size)+rglobals.x_offset
            y2 = int((self.rely2/10000)*rglobals.sq_size)+rglobals.y_offset
            if not self.scrolling:
                x1 += rglobals.scroll_x
                y1 += rglobals.scroll_y
                x2 += rglobals.scroll_x
                y2 += rglobals.scroll_y

            rglobals.canvas.coords(self.line_id, x1,y1,x2,y2)
        # width update
        if WidthChanged:
            rglobals.canvas.itemconfig(
                self.line_id,
                width=int((rglobals.sq_size/600)*self.relwidth)
            )
        # color update
        if ColorChanged:
            rglobals.canvas.itemconfig(self.line_id, fill=self.fill)
        # transparency update
        if TransparencyChanged:
            rglobals.canvas.itemconfig(
                self.line_id,
                stipple=self._get_stipple()
            )
        self._store_previous()
    def _store_previous(self):
        self.previous_relx1 = self.relx1
        self.previous_rely1 = self.rely1
        self.previous_relx2 = self.relx2
        self.previous_rely2 = self.rely2
        self.previous_relwidth = self.relwidth
        self.previous_fill = self.fill
        self.previous_transparency = self.transparency
    def delete(self):
        # Remove line from canvas
        try:
            if hasattr(self, "line_id") and self.line_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.line_id)
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete all instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezLine object! It creates an easy line on the screen and automatically handles drawing it, changing it, and it is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy line like this:
MyezLine = ezLine(relx1={defaults['relx1']}, rely1={defaults['rely1']}, relx2={defaults['relx2']}, rely2={defaults['rely2']}, fill="{defaults['fill']}", relwidth={defaults['relwidth']}, scrolling={defaults['scrolling']}, transparency={defaults['transparency']})
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
relx1 means relative starting x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely1 means relative starting y position.
relx2 means relative ending x position.
rely2 means relative ending y position.
fill means what color the line is. You can pass names like "blue" or hex codes like "#334455"!
relwidth means relative thickness of the line.
scrolling means is it allowed to scroll or is it stuck to the screen position?
transparency means... exactly what it says, 10,000 is fully visible, and lower numbers stipple it out! (Tkinter line transparency uses that retro stippling effect)

Here are the functions you need:

MyezLine.SetPosition(relx1, rely1, relx2, rely2) This function shifts the start and end coordinates of the line to a specific relative spot.
MyezLine.SetWidth(relwidth) This function sets the thickness of the line to a specific relative width.
MyezLine.ChangeWidth(amount) This function changes the thickness of the line, adding or subtracting the amount.
MyezLine.SetColor(fill) This changes the color of the line on the fly.
MyezLine.ChangeTransparency(amount) This function changes the line's stipple transparency by adding or subtracting an amount. Max is 10,000.
MyezLine.SetTransparency(transparency) This function directly sets the transparency to a specific value between 0 and 10,000.
MyezLine.hide() This function makes the line invisible. It does NOT delete it.
MyezLine.show() This function makes the line visible again if it was hidden.
MyezLine.SetScroll(scrolling=True) This sets whether or not the line stays stuck to the screen or moves when the canvas scrolls.
MyezLine.MouseHovering(tolerance=0) Checks if the mouse is hovering over or near the line! You can pass a 'tolerance' value to make it easier to hover over thin lines. Returns True or False.
MyezLine.MouseClicked(tolerance=0) Returns True if you left-click on or near the line based on your tolerance! Great for making interactive wireframes.
MyezLine.delete() This completely wipes the line off the Tkinter canvas and cleans up the memory immediately.

MyezLine.Update() Probably not needed. This syncs up all position, color, and size shifts simultaneously behind the scenes right before the frame renders!
"""

class ezBoundaries():
    def __init__(self,fill="red",relwidth=3,transparency=10000):
        self.relwidth = relwidth
        self.fill=fill
        self.transparency = transparency
        self.visibility = "normal"
        self.Boundary1 = ezLine(0,0,10000,10000,fill=self.fill,relwidth=self.relwidth,transparency=self.transparency)
        self.Boundary2 = ezLine(10000,0,0,10000,fill=self.fill,relwidth=self.relwidth,transparency=self.transparency)
        self.Boundary3 = ezLine(0,0,0,10000,fill=self.fill,relwidth=self.relwidth,transparency=self.transparency)
        self.Boundary4 = ezLine(0,0,10000,0,fill=self.fill,relwidth=self.relwidth,transparency=self.transparency)
        self.Boundary5 = ezLine(0,10000,10000,10000,fill=self.fill,relwidth=self.relwidth,transparency=self.transparency)
        self.Boundary6 = ezLine(10000,0,10000,10000,fill=self.fill,relwidth=self.relwidth,transparency=self.transparency)
        rglobals.AllItems.add(self)
        self.previous_relwidth = self.relwidth
        self.previous_fill = self.fill
        self.previous_transparency = self.transparency
        self.previous_visibility = self.visibility
    def SetWidth(self, relwidth):
        self.relwidth = relwidth

    def ChangeWidth(self, amount):
        self.relwidth = max(0, min(10000, self.relwidth + amount))

    def SetColor(self, fill):
        self.fill = fill

    def ChangeTransparency(self, amount):
        self.transparency = max(0, min(10000, self.transparency + amount))

    def SetTransparency(self, transparency):
        self.transparency = max(0, min(10000, transparency))

    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetVisibility(self,visibility):
        self.visibility = visibility

    def Update(self):
        WidthChanged = (self.relwidth != self.previous_relwidth)
        ColorChanged = (self.fill != self.previous_fill)
        TransparencyChanged = (self.transparency != self.previous_transparency)
        VisibilityChanged = (self.visibility != self.previous_visibility)

        if WidthChanged:
            self.Boundary1.SetWidth(self.relwidth)
            self.Boundary2.SetWidth(self.relwidth)
            self.Boundary3.SetWidth(self.relwidth)
            self.Boundary4.SetWidth(self.relwidth)
            self.Boundary5.SetWidth(self.relwidth)
            self.Boundary6.SetWidth(self.relwidth)
        if ColorChanged:
            self.Boundary1.SetColor(self.fill)
            self.Boundary2.SetColor(self.fill)
            self.Boundary3.SetColor(self.fill)
            self.Boundary4.SetColor(self.fill)
            self.Boundary5.SetColor(self.fill)
            self.Boundary6.SetColor(self.fill)
        if TransparencyChanged:
            self.Boundary1.SetTransparency(self.transparency)
            self.Boundary2.SetTransparency(self.transparency)
            self.Boundary3.SetTransparency(self.transparency)
            self.Boundary4.SetTransparency(self.transparency)
            self.Boundary5.SetTransparency(self.transparency)
            self.Boundary6.SetTransparency(self.transparency)
        if VisibilityChanged:
            self.Boundary1.SetVisibility(self.visibility)
            self.Boundary2.SetVisibility(self.visibility)
            self.Boundary3.SetVisibility(self.visibility)
            self.Boundary4.SetVisibility(self.visibility)
            self.Boundary5.SetVisibility(self.visibility)
            self.Boundary6.SetVisibility(self.visibility)

        self.previous_relwidth = self.relwidth
        self.previous_fill = self.fill
        self.previous_transparency = self.transparency
        self.previous_visibility = self.visibility
    def delete(self):
        # 1. Safely call delete on all child ezLine objects
        for i in range(1, 7):
            boundary_attr = f"Boundary{i}"
            if hasattr(self, boundary_attr):
                line_obj = getattr(self, boundary_attr)
                if line_obj and hasattr(line_obj, "delete"):
                    try:
                        line_obj.delete()
                    except Exception:
                        pass

        # 2. Remove this ezBoundaries instance from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # 3. Wipe all instance variables belonging to this ezBoundaries object
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # 4. Encourage garbage collection (matching your ezLine pattern)
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature dynamically
        import inspect
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        
        return f"""
This is an ezBoundaries object! It generates a massive bounding container made up of SIX optimized ezLine objects (forming a bounding box and an X across the center) showing you exactly what I mean when I say rglobals.sq_size, window_width, window_height, or whatever!

You can create an ezBoundaries container like this:
MyezBoundaries = ezBoundaries(fill="{defaults['fill']}", relwidth={defaults['relwidth']}, transparency={defaults['transparency']})

Super simple to set up! Let's break down what these starting values mean:
fill means the color of all six boundary lines. You can pass names like "red" or hex codes like "#FF0000"!
relwidth means the relative thickness of all the boundary lines simultaneously.
transparency controls the visibility stippling effect, where 10,000 is completely solid and lower numbers create a retro mesh transparency.

Here are the functions you need to control the boundaries:

MyezBoundaries.SetWidth(relwidth) Sets a brand new relative thickness for all six boundary lines at once.
MyezBoundaries.ChangeWidth(amount) Adjusts the thickness of the lines by adding or subtracting an amount.
MyezBoundaries.SetColor(fill) Dynamically changes the color of all lines on the fly.
MyezBoundaries.ChangeTransparency(amount) Shifts the transparency mesh value up or down. Max is 10,000.
MyezBoundaries.SetTransparency(transparency) Directly overrides the transparency to a specific value between 0 and 10,000.
MyezBoundaries.hide() Makes the entire bounding system completely invisible without losing your settings.
MyezBoundaries.show() Brings the bounding box right back to normal visibility if it was hidden.
MyezBoundaries.delete() Wipes all six lines from the canvas, clears them from tracking, and flushes the memory instantly.

MyezBoundaries.Update() Usually handled automatically! This checks behind the scenes for updates and pushes changes down to the individual lines right before the frame renders.
"""

class ezRectangle():
    def __init__(self, relx1=100, rely1=100, relx2=200, rely2=200,
                 fill="blue", outline="black", relstroke=1,
                 scrolling=True, transparency=10000):

        self.relx1 = relx1
        self.rely1 = rely1
        self.relx2 = relx2
        self.rely2 = rely2

        self.fill = fill
        self.outline = outline
        self.relstroke = relstroke
        self.scrolling = scrolling
        self.transparency = transparency

        self.visibility = "normal"

        # --- previous states ---
        self.previous_relx1 = self.relx1
        self.previous_rely1 = self.rely1
        self.previous_relx2 = self.relx2
        self.previous_rely2 = self.rely2
        self.previous_fill = self.fill
        self.previous_outline = self.outline
        self.previous_relstroke = self.relstroke
        self.previous_transparency = self.transparency
        self.previous_visibility = self.visibility

        # create rectangle
        self.rect_id = rglobals.canvas.create_rectangle(
            ((self.relx1 / 10000) * rglobals.sq_size)+rglobals.x_offset,
            ((self.rely1 / 10000) * rglobals.sq_size)+rglobals.y_offset,
            ((self.relx2 / 10000) * rglobals.sq_size)+rglobals.x_offset,
            ((self.rely2 / 10000) * rglobals.sq_size)+rglobals.y_offset,
            fill=self.fill,
            outline=self.outline,
            width=self.relstroke * (rglobals.sq_size / 600)
        )
        rglobals.AllItems.add(self)
    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetPosition(self, relx1="NULL", rely1="NULL", relx2="NULL", rely2="NULL"):
        if relx1 != "NULL":
            self.relx1 = relx1
        if rely1 != "NULL":
            self.rely1 = rely1
        if relx2 != "NULL":
            self.relx2 = relx2
        if rely2 != "NULL":
            self.rely2 = rely2
    def ChangePosition(self, dx1="NULL", dy1="NULL", dx2="NULL", dy2="NULL"):
        if dx1 != "NULL":
            self.relx1 += dx1
        if dy1 != "NULL":
            self.rely1 += dy1
        if dx2 != "NULL":
            self.relx2 += dx2
        if dy2 != "NULL":
            self.rely2 += dy2

    def SetStroke(self, new_relstroke):
        self.relstroke = new_relstroke

    def ChangeStroke(self, delta_stroke):
        self.relstroke += delta_stroke

    def SetFill(self, new_fill):
        self.fill = new_fill

    def SetOutline(self, new_outline):
        self.outline = new_outline

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    def ChangeTransparency(self, amount):
        self.transparency = max(0, min(10000, self.transparency + amount))

    def SetTransparency(self, transparency):
        self.transparency = max(0, min(10000, transparency))

    def _get_stipple(self):
        if self.transparency >= 10000:
            return ""
        elif self.transparency >= 7500:
            return "gray12"
        elif self.transparency >= 5000:
            return "gray25"
        elif self.transparency >= 2500:
            return "gray50"
        else:
            return "gray75"

    def MouseHovering(self, additional_offset_x1=0, additional_offset_y1=0,
                      additional_offset_x2=0, additional_offset_y2=0):

        x1 = min(self.relx1, self.relx2)
        y1 = min(self.rely1, self.rely2)
        x2 = max(self.relx1, self.relx2)
        y2 = max(self.rely1, self.rely2)

        x1 += additional_offset_x1
        y1 += additional_offset_y1
        x2 += additional_offset_x2
        y2 += additional_offset_y2

        return x1 < rglobals.relmouse_x < x2 and y1 < rglobals.relmouse_y < y2

    def MouseClicked(self, *args):
        return rglobals.mouse_clicked['left'] and self.MouseHovering(*args)

    # --- optimized update ---
    def Update(self):

        PositionChanged = (
            self.relx1 != self.previous_relx1 or
            self.rely1 != self.previous_rely1 or
            self.relx2 != self.previous_relx2 or
            self.rely2 != self.previous_rely2 or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        StrokeChanged = (self.relstroke != self.previous_relstroke)
        ColorChanged = (self.fill != self.previous_fill or self.outline != self.previous_outline)
        TransparencyChanged = (self.transparency != self.previous_transparency)
        VisibilityChanged = (self.visibility != self.previous_visibility)

        # --- visibility update ---
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.rect_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        # --- auto bounds visibility ---
        in_bounds = (
            rglobals.minimum_relx < self.relx1 < rglobals.maximum_relx or
            rglobals.minimum_relx < self.relx2 < rglobals.maximum_relx
        )

        if not in_bounds:
            self.hide()

        # --- position update ---
        if PositionChanged or rglobals.WindowChanged or rglobals.ScrollChanged:

            x1 = ((self.relx1 / 10000) * rglobals.sq_size)+rglobals.x_offset
            y1 = ((self.rely1 / 10000) * rglobals.sq_size)+rglobals.y_offset
            x2 = ((self.relx2 / 10000) * rglobals.sq_size)+rglobals.x_offset
            y2 = ((self.rely2 / 10000) * rglobals.sq_size)+rglobals.y_offset

            if not self.scrolling:
                x1 += rglobals.scroll_x
                y1 += rglobals.scroll_y
                x2 += rglobals.scroll_x
                y2 += rglobals.scroll_y

            rglobals.canvas.coords(self.rect_id, x1, y1, x2, y2)

        # --- stroke update ---
        if StrokeChanged or rglobals.WindowChanged:

            rglobals.canvas.itemconfig(
                self.rect_id,
                width=self.relstroke * (rglobals.sq_size / 600)
            )

        # --- color update ---
        if ColorChanged:
            rglobals.canvas.itemconfig(
                self.rect_id,
                fill=self.fill,
                outline=self.outline
            )

        # --- transparency update ---
        if TransparencyChanged:
            rglobals.canvas.itemconfig(
                self.rect_id,
                stipple=self._get_stipple()
            )

        self._store_previous()

    def _store_previous(self):
        self.previous_relx1 = self.relx1
        self.previous_rely1 = self.rely1
        self.previous_relx2 = self.relx2
        self.previous_rely2 = self.rely2
        self.previous_fill = self.fill
        self.previous_outline = self.outline
        self.previous_relstroke = self.relstroke
        self.previous_transparency = self.transparency
    def delete(self):
        # Remove from canvas
        try:
            if hasattr(self, "rect_id") and self.rect_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.rect_id)
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete all instance attributes
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezRectangle object! It creates an easy rectangle on the screen and automatically handles drawing it, coloring it, and it is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy rectangle like this:
MyezRectangle = ezRectangle(relx1={defaults['relx1']}, rely1={defaults['rely1']}, relx2={defaults['relx2']}, rely2={defaults['rely2']}, fill="{defaults['fill']}", outline="{defaults['outline']}", relstroke={defaults['relstroke']}, scrolling={defaults['scrolling']}, transparency={defaults['transparency']})
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
relx1 means relative starting x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely1 means relative starting y position.
relx2 means relative ending x position.
rely2 means relative ending y position.
fill means what color the inside of the rectangle is. You can use text names or hex codes like "#334455"!
outline means the color of the border lines.
relstroke is the size/thickness of that border outline.
scrolling means is it allowed to scroll or is it stuck to the screen position?
transparency means... exactly what it says, 10,000 is fully visible, and lower numbers stipple it out! (Tkinter rectangle transparency uses that retro stippling effect)

Here are the functions you need:

MyezRectangle.hide() This function makes the rectangle completely invisible. It does NOT delete it.
MyezRectangle.show() This function makes the rectangle visible again if it was hidden.
MyezRectangle.SetPosition(relx1="NULL", rely1="NULL", relx2="NULL", rely2="NULL") This sets specific relative positions for whichever coordinates you pass! It leaves the rest alone if you don't pass them.
MyezRectangle.ChangePosition(dx1="NULL", dy1="NULL", dx2="NULL", dy2="NULL") This shifts the rectangle's corners relative to where they currently are by adding or subtracting.
MyezRectangle.SetStroke(new_relstroke) Directly sets the thickness of the rectangle's border line.
MyezRectangle.ChangeStroke(delta_stroke) Adds or subtracts thickness to the rectangle's border line.
MyezRectangle.SetFill(new_fill) Dynamically changes the color inside the rectangle.
MyezRectangle.SetOutline(new_outline) Dynamically changes the color of the border outline.
MyezRectangle.SetScroll(scrolling=True) Sets whether the rectangle floats static on screen or moves along with the canvas scroll.
MyezRectangle.ChangeTransparency(amount) Changes the stipple transparency by adding/subtracting an amount. Max is 10,000.
MyezRectangle.SetTransparency(transparency) Directly sets the stipple transparency to a specific value between 0 and 10,000.
MyezRectangle.MouseHovering(additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0) Checks if the user's mouse is hovering anywhere inside the bounds of the rectangle! Super useful for making custom UI panels or invisible button zones. Returns True or False.
MyezRectangle.MouseClicked(*args) Returns True if the user left-clicks inside the rectangle boundaries. Great for UI components!
MyezRectangle.delete() This completely wipes the rectangle from the canvas tracker and handles memory cleanup immediately.

MyezRectangle.Update() Probably not needed. This syncs up all position, sizing, color, border, and visibility adjustments at once behind the scenes per frame!
"""




class ezOval():
    def __init__(self, relx1=100, rely1=100, relx2=200, rely2=200,
                 fill="blue", outline="black", relstroke=1, scrolling=True):
        self.relx1 = relx1
        self.rely1 = rely1
        self.relx2 = relx2
        self.rely2 = rely2

        self.fill = fill
        self.outline = outline
        self.relstroke = relstroke
        self.scrolling = scrolling

        self.visibility = "normal"

        # --- previous states ---
        self.previous_relx1 = self.relx1
        self.previous_rely1 = self.rely1
        self.previous_relx2 = self.relx2
        self.previous_rely2 = self.rely2
        self.previous_fill = self.fill
        self.previous_outline = self.outline
        self.previous_relstroke = self.relstroke
        self.previous_visibility = self.visibility

        self.stroke_width = int(self.relstroke * (rglobals.sq_size / 600))

        self.oval_id = rglobals.canvas.create_oval(
            ((self.relx1/10000)*rglobals.sq_size)+rglobals.x_offset,
            ((self.rely1/10000)*rglobals.sq_size)+rglobals.y_offset,
            ((self.relx2/10000)*rglobals.sq_size)+rglobals.x_offset,
            ((self.rely2/10000)*rglobals.sq_size)+rglobals.y_offset,
            fill=self.fill,
            outline=self.outline,
            width=self.stroke_width
        )
        rglobals.AllItems.add(self)
    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetPosition(self, relx1, rely1, relx2, rely2):
        self.relx1 = relx1
        self.rely1 = rely1
        self.relx2 = relx2
        self.rely2 = rely2

    def ChangePosition(self, dx1, dy1, dx2, dy2):
        self.relx1 += dx1
        self.rely1 += dy1
        self.relx2 += dx2
        self.rely2 += dy2

    def SetStroke(self, new_relstroke):
        self.relstroke = new_relstroke

    def ChangeStroke(self, delta):
        self.relstroke += delta

    def SetFill(self, new_fill):
        self.fill = new_fill

    def SetOutline(self, new_outline):
        self.outline = new_outline

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    def MouseHovering(self, additional_offset_x1=0, additional_offset_y1=0,
                      additional_offset_x2=0, additional_offset_y2=0):

        x1 = min(self.relx1, self.relx2)
        y1 = min(self.rely1, self.rely2)
        x2 = max(self.relx1, self.relx2)
        y2 = max(self.rely1, self.rely2)

        x1 += additional_offset_x1
        y1 += additional_offset_y1
        x2 += additional_offset_x2
        y2 += additional_offset_y2

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        rx = (x2 - x1) / 2
        ry = (y2 - y1) / 2

        if rx == 0 or ry == 0:
            return False

        value = ((rglobals.relmouse_x - cx)**2)/(rx**2) + ((rglobals.relmouse_y - cy)**2)/(ry**2)
        return value <= 1

    def MouseClicked(self, *args):
        return rglobals.mouse_clicked['left'] and self.MouseHovering(*args)

    def Update(self):

        PositionChanged = (
            self.relx1 != self.previous_relx1 or
            self.relx2 != self.previous_relx2 or
            self.rely1 != self.previous_rely1 or
            self.rely2 != self.previous_rely2 or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        StrokeChanged = (
            self.relstroke != self.previous_relstroke or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        ColorChanged = (
            self.fill != self.previous_fill or
            self.outline != self.previous_outline
        )

        VisibilityChanged = (self.visibility != self.previous_visibility)

        # --- visibility update ---
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.oval_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        # --- bounds auto visibility ---
        cx = (self.relx1 + self.relx2) / 2
        cy = (self.rely1 + self.rely2) / 2

        in_bounds = (
            rglobals.minimum_relx < cx < rglobals.maximum_relx and
            rglobals.minimum_rely < cy < rglobals.maximum_rely
        )

        if not in_bounds:
            self.hide()

        # --- position update ---
        if PositionChanged or rglobals.WindowChanged or rglobals.ScrollChanged:

            x1 = ((self.relx1/10000)*rglobals.sq_size)+rglobals.x_offset
            y1 = ((self.rely1/10000)*rglobals.sq_size)+rglobals.y_offset
            x2 = ((self.relx2/10000)*rglobals.sq_size)+rglobals.x_offset
            y2 = ((self.rely2/10000)*rglobals.sq_size)+rglobals.y_offset

            if not self.scrolling:
                x1 += rglobals.scroll_x
                y1 += rglobals.scroll_y
                x2 += rglobals.scroll_x
                y2 += rglobals.scroll_y

            rglobals.canvas.coords(self.oval_id, x1, y1, x2, y2)

        # --- stroke update ---
        if StrokeChanged or rglobals.WindowChanged:
            self.stroke_width = int(self.relstroke*(rglobals.sq_size/600))
            rglobals.canvas.itemconfig(self.oval_id, width=self.stroke_width)

        # --- color update ---
        if ColorChanged:
            rglobals.canvas.itemconfig(self.oval_id, fill=self.fill, outline=self.outline)

        self._store_previous()

    def _store_previous(self):
        self.previous_relx1 = self.relx1
        self.previous_rely1 = self.rely1
        self.previous_relx2 = self.relx2
        self.previous_rely2 = self.rely2
        self.previous_fill = self.fill
        self.previous_outline = self.outline
        self.previous_relstroke = self.relstroke
    def delete(self):
        # Remove from canvas
        try:
            if hasattr(self, "oval_id") and self.oval_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.oval_id)
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete all instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezOval object! It creates an easy oval (or circle!) on the screen and automatically handles drawing it, coloring it, and it is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy oval like this:
MyezOval = ezOval(relx1={defaults['relx1']}, rely1={defaults['rely1']}, relx2={defaults['relx2']}, rely2={defaults['rely2']}, fill="{defaults['fill']}", outline="{defaults['outline']}", relstroke={defaults['relstroke']}, scrolling={defaults['scrolling']})
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
relx1 means relative starting x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely1 means relative starting y position.
relx2 means relative ending x position.
rely2 means relative ending y position.
fill means what color the inside of the oval is. Hex codes like "#334455" work too!
outline means the color of the border line wrapping around it.
relstroke is the thickness of that outline border.
scrolling means is it allowed to scroll or is it stuck to the screen position?

Here are the functions you need:

MyezOval.hide() This function makes the oval completely invisible. It does NOT delete it.
MyezOval.show() This function makes the oval visible again if it was hidden.
MyezOval.SetPosition(relx1, rely1, relx2, rely2) This sets specific new relative coordinates to snap the oval to.
MyezOval.ChangePosition(dx1, dy1, dx2, dy2) This shifts the oval's bounding box relative to its current placement by adding or subtracting values.
MyezOval.SetStroke(new_relstroke) Directly sets the thickness of the oval's border line.
MyezOval.ChangeStroke(delta) Adds or subtracts thickness to the border line.
MyezOval.SetFill(new_fill) Changes the internal color of the oval on the fly.
MyezOval.SetOutline(new_outline) Changes the color of the border line.
MyezOval.SetScroll(scrolling=True) Sets whether the oval stays glued static to the window or moves along with canvas scrolling.
MyezOval.MouseHovering(additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0) This is super cool—it uses actual ellipse math to check if the mouse is perfectly inside the oval curves, not just a square box! You can pass offsets to tweak the detection zone. Returns True or False.
MyezOval.MouseClicked(*args) Returns True if you left-click right inside the oval shape. Awesome for round buttons or click targets.
MyezOval.delete() This completely wipes the oval from the canvas tracking system and cleans up its data to save memory.

MyezOval.Update() Probably not needed. This handles processing any shifts in sizing, position, border weight, or color changes smoothly right before a new frame updates!
"""



class ezPolygon():
    def __init__(self, points, fill="blue", outline="black",
                 relstroke=1, scrolling=True, transparency=10000):

        # [(x1,y1),(x2,y2)...]
        self.points = points

        self.fill = fill
        self.outline = outline
        self.relstroke = relstroke
        self.scrolling = scrolling
        self.transparency = transparency

        self.visibility = "normal"

        # previous states
        self.previous_points = list(points)
        self.previous_fill = fill
        self.previous_outline = outline
        self.previous_relstroke = relstroke
        self.previous_transparency = transparency
        self.previous_visibility = self.visibility

        # build initial canvas coordinates
        canvas_points = []
        for x,y in self.points:
            canvas_points.append(((x/10000)*rglobals.sq_size)+rglobals.x_offset)
            canvas_points.append(((y/10000)*rglobals.sq_size)+rglobals.y_offset)

        self.poly_id = rglobals.canvas.create_polygon(
            canvas_points,
            fill=self.fill,
            outline=self.outline,
            width=self.relstroke*(rglobals.sq_size/600)
        )
        rglobals.AllItems.add(self)
    def hide(self):
        self.visibility = "hidden"
    def show(self):
        self.visibility = "normal"
    def SetPoints(self, points):
        self.points = points
    def Move(self, dx, dy):
        self.points = [(x+dx, y+dy) for x,y in self.points]
    def SetFill(self, new_fill):
        self.fill = new_fill
    def SetOutline(self, new_outline):
        self.outline = new_outline
    def SetStroke(self, new_relstroke):
        self.relstroke = new_relstroke
    def SetTransparency(self, transparency):
        self.transparency = max(0, min(10000, transparency))
    def ChangeTransparency(self, amount):
        self.transparency = max(0, min(10000, self.transparency + amount))
    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling
    def _get_stipple(self):
        if self.transparency >= 10000:
            return ""
        elif self.transparency >= 7500:
            return "gray12"
        elif self.transparency >= 5000:
            return "gray25"
        elif self.transparency >= 2500:
            return "gray50"
        else:
            return "gray75"

    def MouseHovering(self, additional_offset_x1=0, additional_offset_y1=0,
                      additional_offset_x2=0, additional_offset_y2=0):

        x = rglobals.relmouse_x
        y = rglobals.relmouse_y

        points = self.points
        n = len(points)

        if n < 3:
            return False

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        minx = min(xs) + additional_offset_x1
        miny = min(ys) + additional_offset_y1
        maxx = max(xs) + additional_offset_x2
        maxy = max(ys) + additional_offset_y2

        if not (minx < x < maxx and miny < y < maxy):
            return False

        inside = False
        x1,y1 = points[0]

        for i in range(n+1):
            x2,y2 = points[i % n]

            if y > min(y1,y2):
                if y <= max(y1,y2):
                    if x <= max(x1,x2):
                        if y1 != y2:
                            xinters = (y-y1)*(x2-x1)/(y2-y1)+x1
                        if x1 == x2 or x <= xinters:
                            inside = not inside

            x1,y1 = x2,y2

        return inside

    def MouseClicked(self,*args):
        return rglobals.mouse_clicked['left'] and self.MouseHovering(*args)

    def Update(self):

        PointsChanged = (self.points != self.previous_points)
        StrokeChanged = (self.relstroke != self.previous_relstroke)
        ColorChanged = (self.fill != self.previous_fill or self.outline != self.previous_outline)
        TransparencyChanged = (self.transparency != self.previous_transparency)
        VisibilityChanged = (self.visibility != self.previous_visibility)

        # visibility
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.poly_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        # update polygon coords
        if PointsChanged or rglobals.WindowChanged or rglobals.ScrollChanged:

            canvas_points = []

            for x,y in self.points:

                cx = ((x/10000)*rglobals.sq_size)+rglobals.x_offset
                cy = ((y/10000)*rglobals.sq_size)+rglobals.y_offset

                if not self.scrolling:
                    cx += rglobals.scroll_x
                    cy += rglobals.scroll_y

                canvas_points.append(cx)
                canvas_points.append(cy)

            rglobals.canvas.coords(self.poly_id, *canvas_points)

        # stroke
        if StrokeChanged or rglobals.WindowChanged:
            rglobals.canvas.itemconfig(
                self.poly_id,
                width=self.relstroke*(rglobals.sq_size/600)
            )

        # colors
        if ColorChanged:
            rglobals.canvas.itemconfig(
                self.poly_id,
                fill=self.fill,
                outline=self.outline
            )

        # transparency
        if TransparencyChanged:
            rglobals.canvas.itemconfig(
                self.poly_id,
                stipple=self._get_stipple()
            )

        self._store_previous()

    def _store_previous(self):

        self.previous_points = list(self.points)
        self.previous_fill = self.fill
        self.previous_outline = self.outline
        self.previous_relstroke = self.relstroke
        self.previous_transparency = self.transparency
    def delete(self):
        # Remove polygon from canvas
        try:
            if hasattr(self, "poly_id") and self.poly_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.poly_id)
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Clear all key instance attributes
        attrs_to_clear = [
            "points", "previous_points", "fill", "previous_fill", "outline",
            "previous_outline", "relstroke", "previous_relstroke",
            "transparency", "previous_transparency", "visibility", "previous_visibility"
        ]
        for attr in attrs_to_clear:
            if hasattr(self, attr):
                try:
                    delattr(self, attr)
                except Exception:
                    pass

        # Delete any remaining instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezPolygon object! It creates an easy custom polygon on the screen out of any shape you want and automatically handles drawing it, coloring it, and it is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy polygon like this:
MyezPolygon = ezPolygon(points=[(1000,1000), (2000,1000), (1500,2000)], fill="{defaults['fill']}", outline="{defaults['outline']}", relstroke={defaults['relstroke']}, scrolling={defaults['scrolling']}, transparency={defaults['transparency']})
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
points is a list of relative (x, y) coordinate tuples, like [(x1,y1), (x2,y2), (x3,y3)...] that connect together to form your custom shape!
fill means what color the inside of the polygon is. Hex codes like "#334455" work perfectly too!
outline means the color of the lines forming the border of your shape.
relstroke is the size/thickness of that custom border outline.
scrolling means is it allowed to scroll or is it stuck to the screen position?
transparency means... exactly what it says, 10,000 is fully visible, and lower numbers stipple it out! (Tkinter polygon transparency uses that retro stippling effect)

Here are the functions you need:

MyezPolygon.hide() This function makes the polygon completely invisible. It does NOT delete it.
MyezPolygon.show() This function makes the polygon visible again if it was hidden.
MyezPolygon.SetPoints(points) This sets a brand new list of relative coordinate tuples to morph the polygon into a completely different shape.
MyezPolygon.Move(dx, dy) This shifts every single point in the polygon by a relative X and Y amount to move the entire shape together.
MyezPolygon.SetFill(new_fill) Dynamically updates the interior color of the polygon.
MyezPolygon.SetOutline(new_outline) Dynamically updates the color of the outer border lines.
MyezPolygon.SetStroke(new_relstroke) Sets the thickness of the outer border lines.
MyezPolygon.SetTransparency(transparency) Directly sets the stipple transparency to a specific value between 0 and 10,000.
MyezPolygon.ChangeTransparency(amount) Changes the stipple transparency by adding or subtracting an amount. Max is 10,000.
MyezPolygon.SetScroll(scrolling=True) Sets whether the polygon stays glued static to the screen or floats along with the canvas scroll.
MyezPolygon.MouseHovering(additional_offset_x1=0, additional_offset_y1=0, additional_offset_x2=0, additional_offset_y2=0) This is amazing—it uses actual ray-casting math to check if the mouse is perfectly inside the boundaries of your custom polygon shape! You can pass offsets to adjust the detection boundaries. Returns True or False.
MyezPolygon.MouseClicked(*args) Returns True if you left-click inside your custom polygon shape. Super useful for weirdly-shaped UI buttons or map territories!
MyezPolygon.delete() This completely wipes the polygon from the canvas and purges its attributes to immediately free up system memory.

MyezPolygon.Update() Probably not needed. This dynamic updater redraws all vertex points, checks boundaries, and updates fills or outlines simultaneously right before a frame renders!
"""



import tkinter as tk
import inspect

class ezButton():
    def __init__(self, text, relx=4300, rely=9450, command=None,
                 relwidth=1370, relheight=570, relfontsize=10,
                 anchor="nw", scrolling=True, font_color="black", background_color="white",
                 hover_font_color="black", hover_background_color="lightgray"):

        self.text = text
        self.relx = relx
        self.rely = rely
        self.relwidth = relwidth
        self.relheight = relheight
        self.relfontsize = relfontsize
        self.command = command
        self.anchor = anchor
        self.scrolling = scrolling
        self.font_color = font_color
        self.background_color = background_color
        self.hover_font_color = hover_font_color
        self.hover_background_color = hover_background_color
        self.visibility = "normal"

        # Previous states
        self.previous_relx = relx
        self.previous_rely = rely
        self.previous_relwidth = relwidth
        self.previous_relheight = relheight
        self.previous_relfontsize = relfontsize
        self.previous_text = text
        self.previous_anchor = anchor
        self.previous_visibility = self.visibility
        self.previous_command = command
        self.previous_font_color = font_color
        self.previous_background_color = background_color
        self.previous_hover_font_color = hover_font_color
        self.previous_hover_background_color = hover_background_color

        # Create button widget with colors and hover/active colors
        self.button = tk.Button(
            rglobals.canvas, 
            text=self.text, 
            command=self.command, 
            fg=self.font_color, 
            bg=self.background_color,
            activeforeground=self.hover_font_color,
            activebackground=self.hover_background_color
        )

        # Create canvas window
        self.button_window_id = rglobals.canvas.create_window(
            ((self.relx / 10000) * rglobals.sq_size) + rglobals.x_offset,
            ((self.rely / 10000) * rglobals.sq_size) + rglobals.y_offset,
            window=self.button,
            width=(self.relwidth / 10000) * rglobals.sq_size,
            height=(self.relheight / 10000) * rglobals.sq_size,
            anchor=self.anchor
        )

        # Initial font
        self.font_size = int(rglobals.sq_size * self.relfontsize * 0.002)
        self.button.config(font=("Arial", self.font_size))
        rglobals.AllItems.add(self)

    # ------------------
    # Movement / sizing / styling
    # ------------------
    def move(self, XAmount=0, YAmount=0):
        self.relx += XAmount
        self.rely += YAmount

    def SetPosition(self, relx, rely):
        self.relx = relx
        self.rely = rely

    def SetSize(self, relwidth, relheight):
        self.relwidth = relwidth
        self.relheight = relheight

    def ChangeSize(self, dw, dh):
        self.relwidth += dw
        self.relheight += dh

    def SetText(self, new_text):
        self.text = new_text

    def SetCommand(self, command):
        self.command = command

    def SetFontColor(self, color):
        self.font_color = color

    def SetBackgroundColor(self, color):
        self.background_color = color

    def SetHoverFontColor(self, color):
        self.hover_font_color = color

    def SetHoverBackgroundColor(self, color):
        self.hover_background_color = color

    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    # ------------------
    # Update
    # ------------------
    def Update(self):
        PositionChanged = (
            self.relx != self.previous_relx or
            self.rely != self.previous_rely or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        SizeChanged = (
            self.relwidth != self.previous_relwidth or
            self.relheight != self.previous_relheight or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        FontChanged = (
            self.relfontsize != self.previous_relfontsize or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        TextChanged = (self.text != self.previous_text)
        AnchorChanged = (self.anchor != self.previous_anchor)
        CommandChanged = (self.command != self.previous_command)
        VisibilityChanged = (self.visibility != self.previous_visibility)
        
        ColorChanged = (
            self.font_color != self.previous_font_color or 
            self.background_color != self.previous_background_color or
            self.hover_font_color != self.previous_hover_font_color or
            self.hover_background_color != self.previous_hover_background_color
        )
        
        # Auto show if in bounds
        in_bounds = (
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )

        # Visibility update
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.button_window_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        # Position update
        if PositionChanged or rglobals.WindowChanged or rglobals.ScrollChanged:
            x = ((self.relx / 10000) * rglobals.sq_size) + rglobals.x_offset
            y = ((self.rely / 10000) * rglobals.sq_size) + rglobals.y_offset

            if not self.scrolling:
                x += rglobals.scroll_x
                y += rglobals.scroll_y

            rglobals.canvas.coords(self.button_window_id, x, y)

        # Size update
        if SizeChanged:
            rglobals.canvas.itemconfig(
                self.button_window_id,
                width=(self.relwidth / 10000) * rglobals.sq_size,
                height=(self.relheight / 10000) * rglobals.sq_size
            )

        # Font update
        if FontChanged:
            self.font_size = int(rglobals.sq_size * self.relfontsize * 0.002)
            self.button.config(font=("Arial", self.font_size))

        # Text update
        if TextChanged:
            self.button.config(text=self.text)

        # Command update
        if CommandChanged:
            self.button.config(command=self.command)

        # Color update (including hover/active colors)
        if ColorChanged:
            self.button.config(
                fg=self.font_color, 
                bg=self.background_color,
                activeforeground=self.hover_font_color,
                activebackground=self.hover_background_color
            )

        # Anchor update
        if AnchorChanged:
            rglobals.canvas.itemconfig(self.button_window_id, anchor=self.anchor)

        # Auto hide if out of bounds
        if not in_bounds and self.visibility == "normal":
            self.hide()

        self._store_previous()

    # ------------------
    # Store previous
    # ------------------
    def _store_previous(self):
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfontsize = self.relfontsize
        self.previous_text = self.text
        self.previous_anchor = self.anchor
        self.previous_command = self.command
        self.previous_font_color = self.font_color
        self.previous_background_color = self.background_color
        self.previous_hover_font_color = self.hover_font_color
        self.previous_hover_background_color = self.hover_background_color

    def delete(self):
        try:
            if hasattr(self, "button_window_id") and self.button_window_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.button_window_id)
        except Exception:
            pass

        try:
            if hasattr(self, "button") and self.button:
                self.button.destroy()
        except Exception:
            pass

        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        attrs_to_clear = [
            "button", "button_window_id", "text", "command",
            "relx", "rely", "relwidth", "relheight", "relfontsize",
            "anchor", "scrolling", "visibility", "font_size", "font_color", "background_color",
            "hover_font_color", "hover_background_color",
            "previous_relx", "previous_rely", "previous_relwidth",
            "previous_relheight", "previous_relfontsize", "previous_text",
            "previous_anchor", "previous_visibility", "previous_command",
            "previous_font_color", "previous_background_color",
            "previous_hover_font_color", "previous_hover_background_color"
        ]
        for attr in attrs_to_clear:
            if hasattr(self, attr):
                try:
                    delattr(self, attr)
                except Exception:
                    pass

        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        import gc
        gc.collect()

    def __repr__(self):
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezButton object! It creates a fully working, clickable Tkinter button inside your canvas and automatically handles scaling it, placing it, and OPTIMIZING it behind the scenes! No performance headaches here.
You can create an easy button like this:
MyezButton = ezButton(text="Click Me!", relx={defaults['relx']}, rely={defaults['rely']}, command=my_function_name, relwidth={defaults['relwidth']}, relheight={defaults['relheight']}, relfontsize={defaults['relfontsize']}, anchor="{defaults['anchor']}", scrolling={defaults['scrolling']}, font_color="{defaults['font_color']}", background_color="{defaults['background_color']}", hover_font_color="{defaults['hover_font_color']}", hover_background_color="{defaults['hover_background_color']}")
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
text is whatever message or label you want stamped right onto the front of the button.
relx means relative x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely means relative y position.
command is the name of the function you want to execute when someone clicks the button (leave off the parenthesis () when passing it!).
relwidth is the relative width of the button box.
relheight is the relative height of the button box.
relfontsize controls the relative scale of the button text so it changes size nicely with your window scale.
anchor means north east south west. It must be n, ne, e, se, s, sw, w, nw, or center. It dictates which corner or side of the button aligns with your (relx, rely) spot.
scrolling means is it allowed to scroll or is it stuck static to the screen position?
font_color changes the color of the text (e.g., 'black', 'red', '#FFFFFF').
background_color changes the background fill of the button widget.
hover_font_color changes the text color when the button is actively being clicked/hovered.
hover_background_color changes the background fill color when the button is actively being clicked/hovered.

Here are the functions you need:

MyezButton.move(XAmount=0, YAmount=0) This function shifts the button's position relative to where it currently is.
MyezButton.SetPosition(relx, rely) This snaps the button immediately to a brand new exact relative coordinate.
MyezButton.SetSize(relwidth, relheight) This directly resizes the button dimensions using absolute relative values.
MyezButton.ChangeSize(dw, dh) This scales the button's width and height up or down from its current size.
MyezButton.SetText(new_text) Change the text display on the button dynamically.
MyezButton.SetCommand(command) Swaps out what function runs when the button gets clicked on the fly!
MyezButton.SetFontColor(color) Changes the button's font color dynamically.
MyezButton.SetBackgroundColor(color) Changes the button's background color dynamically.
MyezButton.SetHoverFontColor(color) Changes the hover text color dynamically.
MyezButton.SetHoverBackgroundColor(color) Changes the hover background color dynamically.
MyezButton.hide() This function makes the button completely invisible. It does NOT delete it.
MyezButton.show() This makes the button pop back onto the screen if it was hidden.
MyezButton.SetScroll(scrolling=True) Sets whether the button rolls along with canvas scroll movements or stays glued in place.
MyezButton.delete() This completely destroys the Tkinter widget, rips it off the canvas window, and forces garbage collection to keep things clean.

MyezButton.Update() Probably not needed. This recalculates positions, window scales, text fonts, colors, and callback bindings automatically behind the scenes per frame!
"""

class ezMessage():
    def __init__(self, text, relx=1500, rely=400, relwidth=3000,
                 relfont_size=10000, font_name="Arial",
                 anchor="nw", scrolling=True, background=None):

        self.text = text
        self.relx = relx
        self.rely = rely
        self.relwidth = relwidth
        self.relfont_size = relfont_size
        self.font_name = font_name
        self.anchor = anchor
        self.scrolling = scrolling
        self.background = background

        self.visibility = "normal"

        # previous states
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relfont_size = self.relfont_size
        self.previous_text = self.MyText
        self.previous_anchor = self.anchor
        self.previous_background = self.background
        self.previous_visibility = self.visibility

        # compute font size
        self.font_size = int((rglobals.sq_size - 4.36842) *
                             rglobals.font_scale *
                             self.relfont_size)

        # create widget
        self.message_widget = tk.Message(
            rglobals.canvas,
            text=self.MyText,
            font=(self.font_name, self.font_size),
            width=int((self.relwidth/10000)*rglobals.sq_size),
            anchor=self.anchor,
            bg=self.background
        )

        # place on canvas
        self.message_id = rglobals.canvas.create_window(
            int((self.relx/10000)*rglobals.sq_size)+rglobals.x_offset,
            int((self.rely/10000)*rglobals.sq_size)+rglobals.y_offset,
            window=self.message_widget,
            anchor=self.anchor
        )
        rglobals.AllItems.add(self)
    def SetBackground(self, new_bg=None):
        self.background = new_bg

    def move(self,XAmount=0,YAmount=0):
        self.relx += XAmount
        self.rely += YAmount

    def SetPosition(self,relx=0,rely=0):
        self.relx = relx
        self.rely = rely

    def SetSize(self,relwidth):
        self.relwidth = relwidth

    def ChangeSize(self,relwidth_amount):
        self.relwidth += relwidth_amount

    def SetText(self,NewText):
        self.text = NewText

    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    def MouseHovering(self, *offsets):

        bbox = rglobals.canvas.bbox(self.message_id)
        if bbox is None:
            return False

        x1, y1, x2, y2 = bbox

        x1 = ((x1 - rglobals.x_offset) / rglobals.sq_size) * 10000
        y1 = ((y1 - rglobals.y_offset) / rglobals.sq_size) * 10000
        x2 = ((x2 - rglobals.x_offset) / rglobals.sq_size) * 10000
        y2 = ((y2 - rglobals.y_offset) / rglobals.sq_size) * 10000

        additional_offset_x1, additional_offset_y1, additional_offset_x2, additional_offset_y2 = offsets if offsets else (0,0,0,0)

        x1 += additional_offset_x1
        y1 += additional_offset_y1
        x2 += additional_offset_x2
        y2 += additional_offset_y2

        return x1 < rglobals.relmouse_x < x2 and y1 < rglobals.relmouse_y < y2

    def MouseClicked(self,*args):
        return rglobals.mouse_clicked['left'] and self.MouseHovering(*args)

    # --- optimized update ---
    def Update(self):

        PositionChanged = (
            self.relx != self.previous_relx or
            self.rely != self.previous_rely or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        WidthChanged = (
            self.relwidth != self.previous_relwidth or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        FontChanged = (
            self.relfont_size != self.previous_relfont_size or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        TextChanged = (self.text != self.previous_text)
        AnchorChanged = (self.anchor != self.previous_anchor)
        BackgroundChanged = (self.background != self.previous_background)
        VisibilityChanged = (self.visibility != self.previous_visibility)

        # visibility update
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.message_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        # auto bounds hide
        in_bounds = (
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )

        if not in_bounds:
            self.hide()

        # position update
        if PositionChanged or rglobals.WindowChanged or rglobals.ScrollChanged:

            x = int((self.relx/10000)*rglobals.sq_size)+rglobals.x_offset
            y = int((self.rely/10000)*rglobals.sq_size)+rglobals.y_offset

            if not self.scrolling:
                x += rglobals.scroll_x
                y += rglobals.scroll_y

            rglobals.canvas.coords(self.message_id, x, y)

        # font or width update
        if WidthChanged or FontChanged or AnchorChanged or rglobals.WindowChanged:

            self.font_size = int((rglobals.sq_size - 4.36842) *
                                 rglobals.font_scale *
                                 self.relfont_size)

            self.message_widget.config(
                font=(self.font_name, self.font_size),
                width=int((self.relwidth/10000)*rglobals.sq_size),
                anchor=self.anchor
            )

        # text update
        if TextChanged:
            self.message_widget.config(text=self.text)

        # background update
        if BackgroundChanged:
            self.message_widget.config(bg=self.background)

        self._store_previous()

    def _store_previous(self):
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relfont_size = self.relfont_size
        self.previous_text = self.text
        self.previous_anchor = self.anchor
        self.previous_background = self.background
    def delete(self):
        # Remove from canvas
        try:
            if hasattr(self, "message_id") and self.message_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.message_id)
        except Exception:
            pass

        # Destroy the widget
        try:
            if hasattr(self, "message_widget") and self.message_widget:
                self.message_widget.destroy()
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete all instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezMessage object! It creates an easy multi-line text block on the screen using Tkinter's Message widget. It automatically wraps text nicely, scales it, and is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy message block like this:
MyezMessage = ezMessage(text="Your long paragraph text here...", relx={defaults['relx']}, rely={defaults['rely']}, relwidth={defaults['relwidth']}, relfont_size={defaults['relfont_size']}, font_name="{defaults['font_name']}", anchor="{defaults['anchor']}", scrolling={defaults['scrolling']}, background={defaults['background']})
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
text is the paragraph or message you want to display. It will wrap lines automatically!
relx means relative x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely means relative y position.
relwidth is the relative width boundary where the text is allowed to stretch before it wraps down to a new line.
relfont_size is the relative font scale that keeps your text sized right on different screen layouts.
font_name is the type of font family you want (like Arial or Times New Roman).
anchor means north east south west. It must be n, ne, e, se, s, sw, w, nw, or center. It changes where the text block is anchored relative to its position point.
scrolling means is it allowed to scroll or is it stuck static to the screen position?
background sets a custom solid background color behind the text block (defaults to None for a transparent layout look).

Here are the functions you need:

MyezMessage.SetBackground(new_bg=None) Dynamically changes the background color block behind your text.
MyezMessage.move(XAmount=0, YAmount=0) This function shifts the message block position by a relative amount.
MyezMessage.SetPosition(relx=0, rely=0) This snaps the message block directly to a new absolute relative position.
MyezMessage.SetSize(relwidth) Directly sets a new relative width layout restriction for text-wrapping.
MyezMessage.ChangeSize(relwidth_amount) Expands or shrinks the wrapping width boundary on the fly.
MyezMessage.SetText(NewText) Swaps out what paragraph or message the widget is currently displaying.
MyezMessage.hide() This function makes the text block completely invisible. It does NOT delete it.
MyezMessage.show() This makes the message block reappear if it was hidden.
MyezMessage.SetScroll(scrolling=True) Sets whether the text rolls along with canvas scroll movements or stays glued in place.
MyezMessage.MouseHovering(*offsets) Checks if the user's mouse is hovering within the bounding box of the message paragraph. You can pass offsets to loosen or tighten the hover zone. Returns True or False.
MyezMessage.MouseClicked(*args) Returns True if the left mouse button clicks inside the boundary of the text block.
MyezMessage.delete() This completely tears down the Message widget, removes its window from the canvas tracker, and cleans up memory immediately.

MyezMessage.Update() Probably not needed. This syncs up all position, auto-wrapping widths, font resizing, and background updates behind the scenes per frame!
"""

class ezScroll():
    def __init__(self, rel_v_width=15000, rel_v_height=15000):

        self.rel_v_width = rel_v_width
        self.rel_v_height = rel_v_height

        self.allow_v = True
        self.allow_h = True

        # scrollbar visible state
        self.v_visible = False
        self.h_visible = False

        # previous states
        self.previous_rel_v_width = rel_v_width
        self.previous_rel_v_height = rel_v_height
        self.previous_allow_v = self.allow_v
        self.previous_allow_h = self.allow_h
        self.previous_final_w = None
        self.previous_final_h = None

        # create widgets
        self.v_bar = tk.Scrollbar(rglobals.root, orient="vertical", command=rglobals.canvas.yview)
        self.h_bar = tk.Scrollbar(rglobals.root, orient="horizontal", command=rglobals.canvas.xview)

        rglobals.canvas.config(
            yscrollcommand=self.v_bar.set,
            xscrollcommand=self.h_bar.set
        )

        # initial draw
        self._recalculate()
        rglobals.AllItems.add(self)
    def SetSize(self, rel_v_width, rel_v_height):
        self.rel_v_width = rel_v_width
        self.rel_v_height = rel_v_height

    def ChangeSize(self, dw, dh):
        self.rel_v_width += dw
        self.rel_v_height += dh

    def HideVerticalScroll(self):
        self.allow_v = False

    def ShowVerticalScroll(self):
        self.allow_v = True

    def HideHorizontalScroll(self):
        self.allow_h = False

    def ShowHorizontalScroll(self):
        self.allow_h = True

    def _recalculate(self):

        pixel_v_w = int((self.rel_v_width / 10000) * rglobals.sq_size)
        pixel_v_h = int((self.rel_v_height / 10000) * rglobals.sq_size)

        # ---- vertical ----
        need_v = self.allow_v and pixel_v_h > rglobals.window_height

        if need_v and not self.v_visible:
            self.v_bar.pack(side="right", fill="y", before=rglobals.canvas)
            self.v_visible = True

        elif not need_v and self.v_visible:
            self.v_bar.pack_forget()
            rglobals.canvas.yview_moveto(0)
            self.v_visible = False

        # ---- horizontal ----
        need_h = self.allow_h and pixel_v_w > rglobals.window_width

        if need_h and not self.h_visible:
            self.h_bar.pack(side="bottom", fill="x", before=rglobals.canvas)
            self.h_visible = True

        elif not need_h and self.h_visible:
            self.h_bar.pack_forget()
            rglobals.canvas.xview_moveto(0)
            self.h_visible = False

        final_w = pixel_v_w if self.h_visible else rglobals.window_width
        final_h = pixel_v_h if self.v_visible else rglobals.window_height

        if final_w != self.previous_final_w or final_h != self.previous_final_h:

            rglobals.canvas.config(scrollregion=(0, 0, final_w, final_h))

            self.previous_final_w = final_w
            self.previous_final_h = final_h

    def Update(self):

        SizeChanged = (
            self.rel_v_width != self.previous_rel_v_width or
            self.rel_v_height != self.previous_rel_v_height
        )

        VisibilityChanged = (
            self.allow_v != self.previous_allow_v or
            self.allow_h != self.previous_allow_h
        )

        if not (SizeChanged or VisibilityChanged or rglobals.WindowChanged):
            return

        self._recalculate()

        self._store_previous()

    def _store_previous(self):

        self.previous_rel_v_width = self.rel_v_width
        self.previous_rel_v_height = self.rel_v_height
        self.previous_allow_v = self.allow_v
        self.previous_allow_h = self.allow_h
    def delete(self):
        # Remove scrollbars from canvas/root
        try:
            if hasattr(self, "v_bar") and self.v_bar:
                self.v_bar.pack_forget()
                self.v_bar.destroy()
        except Exception:
            pass

        try:
            if hasattr(self, "h_bar") and self.h_bar:
                self.h_bar.pack_forget()
                self.h_bar.destroy()
        except Exception:
            pass

        # Remove from global AllItems
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete all instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezScroll object! It hooks up automatic vertical and horizontal scrollbars directly to your root window and canvas. It handles tracking bounds, matching scales, and it is OPTIMIZED automatically, only rendering bars when your canvas size overflows the window! So don't worry about optimizations.
You can create an easy scroll setup like this:
MyezScroll = ezScroll(rel_v_width={defaults['rel_v_width']}, rel_v_height={defaults['rel_v_height']})
WOAH lots of stuff there! Don't worry, most of it's not necessary, but let's explain it!
rel_v_width is the relative total target width of your virtual canvas area. Setting it over 10,000 means the world is wider than a single screen!
rel_v_height is the relative total target height of your virtual canvas area. Setting it over 10,000 means the world is taller than a single screen!

Here are the functions you need:

MyezScroll.SetSize(rel_v_width, rel_v_height) This directly updates the size limits of your virtual scrolling world area.
MyezScroll.ChangeSize(dw, dh) This expands or shrinks the scrolling canvas area by adding or subtracting values from the current width and height limits.
MyezScroll.HideVerticalScroll() Forcefully disables and packs away the vertical scrollbar, locking y-axis scrolling.
MyezScroll.ShowVerticalScroll() Re-enables the vertical scrollbar check so it can pop out automatically if the layout bounds overflow.
MyezScroll.HideHorizontalScroll() Forcefully disables and packs away the horizontal scrollbar, locking x-axis scrolling.
MyezScroll.ShowHorizontalScroll() Re-enables the horizontal scrollbar check so it can dynamically pop up when your width goes past window bounds.
MyezScroll.delete() This safely unbinds, hides, and completely obliterates both scrollbar widgets from the root window, cleaning up tracking references to save system memory.

MyezScroll.Update() Probably not needed. This checks canvas boundaries, window resize events, and packs or hides the layout bars dynamically behind the scenes per frame!
"""


class ezInputTextBox():
    def __init__(self, initial_text="", relx=1500, rely=400, relwidth=5000, relheight=2000,
                 relfont_size=1000, font_name="Arial", anchor="nw", scrolling=True):

        self.text = initial_text
        self.relx = relx
        self.rely = rely
        self.relwidth = relwidth
        self.relheight = relheight
        self.relfont_size = relfont_size
        self.font_name = font_name
        self.anchor = anchor
        self.scrolling = scrolling

        self.visibility = "normal"

        # --- previous states ---
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfont_size = self.relfont_size
        self.previous_text = self.text
        self.previous_anchor = self.anchor
        self.previous_font_name = self.font_name
        self.previous_visibility = self.visibility

        # compute font size
        self.font_size = int((rglobals.sq_size - 4.36842) *
                             rglobals.font_scale *
                             self.relfont_size)

        # --- create widget ---
        self.text_widget = tk.Text(
            rglobals.canvas,
            font=(self.font_name, self.font_size),
            wrap="word"
        )

        self.text_widget.insert("1.0", self.text)

        # scrollbar
        self.scrollbar = tk.Scrollbar(
            rglobals.canvas,
            orient="vertical",
            command=self.text_widget.yview
        )

        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        # --- compute initial sizes ---
        initial_w = int((self.relwidth / 10000) * rglobals.sq_size)
        initial_h = int((self.relheight / 10000) * rglobals.sq_size)

        # create windows
        self.text_window_id = rglobals.canvas.create_window(
            ((self.relx / 10000) * rglobals.sq_size) + rglobals.x_offset,
            ((self.rely / 10000) * rglobals.sq_size) + rglobals.y_offset,
            window=self.text_widget,
            anchor=self.anchor,
            width=initial_w,   # <-- ADDED HERE
            height=initial_h   # <-- ADDED HERE
        )

        self.scroll_window_id = rglobals.canvas.create_window(
            ((self.relx / 10000) * rglobals.sq_size) + rglobals.x_offset + initial_w,
            ((self.rely / 10000) * rglobals.sq_size) + rglobals.y_offset,
            window=self.scrollbar,
            anchor="nw",
            height=initial_h   # <-- ADDED HERE (Scrollbars only need height)
        )

        self.Update()
        rglobals.AllItems.add(self)
    def GetText(self):
        return self.text_widget.get("1.0", "end-1c")
    def SetText(self, new_text):
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", new_text)
        self.text = new_text
    def move(self, XAmount=0, YAmount=0):
        self.relx += XAmount
        self.rely += YAmount

    def SetPosition(self, relx, rely):
        self.relx = relx
        self.rely = rely

    def SetSize(self, relwidth, relheight):
        self.relwidth = relwidth
        self.relheight = relheight

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    # --- optimized update ---
    def Update(self):

        PositionChanged = (
            self.relx != self.previous_relx or
            self.rely != self.previous_rely or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        SizeChanged = (
            self.relwidth != self.previous_relwidth or
            self.relheight != self.previous_relheight or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        FontChanged = (
            self.relfont_size != self.previous_relfont_size or
            self.font_name != self.previous_font_name or
            rglobals.sq_size != rglobals.previous_sq_size
        )

        AnchorChanged = (self.anchor != self.previous_anchor)
        VisibilityChanged = (self.visibility != self.previous_visibility)

        # only read widget text when needed
        current_text = self.GetText()
        TextChanged = (current_text != self.previous_text)

        # --- bounds visibility ---
        in_bounds = (
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )

        if not in_bounds and self.visibility == "normal":
            self.hide()

        # --- visibility update ---
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.text_window_id, state=self.visibility)
            rglobals.canvas.itemconfig(self.scroll_window_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous(current_text)
            return

        # --- compute sizes ---
        new_w = int((self.relwidth/10000)*rglobals.sq_size)
        new_h = int((self.relheight/10000)*rglobals.sq_size)

        # --- position update ---
        if PositionChanged or rglobals.WindowChanged or rglobals.ScrollChanged:

            x = int((self.relx/10000)*rglobals.sq_size) + rglobals.x_offset
            y = int((self.rely/10000)*rglobals.sq_size) + rglobals.y_offset

            if not self.scrolling:
                x += rglobals.scroll_x
                y += rglobals.scroll_y

            rglobals.canvas.coords(self.text_window_id, x, y)
            rglobals.canvas.coords(self.scroll_window_id, x + new_w, y)

        # --- size update ---
        if SizeChanged:

            rglobals.canvas.itemconfig(
                self.text_window_id,
                width=new_w,
                height=new_h
            )

            rglobals.canvas.itemconfig(
                self.scroll_window_id,
                height=new_h
            )

        # --- font update ---
        if FontChanged:

            self.font_size = int((rglobals.sq_size - 4.36842) *
                                 rglobals.font_scale *
                                 self.relfont_size)

            self.text_widget.config(font=(self.font_name, self.font_size))

        # --- text update ---
        if TextChanged:
            self.text = current_text

        # store previous
        self._store_previous(current_text)

    def _store_previous(self, current_text):

        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfont_size = self.relfont_size
        self.previous_anchor = self.anchor
        self.previous_font_name = self.font_name
        self.previous_text = current_text
    def delete(self):
        import gc

        # Remove from canvas
        try:
            if hasattr(self, "text_window_id") and self.text_window_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.text_window_id)
            if hasattr(self, "scroll_window_id") and self.scroll_window_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.scroll_window_id)
        except Exception:
            pass

        # Destroy widgets
        try:
            if hasattr(self, "text_widget") and self.text_widget:
                self.text_widget.destroy()
            if hasattr(self, "scrollbar") and self.scrollbar:
                self.scrollbar.destroy()
        except Exception:
            pass

        # Remove from global tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete all instance attributes
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezInputTextBox object! It creates an easy, scrollable multi-line text input field on the screen using Tkinter's Text and Scrollbar widgets. It automatically handles scaling, placement, word wrapping, and is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy input text box like this:
MyezInputTextBox = ezInputTextBox(initial_text="{defaults['initial_text']}", relx={defaults['relx']}, rely={defaults['rely']}, relwidth={defaults['relwidth']}, relheight={defaults['relheight']}, relfont_size={defaults['relfont_size']}, font_name="{defaults['font_name']}", anchor="{defaults['anchor']}", scrolling={defaults['scrolling']})
WOAH that's a lot of information! Don't worry, most of it's not necessary, but let's go over them!
initial_text is whatever text or placeholder message you want already sitting in the box when it spawns.
relx means relative starting x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely means relative starting y position.
relwidth is the relative width of your input box area.
relheight is the relative height of your input box area.
relfont_size is the relative font scale that keeps the typed text looking proportional on any screen layout.
font_name is the font style used inside the box (like Arial, Times New Roman, or Liberation Sans).
anchor means north east south west. It must be n, ne, e, se, s, sw, w, nw, or center. It changes where the input box is anchored relative to its position point.
scrolling means is the whole text box allowed to move when the canvas rolls, or is it stuck static to the screen overlay?

Here are the functions you need:

MyezInputTextBox.GetText() This is the big one! Returns everything currently typed inside the input box as a standard clean string.
MyezInputTextBox.SetText(new_text) Completely wipes out whatever text is inside the input field and replaces it with your new string.
MyezInputTextBox.move(XAmount=0, YAmount=0) This function shifts the input text box and its attached scrollbar relative to its current placement.
MyezInputTextBox.SetPosition(relx, rely) Snaps the text field directly to a new absolute relative position on the map.
MyezInputTextBox.SetSize(relwidth, relheight) Resizes the boundaries of your input frame and syncs up the side vertical scrollbar length.
MyezInputTextBox.SetScroll(scrolling=True) Sets whether the text box rolls along with canvas layout movements or stays glued in place.
MyezInputTextBox.hide() This function makes the input field and its scrollbar completely invisible. It does NOT delete them or lose what's typed inside.
MyezInputTextBox.show() This makes the input box pop back onto the screen if it was hidden.
MyezInputTextBox.delete() This completely tears down the internal text widget, unbinds the canvas layout windows, destroys the scrollbar, and cleans up memory immediately.

MyezInputTextBox.Update() Probably not needed. This syncs up typed input changes, position math, relative widget boundaries, and responsive font resizing automatically behind the scenes per frame!
"""


class ezInputText():
    def __init__(self, default_text="", relx=2000, rely=2000, relwidth=3000, relheight=600,
                 relfontsize=1000, font_name="Arial", scrolling=True):

        self.default_text = default_text
        self.text = default_text
        self.relx = relx
        self.rely = rely
        self.relwidth = relwidth
        self.relheight = relheight
        self.relfontsize = relfontsize
        self.font_name = font_name
        self.scrolling = scrolling

        # visibility
        self.visibility = "normal"

        # previous states
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfontsize = self.relfontsize
        self.previous_text = self.text
        self.previous_font_name = self.font_name
        self.previous_visibility = self.visibility

        # create Entry widget
        self.entry = tk.Entry(
            rglobals.canvas,
            font=(self.font_name, int(rglobals.sq_size * self.relfontsize * 0.002))
        )
        self.entry.insert(0, self.default_text)

        # place Entry on canvas
        self.entry_window_id = rglobals.canvas.create_window(
            (self.relx/10000)*rglobals.sq_size + rglobals.x_offset,
            (self.rely/10000)*rglobals.sq_size + rglobals.y_offset,
            window=self.entry,
            width=(self.relwidth/10000)*rglobals.sq_size,
            height=(self.relheight/10000)*rglobals.sq_size,
            anchor="nw"
        )
        rglobals.AllItems.add(self)
    # --- Move / Resize ---
    def move(self, XAmount=0, YAmount=0):
        self.relx += XAmount
        self.rely += YAmount

    def SetPosition(self, relx, rely):
        self.relx = relx
        self.rely = rely

    def SetSize(self, relwidth, relheight):
        self.relwidth = relwidth
        self.relheight = relheight

    def ChangeSize(self, dw, dh):
        self.relwidth += dw
        self.relheight += dh

    # --- Text access ---
    def GetText(self):
        return self.entry.get()

    def SetText(self, new_text):
        self.entry.delete(0, "end")
        self.entry.insert(0, new_text)
        self.text = new_text

    # --- visibility ---
    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    # --- optimized Update ---
    def Update(self):
        PositionChanged = (self.relx != self.previous_relx or self.rely != self.previous_rely)
        SizeChanged = (self.relwidth != self.previous_relwidth or self.relheight != self.previous_relheight)
        FontChanged = (self.relfontsize != self.previous_relfontsize or self.font_name != self.previous_font_name)
        TextChanged = (self.text != self.previous_text)
        VisibilityChanged = (self.visibility != self.previous_visibility)

        # update visibility
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.entry_window_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        # auto-hide if out of bounds
        in_bounds = (
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )
        if not in_bounds:
            self.hide()

        # update position & size
        if PositionChanged or SizeChanged or rglobals.WindowChanged or rglobals.ScrollChanged:
            x = (self.relx/10000)*rglobals.sq_size + rglobals.x_offset
            y = (self.rely/10000)*rglobals.sq_size + rglobals.y_offset
            if not self.scrolling:
                x += rglobals.scroll_x
                y += rglobals.scroll_y

            rglobals.canvas.coords(self.entry_window_id, x, y)
            rglobals.canvas.itemconfig(
                self.entry_window_id,
                width=(self.relwidth/10000)*rglobals.sq_size,
                height=(self.relheight/10000)*rglobals.sq_size
            )

        # update font size if changed
        if FontChanged or SizeChanged or rglobals.WindowChanged:
            self.entry.config(font=(self.font_name, int(rglobals.sq_size * self.relfontsize * 0.002)))

        # update text if changed
        if TextChanged:
            self.entry.delete(0, "end")
            self.entry.insert(0, self.text)

        self._store_previous()

    def _store_previous(self):
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfontsize = self.relfontsize
        self.previous_text = self.text
        self.previous_font_name = self.font_name
        self.previous_visibility = self.visibility
    def delete(self):
        # Remove Entry widget from canvas
        try:
            if hasattr(self, "entry_window_id") and self.entry_window_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.entry_window_id)
        except Exception:
            pass

        # Destroy the Entry widget itself
        try:
            if hasattr(self, "entry") and self.entry:
                self.entry.destroy()
        except Exception:
            pass

        # Remove from global AllItems
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete all instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezInputText object! It creates an easy, single-line text input field on the screen using Tkinter's Entry widget. It automatically handles scaling, placement, and is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy input text field like this:
MyezInputText = ezInputText(default_text="{defaults['default_text']}", relx={defaults['relx']}, rely={defaults['rely']}, relwidth={defaults['relwidth']}, relheight={defaults['relheight']}, relfontsize={defaults['relfontsize']}, font_name="{defaults['font_name']}", scrolling={defaults['scrolling']})
WOAH that's a lot of information! Don't worry, most of it's not necessary, but let's go over them!
default_text is whatever initial text or placeholder message you want already filled inside the box when it spawns.
relx means relative starting x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely means relative starting y position.
relwidth is the relative width of your input line area.
relheight is the relative height of your input line area.
relfontsize controls the relative font scale so your typed text looks nice and fits neatly inside the field on any screen scale.
font_name is the font style used inside the field (like Arial, Comic Sans, or Helvetica).
scrolling means is the text entry field allowed to move when the canvas scrolls, or is it stuck static to the screen layout overlay?

Here are the functions you need:

MyezInputText.GetText() This is the big one! Returns everything currently typed inside the single-line input field as a standard clean string.
MyezInputText.SetText(new_text) Completely clears whatever text is currently inside the input field and replaces it with your new string.
MyezInputText.move(XAmount=0, YAmount=0) This function shifts the input field's position relative to its current placement on the canvas.
MyezInputText.SetPosition(relx, rely) Snaps the input line directly to a new absolute relative coordinate on the screen.
MyezInputText.SetSize(relwidth, relheight) Resizes the outer frame boundaries of your input box.
MyezInputText.ChangeSize(dw, dh) Scales the entry field's width and height up or down from its current size.
MyezInputText.hide() This function makes the text entry field completely invisible. It does NOT delete it or lose what's typed inside.
MyezInputText.show() This makes the input box pop back onto the screen if it was hidden.
MyezInputText.SetScroll(scrolling=True) Sets whether the input field moves dynamically along with canvas scroll movements or stays glued in place.
MyezInputText.delete() This completely destroys the internal Entry widget, removes its window from the canvas tracker, and handles memory cleanup immediately.

MyezInputText.Update() Probably not needed. This syncs up position shifts, relative dimension boundaries, font scaling, and dynamic text resets behind the scenes automatically per frame!
"""




class ezCheckBox():
    def __init__(self, text, relx=5000, rely=5000, relwidth=2000, relheight=500, 
                 relfontsize=10, initial_state=False, command=None, scrolling=True):
        self.text = text
        self.relx = relx
        self.rely = rely
        self.relwidth = relwidth
        self.relheight = relheight
        self.relfontsize = relfontsize
        self.command = command
        self.scrolling = scrolling
        self.visibility = "normal"

        # Checkbox state variable
        self.var = tk.BooleanVar(value=initial_state)

        # Previous states
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_text = self.text
        self.previous_relfontsize = self.relfontsize
        self.previous_state = self.var.get()
        self.previous_visibility = self.visibility

        # Create Tkinter Checkbutton
        self.checkbox = tk.Checkbutton(
            rglobals.canvas,
            text=self.text,
            variable=self.var,
            command=self.command,
            anchor="w"
        )
        self.checkbox.config(font=("Arial", int(rglobals.sq_size * self.relfontsize * 0.002)))

        # Place on canvas
        self.checkbox_window_id = rglobals.canvas.create_window(
            (self.relx/10000)*rglobals.sq_size + rglobals.x_offset,
            (self.rely/10000)*rglobals.sq_size + rglobals.y_offset,
            window=self.checkbox,
            width=(self.relwidth/10000)*rglobals.sq_size,
            height=(self.relheight/10000)*rglobals.sq_size,
            anchor="nw"
        )
        rglobals.AllItems.add(self)
    # --- basic setters/getters ---
    def get(self):
        return self.var.get()

    def set(self, state=True):
        self.var.set(state)

    def move(self, XAmount=0, YAmount=0):
        self.relx += XAmount
        self.rely += YAmount

    def SetPosition(self, relx, rely):
        self.relx = relx
        self.rely = rely

    def SetSize(self, relwidth, relheight):
        self.relwidth = relwidth
        self.relheight = relheight

    def ChangeSize(self, dw, dh):
        self.relwidth += dw
        self.relheight += dh

    def SetText(self, new_text):
        self.text = new_text

    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    # --- optimized update ---
    def Update(self):
        PositionChanged = (self.relx != self.previous_relx or self.rely != self.previous_rely)
        SizeChanged = (self.relwidth != self.previous_relwidth or self.relheight != self.previous_relheight)
        FontChanged = (self.relfontsize != self.previous_relfontsize)
        TextChanged = (self.text != self.previous_text)
        StateChanged = (self.var.get() != self.previous_state)
        VisibilityChanged = (self.visibility != self.previous_visibility)

        # Update visibility
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.checkbox_window_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        # Auto-hide if out of bounds
        in_bounds = (
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )
        if not in_bounds and self.visibility == "normal":
            self.hide()

        # Update position & size
        if PositionChanged or SizeChanged or rglobals.WindowChanged or rglobals.ScrollChanged:
            x = (self.relx/10000)*rglobals.sq_size + rglobals.x_offset
            y = (self.rely/10000)*rglobals.sq_size + rglobals.y_offset
            if not self.scrolling:
                x += rglobals.scroll_x
                y += rglobals.scroll_y

            rglobals.canvas.coords(self.checkbox_window_id, x, y)
            rglobals.canvas.itemconfig(
                self.checkbox_window_id,
                width=(self.relwidth/10000)*rglobals.sq_size,
                height=(self.relheight/10000)*rglobals.sq_size
            )

        # Update font & text
        if FontChanged or TextChanged or rglobals.WindowChanged:
            self.checkbox.config(
                text=self.text,
                font=("Arial", int(rglobals.sq_size * self.relfontsize * 0.002))
            )

        # Store previous states
        self._store_previous()

    def _store_previous(self):
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_text = self.text
        self.previous_relfontsize = self.relfontsize
        self.previous_state = self.var.get()
        self.previous_visibility = self.visibility
    def delete(self):
        # Remove the Checkbutton from the canvas
        try:
            if hasattr(self, "checkbox_window_id") and self.checkbox_window_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.checkbox_window_id)
        except Exception:
            pass

        # Destroy the Tkinter Checkbutton widget
        try:
            if hasattr(self, "checkbox") and self.checkbox:
                self.checkbox.destroy()
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Clear the BooleanVar
        try:
            if hasattr(self, "var") and self.var:
                del self.var
        except Exception:
            pass

        # Delete all other instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezCheckbox object! It creates an easy, interactive toggle checkbox on the screen using Tkinter's Checkbutton widget. It automatically handles scaling, labels, click events, and is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy checkbox like this:
MyezCheckbox = ezCheckbox(text="Enable Feature", relx={defaults['relx']}, rely={defaults['rely']}, relwidth={defaults['relwidth']}, relheight={defaults['relheight']}, relfontsize={defaults['relfontsize']}, initial_state={defaults['initial_state']}, command=my_function_name, scrolling={defaults['scrolling']})
WOAH that's a lot of information! Don't worry, most of it's not necessary, but let's go over them!
text is the label string displayed right next to the clickable toggle box.
relx means relative starting x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely means relative starting y position.
relwidth is the relative total width allocated for the checkbox and its label text together.
relheight is the relative height of the checkbox click frame.
relfontsize controls the relative font scale so the text scales cleanly along with window size changes.
initial_state sets whether the checkbox starts out unchecked (False) or checked (True).
command is an optional function to run instantly every single time the box gets clicked or toggled.
scrolling means is the checkbox allowed to roll along with canvas movements, or is it locked static to the screen window?

Here are the functions you need:

MyezCheckbox.get() This is the big one! Returns True if the box is currently checked, or False if it is blank.
MyezCheckbox.set(state=True) Manually forces the checkbox state. Pass True to check it, or False to uncheck it from your script.
MyezCheckbox.move(XAmount=0, YAmount=0) Shifts the position of the checkbox frame relative to its current spot on the canvas.
MyezCheckbox.SetPosition(relx, rely) Snaps the checkbox directly to a brand new absolute relative coordinate.
MyezCheckbox.SetSize(relwidth, relheight) Resizes the layout container box for the widget.
MyezCheckbox.ChangeSize(dw, dh) Scales the checkbox box dimensions up or down on the fly.
MyezCheckbox.SetText(new_text) Dynamically updates the text label sitting next to the checkbox.
MyezCheckbox.hide() This function makes the checkbox completely invisible. It does NOT delete it or reset its true value.
MyezCheckbox.show() This makes the checkbox pop back onto the screen if it was hidden.
MyezCheckbox.SetScroll(scrolling=True) Sets whether the checkbox element moves with canvas scroll rules or stays fixed to the overlay layer.
MyezCheckbox.delete() This completely removes the checkbox from the canvas layer, destroys the core widget, detaches its tracking variables, and clears up system memory instantly.

MyezCheckbox.Update() Probably not needed. This coordinates widget scale events, label modifications, and relative screen position conversions behind the scenes every single frame!
"""


class ezRadioButtonGroup():
    def __init__(self, options, default_selection=0, relx=1500, rely=400, relwidth=3000, relheight=600,
                 relfontsize=10, scrolling=True, font_name="Arial", orientation="vertical"): # <-- Added orientation
        self.options = options
        self.relx = relx
        self.rely = rely
        self.relwidth = relwidth
        self.relheight = relheight
        self.relfontsize = relfontsize
        self.scrolling = scrolling
        self.font_name = font_name
        self.orientation = orientation.lower() # <-- Store orientation ("vertical" or "horizontal")
        self.visibility = "normal"
        # Previous states
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfontsize = self.relfontsize
        self.previous_visibility = self.visibility
        self.default_selection = default_selection
        self.variable = tk.StringVar(value=options[self.default_selection])
        self.buttons = []
        # Create Radiobuttons
        for i, option in enumerate(options):
            btn = tk.Radiobutton(
                rglobals.canvas,
                text=option,
                variable=self.variable,
                value=option,
                font=(self.font_name, int(rglobals.sq_size * relfontsize * 0.002))
            )
            # --- Dynamic Coordinate Calculation ---
            if self.orientation == "horizontal":
                # X moves with i, Y stays constant
                x_calc = self.relx + i * (self.relwidth + 200)
                y_calc = self.rely
            else:
                # X stays constant, Y moves with i (Your original logic)
                x_calc = self.relx
                y_calc = self.rely + i * (self.relheight + 200)

            btn_id = rglobals.canvas.create_window(
                (x_calc / 10000) * rglobals.sq_size + rglobals.x_offset,
                (y_calc / 10000) * rglobals.sq_size + rglobals.y_offset,
                window=btn,
                width=(self.relwidth / 10000) * rglobals.sq_size,
                height=(self.relheight / 10000) * rglobals.sq_size,
                anchor="nw"
            )
            self.buttons.append((btn, btn_id))
        rglobals.AllItems.add(self)
    def GetValue(self):
        return self.variable.get()
    def GetInt(self):
        return self.options.index(self.variable.get())
    def hide(self):
        self.visibility = "hidden"
    def show(self):
        self.visibility = "normal"
    # --- optimized Update ---
    def Update(self):
        PositionChanged = (
            self.relx != self.previous_relx or
            self.rely != self.previous_rely or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        SizeChanged = (
            self.relwidth != self.previous_relwidth or
            self.rely != self.previous_relheight or # Note: check if you meant self.relheight here in your original code!
            self.relfontsize != self.previous_relfontsize or
            rglobals.sq_size != rglobals.previous_sq_size
        )
        VisibilityChanged = (self.visibility != self.previous_visibility)

        if VisibilityChanged:
            state = self.visibility
            for _, btn_id in self.buttons:
                rglobals.canvas.itemconfig(btn_id, state=state)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        in_bounds = (
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )
        if not in_bounds:
            self.hide()

        # --- update buttons ---
        if PositionChanged or SizeChanged or rglobals.WindowChanged or rglobals.ScrollChanged:
            for i, (btn, btn_id) in enumerate(self.buttons):
                
                # --- Dynamic Coordinate Calculation for Update ---
                if self.orientation == "horizontal":
                    x_calc = self.relx + i * (self.relwidth + 200)
                    y_calc = self.rely
                else:
                    x_calc = self.relx
                    y_calc = self.rely + i * (self.relheight + 200)

                x = (x_calc / 10000) * rglobals.sq_size + rglobals.x_offset
                y = (y_calc / 10000) * rglobals.sq_size + rglobals.y_offset

                if not self.scrolling:
                    x += rglobals.scroll_x
                    y += rglobals.scroll_y

                rglobals.canvas.coords(btn_id, x, y)

                if SizeChanged:
                    rglobals.canvas.itemconfig(
                        btn_id,
                        width=(self.relwidth / 10000) * rglobals.sq_size,
                        height=(self.relheight / 10000) * rglobals.sq_size
                    )
                    btn.config(font=(self.font_name, int(rglobals.sq_size * self.relfontsize * 0.002)))

        self._store_previous()

    def _store_previous(self):
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfontsize = self.relfontsize
        self.previous_visibility = self.visibility
    def delete(self):
        import gc
        # Delete buttons from canvas and destroy widgets
        try:
            for btn, btn_id in getattr(self, "buttons", []):
                try:
                    if hasattr(rglobals, "canvas"):
                        rglobals.canvas.delete(btn_id)
                except Exception:
                    pass
                try:
                    btn.destroy()
                except Exception:
                    pass
            self.buttons.clear()
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Delete the StringVar
        try:
            if hasattr(self, "variable"):
                self.variable.set("")  # Clear value
                del self.variable
        except Exception:
            pass

        # Delete all other instance attributes
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        gc.collect()
    def __repr__(self):
            # Grab default values from the __init__ signature
            defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
            return f"""
This is an ezRadioButtonGroup object! It creates an easy list of items to check and you can only check one. and automatically handles putting it on the screen, changing it, and it is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy Radio Button Group like this:
MyezRadioButtonGroup = ezRadioButtonGroup(options=["Option 1", "Option 2", "Option 3"], default_selection={defaults['default_selection']} relx={defaults['relx']}, rely={defaults['rely']}, relwidth={defaults['relwidth']}, relheight={defaults['relheight']},
                                          relfontsize={defaults['relfontsize']}, scrolling={defaults['scrolling']}, font_name="{defaults['font_name']}", orientation="{defaults['orientation']}")

WOAH that's a lot of information! Don't worry, most are not necessary, let's go over them.

options, this means the options to select from, format is ["option 1", "option 2", "option 3",....]
default_selection, this is a number of the default selected option.
relx, the relative x position of the items, up to 10,000
rely, the relative y position of the items, up to 10,000
relwidth, the relative width of the items, up to 10,000
relheight, the relative height of the items, up to 10,000
relfontsize, the relative font size of the items, up to 10,000
scrolling, whether or not the items should scroll or stay locked on screen
font_name, the font name, like times new roman, liberation serif, etc.
orientation, whether the options should be vertical, or horizontal

Here are the functions you need:

MyezRadioButtonGroup.GetValue() this returns the text of the currently selected value.
MyezRadioButtonGroup.GetInt() this shows you the NUMBER of the currently selected value.
MyezRadioButtonGroup.hide() this hides the button. Not deletes it, hides it.
MyezRadioButtonGroup.show() this shows the button if it's hidden.
MyezRadioButtonGroup.delete() this actually gets rid of the button. Frees up memory.

MyezRadioButtonGroup.Update() Uh, you probably don't need this. This applies changes to the button.
"""




class ezSlider:
    def __init__(self):
        print("This is unfinished, and I'd have to manually program this. ChatGPT and Google Gemini aren't working.]")
        print("I don't want to yet. I'm skipping the slider")
        print("until I need it.")
        #Here's how I WOULD do it though:
        #First create the background, with my ezRectangle class
        #Then from that, check if it's clicked, and where the mouse is in there
        #Create a knob with 2 smaller ezRectangles, that always go to the mouse position if clicked.
        #Calculate the value based on where the mouse is.
        #Write that value above the slider using ezText
        #The built in slider is NOT easy to program, it doesn't scale.
        #Input values would be:
        #relx, rely, relwidth, relheight
        #Knob values are calculated based on the relheight

class ezSpinbox():
    def __init__(self, values, relx=2000, rely=2000, relwidth=3000, relheight=600,
                 relfontsize=10, font_name="Arial", scrolling=True, command=None):

        self.values = list(values)
        self.relx = relx
        self.rely = rely
        self.relwidth = relwidth
        self.relheight = relheight
        self.relfontsize = relfontsize
        self.font_name = font_name
        self.scrolling = scrolling
        self.command = command

        # Visibility state
        self.visibility = "normal"

        # --- previous state tracking ---
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfontsize = self.relfontsize
        self.previous_values = list(self.values)
        self.previous_font_name = self.font_name
        self.previous_visibility = self.visibility

        # --- create the Spinbox ---
        self.spinbox = tk.Spinbox(
            rglobals.canvas,
            values=self.values,
            font=(self.font_name, max(1, int(rglobals.sq_size * self.relfontsize * 0.002))),
            command=self.command
        )

        self.spinbox_window_id = rglobals.canvas.create_window(
            (self.relx / 10000) * rglobals.sq_size + rglobals.x_offset,
            (self.rely / 10000) * rglobals.sq_size + rglobals.y_offset,
            window=self.spinbox,
            width=(self.relwidth / 10000) * rglobals.sq_size,
            height=(self.relheight / 10000) * rglobals.sq_size,
            anchor="nw"
        )
        rglobals.AllItems.add(self)
    # --- movement & sizing ---
    def move(self, XAmount=0, YAmount=0):
        self.relx += XAmount
        self.rely += YAmount

    def SetPosition(self, relx, rely):
        self.relx = relx
        self.rely = rely

    def SetSize(self, relwidth, relheight):
        self.relwidth = relwidth
        self.relheight = relheight

    def ChangeSize(self, dw, dh):
        self.relwidth += dw
        self.relheight += dh

    # --- value access ---
    def GetValue(self):
        return self.spinbox.get()

    def SetValues(self, values):
        self.values = list(values)

    def SetCommand(self, command):
        self.command = command
        self.spinbox.config(command=self.command)

    # --- visibility ---
    def hide(self):
        self.visibility = "hidden"

    def show(self):
        self.visibility = "normal"

    def SetScroll(self, scrolling=True):
        self.scrolling = scrolling

    # --- optimized update ---
    def Update(self):
        PositionChanged = (self.relx != self.previous_relx or self.rely != self.previous_rely)
        SizeChanged = (self.relwidth != self.previous_relwidth or self.relheight != self.previous_relheight)
        ValuesChanged = (self.values != self.previous_values)
        FontChanged = (self.font_name != self.previous_font_name or self.relfontsize != self.previous_relfontsize)
        VisibilityChanged = (self.visibility != self.previous_visibility)

        # --- update visibility ---
        if VisibilityChanged:
            rglobals.canvas.itemconfig(self.spinbox_window_id, state=self.visibility)
            self.previous_visibility = self.visibility

        if self.visibility != "normal":
            self._store_previous()
            return

        # --- auto hide if out of bounds ---
        in_bounds = (
            rglobals.minimum_relx < self.relx < rglobals.maximum_relx and
            rglobals.minimum_rely < self.rely < rglobals.maximum_rely
        )
        if not in_bounds:
            self.hide()

        # --- position and size ---
        if PositionChanged or SizeChanged or rglobals.WindowChanged or rglobals.ScrollChanged:
            x = (self.relx / 10000) * rglobals.sq_size + rglobals.x_offset
            y = (self.rely / 10000) * rglobals.sq_size + rglobals.y_offset
            if not self.scrolling:
                x += rglobals.scroll_x
                y += rglobals.scroll_y
            rglobals.canvas.coords(self.spinbox_window_id, x, y)
            rglobals.canvas.itemconfig(
                self.spinbox_window_id,
                width=(self.relwidth / 10000) * rglobals.sq_size,
                height=(self.relheight / 10000) * rglobals.sq_size
            )

        # --- update values ---
        if ValuesChanged:
            self.spinbox.config(values=self.values)

        # --- update font ---
        if FontChanged or SizeChanged or rglobals.WindowChanged:
            self.spinbox.config(font=(self.font_name, max(1, int(rglobals.sq_size * self.relfontsize * 0.002))))

        # --- store previous ---
        self._store_previous()

    def _store_previous(self):
        self.previous_relx = self.relx
        self.previous_rely = self.rely
        self.previous_relwidth = self.relwidth
        self.previous_relheight = self.relheight
        self.previous_relfontsize = self.relfontsize
        self.previous_values = list(self.values)
        self.previous_font_name = self.font_name
        self.previous_visibility = self.visibility
    def delete(self):
        # Remove from canvas
        try:
            if hasattr(self, "spinbox_window_id") and self.spinbox_window_id and hasattr(rglobals, "canvas"):
                rglobals.canvas.delete(self.spinbox_window_id)
        except Exception:
            pass

        # Destroy the actual Tkinter Spinbox widget
        try:
            if hasattr(self, "spinbox") and self.spinbox:
                self.spinbox.destroy()
        except Exception:
            pass

        # Remove from global item tracking
        try:
            if hasattr(rglobals, "AllItems") and self in rglobals.AllItems:
                rglobals.AllItems.remove(self)
        except Exception:
            pass

        # Clear important references
        attrs_to_clear = ["spinbox", "values"]
        for attr in attrs_to_clear:
            if hasattr(self, attr):
                try:
                    delattr(self, attr)
                except Exception:
                    pass

        # Delete all other instance variables
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass

        # Encourage garbage collection
        import gc
        gc.collect()
    def __repr__(self):
            # Grab default values from the __init__ signature
            defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
    def __repr__(self):
        # Grab default values from the __init__ signature
        defaults = {k: v.default for k, v in inspect.signature(self.__init__).parameters.items() if v.default is not inspect.Parameter.empty}
        return f"""
This is an ezSpinbox object! It creates an easy text box with up/down arrows on the screen using Tkinter's Spinbox widget. It lets users cycle through a sequence of values, handles layout scaling, and is OPTIMIZED automatically, only updating when it needs to! So don't worry about optimizations.
You can create an easy spinbox like this:
MyezSpinbox = ezSpinbox(values=["Option 1", "Option 2", "Option 3"], relx={defaults['relx']}, rely={defaults['rely']}, relwidth={defaults['relwidth']}, relheight={defaults['relheight']}, relfontsize={defaults['relfontsize']}, font_name="{defaults['font_name']}", scrolling={defaults['scrolling']}, command=my_function_name)
WOAH that's a lot of information! Don't worry, most of it's not necessary, but let's go over them!
values is a list, tuple, or range of options the user can scroll through (like numbers or strings).
relx means relative starting x position, meaning it automatically changes based on the window size, so you don't have to worry about other windows or devices!
rely means relative starting y position.
relwidth is the relative width of the spinbox box.
relheight is the relative height of the spinbox box.
relfontsize controls the relative font scale so the options text scales nicely along with window changes.
font_name is the font style used inside the box (like Arial or Helvetica).
scrolling means is the spinbox container allowed to move when the canvas scrolls, or is it fixed static to the screen?
command is an optional function triggered instantly every single time a user clicks the up or down arrows to change the value.

Here are the functions you need:

MyezSpinbox.GetValue() This is the big one! Returns a string of whatever option is currently actively showing inside the spinbox text field.
MyezSpinbox.SetValues(values) Swaps out the current options sequence with a brand new list of choices on the fly.
MyezSpinbox.SetCommand(command) Dynamically updates or assigns the callback function that executes when arrows are clicked.
MyezSpinbox.move(XAmount=0, YAmount=0) Shifts the position of the spinbox relative to its current spot on the canvas.
MyezSpinbox.SetPosition(relx, rely) Snaps the spinbox widget directly to a new absolute relative coordinate.
MyezSpinbox.SetSize(relwidth, relheight) Dynamically adjusts the outer bounding dimensions of the spinbox frame.
MyezSpinbox.ChangeSize(dw, dh) Scales the spinbox width and height parameters up or down from its current geometry.
MyezSpinbox.hide() This function makes the spinbox completely invisible. It does NOT delete it or erase the current selection state.
MyezSpinbox.show() Makes the spinbox pop back onto the view layer if it was previously hidden.
MyezSpinbox.SetScroll(scrolling=True) Sets whether the spinbox follows canvas scroll adjustments or remains pinned directly to the static view layer.
MyezSpinbox.delete() This completely shreds the internal Spinbox widget, removes its container window tracking from the canvas, and wipes instance parameters to free system memory instantly.

MyezSpinbox.Update() Probably not needed. This coordinates structural transformations, list assignments, display fonts, and canvas relative positionings behind the scenes automatically per frame!
"""



def ezFolderInput():
    folder_path = filedialog.askdirectory(
        title="Select a folder"
    )
    return folder_path


def StartMainLoop():
    global previous_keys_held
    rglobals.relmouse_x = ((rglobals.root.winfo_pointerx()-rglobals.x_offset-rglobals.root.winfo_rootx())/rglobals.sq_size)*10000
    rglobals.relmouse_y = ((rglobals.root.winfo_pointery()-rglobals.y_offset-rglobals.root.winfo_rooty())/rglobals.sq_size)*10000
    #print()
    #print(rglobals.keys_held)
    #print(previous_keys_held)
    for key in rglobals.keys_held:
        if key not in previous_keys_held:
            rglobals.keys_clicked.add(key)
    for key in previous_keys_held:
        if key not in rglobals.keys_held:
            rglobals.keys_released.add(key)

def EndMainLoop():
    global previous_keys_held
    #Now we END the animation.
    # Reset single-frame clicks after processing
    for btn in rglobals.mouse_clicked:
        rglobals.mouse_clicked[btn] = False
        rglobals.mouse_released[btn] = False
    rglobals.keys_clicked.clear()
    rglobals.keys_released.clear()
    previous_keys_held = rglobals.keys_held.copy()

def SetGlobalVariables(func):
    def wrapped(*args, **kwargs):
        StartMainLoop()
        result = func(*args, **kwargs)
        EndMainLoop()
        return result
    return wrapped

def UpdateLoop():
    global SaveWindowSize
    global PreviousTime
    # Get current rglobals.canvas size, this is NEEDED before any updates, you generally don't need to change this stuff:
    rglobals.window_width = rglobals.canvas.winfo_width()
    rglobals.window_height = rglobals.canvas.winfo_height()
    rglobals.sq_size = max(1, min(rglobals.window_width, rglobals.window_height))  # ensure it's never zero
    if rglobals.sq_size == 0:
        rglobals.root.after(50, UpdateLoop)
        return
    rglobals.scroll_x = rglobals.canvas.canvasx(0)
    rglobals.scroll_y = rglobals.canvas.canvasy(0)
    rglobals.WindowChanged = (rglobals.sq_size != rglobals.previous_sq_size or rglobals.window_height != rglobals.previous_window_height or rglobals.window_width != rglobals.previous_window_width)
    rglobals.ScrollChanged = (rglobals.scroll_x != rglobals.previous_scroll_x or rglobals.scroll_y != rglobals.previous_scroll_y)
    if(rglobals.WindowChanged):
        SaveWindowSize = True
        PreviousTime = time.time_ns()
        rglobals.x_offset = 0
        rglobals.y_offset = 0
        if(rglobals.window_width > rglobals.window_height):
            rglobals.x_offset = int((rglobals.window_width-rglobals.window_height)/2)
        elif(rglobals.window_width < rglobals.window_height):
            rglobals.y_offset = int((rglobals.window_height-rglobals.window_width)/2)
    if SaveWindowSize:
        if time.time_ns() - PreviousTime > 3000000000:
            SaveWindowSize = False
            with open("Saved_Window_Size.txt", "w", encoding="utf-8") as file:
                file.write(f"{rglobals.window_width}\n")
                file.write(f"{rglobals.window_height}")
    #print(type(rglobals.AllItems))
    #print(len(rglobals.AllItems))
    for MyItem in rglobals.AllItems:
        MyItem.Update()
    rglobals.root.after(rglobals.FPSTIME, UpdateLoop)
    #First set the previous ones, since we're re doing the animation loop:
    rglobals.previous_sq_size = rglobals.sq_size
    rglobals.previous_window_height = rglobals.window_height
    rglobals.previous_window_width = rglobals.window_width
    rglobals.previous_scroll_x = rglobals.scroll_x
    rglobals.previous_scroll_y = rglobals.scroll_y

def StartProgram(MainLoop,FPS):
    rglobals.FPSTIME = int(1000/FPS)
    #These commands start our program!
    #The first one starts the MainLoop where all of our game/app logic takes place:
    rglobals.root.after(100, MainLoop)
    #The second one starts our frames per second or Updating loop, that ACTUALLY draws stuff to the screen
    #The reason we have 2 separate loops is so we can raise or lower the FPS without affecting game speed:
    rglobals.root.after(100, UpdateLoop)
    #I dunno what this does... but it's necessary at the VERY end of the program the LAST line:
    rglobals.root.mainloop()


global sound_exe_path
sound_exe_path = f"{os.getcwd()}{os.sep}ezGUI{os.sep}eztkinter{os.sep}ffplay.exe"

# Session guard to keep audio playback instant after the first check
_FFPLAY_VERIFIED = False
# We will match this against the first line of 'ffplay -version'
EXPECTED_VERSION_TAG = "8.1.2"  
FFPLAY_ZIP_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

def _ensure_ffplay():
    """Ensures ffplay.exe exists and is the correct version on Windows."""
    global _FFPLAY_VERIFIED, sound_exe_path
    if _FFPLAY_VERIFIED:
        return

    os.makedirs(os.path.dirname(sound_exe_path), exist_ok=True)
    download_needed = False

    if not os.path.exists(sound_exe_path):
        print("ffplay.exe not found. Preparing to download...")
        download_needed = True
    else:
        # Check current version
        try:
            result = subprocess.run(
                [sound_exe_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            if EXPECTED_VERSION_TAG not in result.stdout:
                print("ffplay.exe is outdated. Preparing upgrade...")
                download_needed = True
                try:
                    os.remove(sound_exe_path)
                except Exception as e:
                    print(f"Failed to remove old ffplay.exe: {e}")
                    download_needed = False 
        except PermissionError:
            pass
        except:
            download_needed = True


    if download_needed:
        print(f"Downloading FFmpeg archive from {FFPLAY_ZIP_URL}...")
        try:
            # Spoof user-agent so the server doesn't block the Python script
            req = urllib.request.Request(FFPLAY_ZIP_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                zip_data = response.read()
            
            # Read the zip completely in memory and extract just ffplay.exe
            with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                ffplay_zip_path = None
                for file_info in z.infolist():
                    # Dynamic check for the file inside the bin folder
                    if file_info.filename.endswith("bin/ffplay.exe"):
                        ffplay_zip_path = file_info.filename
                        break
                
                if ffplay_zip_path:
                    print(f"Extracting {ffplay_zip_path} -> {sound_exe_path}")
                    executable_bytes = z.read(ffplay_zip_path)
                    with open(sound_exe_path, 'wb') as f:
                        f.write(executable_bytes)
                    print("ffplay.exe installed successfully!")
                else:
                    print("ERROR: Clean download, but couldn't find 'bin/ffplay.exe' inside the zip structure.")
                    return
        except Exception as e:
            print(f"ERROR: Failed to download or extract ffplay.exe: {e}")
            return

    _FFPLAY_VERIFIED = True


class ezSound:
    def __init__(self, filepath):
        self.filepath = os.path.abspath(filepath)
        if not os.path.isfile(self.filepath):
            raise FileNotFoundError(f"{self.filepath} does not exist")
        self._thread = None
        self._proc = None
        self.playing = False
        rglobals.AllSounds.add(self)

    def _play_single(self, duration=None):
        try:
            if os.name == "posix":
                self._proc = subprocess.Popen(['aplay', self.filepath])
                if duration is not None:
                    time.sleep(duration)
                    self.stop()
                else:
                    self._proc.wait()

            elif os.name == "nt":
                global sound_exe_path
                
                # Triggers auto-download/update checking dynamically
                _ensure_ffplay()

                if os.path.exists(sound_exe_path):
                    self._proc = subprocess.Popen(
                        [sound_exe_path, "-nodisp", "-autoexit", self.filepath],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    if duration:
                        time.sleep(duration)
                        self.stop()
                    else:
                        self._proc.wait()
                else:
                    print(f"ERROR: SOUND EXECUTABLE {sound_exe_path} DOES NOT EXIST.")
        finally:
            self.playing = False
            self._proc = None

    def play(self, duration=None):
        self.playing = True
        self._thread = threading.Thread(target=self._play_single, args=(duration,))
        self._thread.start()

    def stop(self):
        self.playing = False
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                pass
            self._proc = None

    def delete(self):
        try:
            self.stop()
        except Exception:
            pass
        try:
            if hasattr(rglobals, "AllSounds") and self in rglobals.AllSounds:
                rglobals.AllSounds.remove(self)
        except Exception:
            pass
        attrs_to_clear = ["_proc", "_thread", "filepath"]
        for attr in attrs_to_clear:
            if hasattr(self, attr):
                try:
                    delattr(self, attr)
                except Exception:
                    pass
        for attr in list(self.__dict__.keys()):
            try:
                delattr(self, attr)
            except Exception:
                pass
        import gc
        gc.collect()

    def __repr__(self):
        return f"""
This is an ezSound object! It plays sound on Linux primarily, but also Microslop Winslop!
You can create an ezSound object like this:
MyezSoundObject = ezSound("{os.sep}path{os.sep}to{os.sep}audio{os.sep}file.wav") 
MyezSoundObject.play() is a function that plays the audio 
MyezSoundObject.stop() is a function that stops playing the audio (if playing)
MyezSoundObject.delete() is a function that deletes this object and frees memory, but you can't call it after that! 
MyezSoundObject.filepath is a variable that tells you where the audio was loaded from. 
self.filepath={self.filepath}
MyezSoundObject.playing is a variable that tells you if the audio is currently playing or not. 
self.playing={self.playing}
"""
