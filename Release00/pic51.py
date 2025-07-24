# Requirements: pip install compushady pillow numpy pygame
# Requirements: [Linux] libvulkan-dev and libx11-dev on Debian 

import os
import json
import time
#import threading
from tkinter import filedialog
from natsort import natsorted
import LIBSHADER_SRCNN as SRCNN # local lib
import LIBSHADER_Lanczos as Lanczos # local lib

if os.name == 'nt':
    from ctypes import windll
    windll.user32.SetProcessDPIAware() # HiDPI support
    import winsound
    def beepLO(): winsound.Beep(440, 30) # pass
    def beepHI(): winsound.Beep(440*2, 30) # pass
else:
    def beepLO(): pass
    def beepHI(): pass

caption = "Image Viewer with Super Resolution Zoom"
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
pygame.init() # must after DPI aware # print(pygame.display.Info()) # print(pygame.display.get_driver())
pygame.display.set_caption(caption)
# icon = pygame.image.load('pixiv3.ico') # print(icon.get_size())
# pygame.display.set_icon(icon)
pygame.font.init() # print(pygame.font.get_fonts())
font = pygame.font.SysFont('arialblack', 30)
[(sw,sh)] = pygame.display.get_desktop_sizes()
(w,h)=(sw//2,sh//2)
fullscreenT = 0 # full screen state and toggle flag
#(w,h)=(sw,sh)
#fullscreenT = 1 # full screen state and toggle flag
display = pygame.display.set_mode((w, h))
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR) # SYSTEM_CURSOR_ARROW)SYSTEM_CURSOR_HAND)SYSTEM_CURSOR_NO)SYSTEM_CURSOR_SIZEALL)
clock = pygame.time.Clock()

silent = 0 # Debug messages shown when run from IDE, or rename *.py *.pyw
INIT_DIR="/home/guest/Pictures"
BOOKMARK = r"bookmark.json" # must use full path for running py from windows desktop shorcuts

# Load one image to memory cache
def load(nnn):
    global info_cache
    global image_cache
    global screen_cache
    start_time = time.time()
    filename = os.path.join(path,list[nnn])
    filesize = os.path.getsize(filename)
    image_cache = pygame.image.load(filename)
    image_cache=pygame.Surface.convert(image_cache,32)
            
    (img_w, img_h) = image_cache.get_size()
    ratio = min(w/img_w, h/img_h)
    
    # screen_cache = pygame.transform.smoothscale(image_cache,(int(img_w*ratio),int(img_h*ratio)))
    
    Lanczos.compute(image_cache.get_buffer(),img_w,img_h, int(img_w*ratio), int(img_h*ratio))
    screen_cache = pygame.image.frombuffer(Lanczos.readback_buffer.readback(), (Lanczos.OUTPUT.row_pitch//4, Lanczos.OUTPUT.height), "BGRA")

    info_cache=[str(nnn)+"/"+str(total-1)+"  "+list[nnn],str(img_w)+"x"+str(img_h)+"  "+str(int(filesize/1000))+"K"+"  "+str(round(time.time()-start_time,2))+"s"]

# Update display using pre-decoded image cache
def show(index=1):
    global zoomed_image, zoom_mode, backup    
    zoomed_image = None # clear zoom cache at new image
    backup = None 
    zoom_mode = 0
    
    v=36
    display.fill((0,0,0))

    (iw,ih) = screen_buffer[index].get_size()
    display.blit(screen_buffer[index], (w//2-iw//2, h//2-ih//2))

    if show_info:
        pygame.draw.rect(display,(0,0,0),(20,35,500,160),0) # width default=0 fill
        pygame.draw.rect(display,(55,55,55),(20,35,500,160),1)
        BG=(0,0,0)
        COLOR=(255,0,0) if (list[n] in marked_for_delete) else (255,255,255)
        if x4_mode: string = " [ESC] Exit [F1] Fullscreen [F2] Open folder [i] Toggle OSD [L/R] Rotate [Wheel Click] Zoom [4] Enable X4 zoom mode [ON] "
        else: string = " [ESC] Exit [F1] Fullscreen [F2] Open folder [i] Toggle OSD [L/R] Rotate [Wheel Click] Zoom [4] Enable X4 zoom mode [OFF] "
        display.blit(font.render(string, True, COLOR,BG), (v, h-v*2))
        string = str(n-sub_start)+"/"+str(subtotal-1)+" in ["+str(sub_start)+"-"+str(sub_end)+"]  Marked="+str(len(marked_for_delete))
        display.blit(font.render(string, True, COLOR,BG), (v, v*4))
        string = info_buffer[index][1]
        display.blit(font.render(string, True, COLOR,BG), (v, v*3))
        string = info_buffer[index][0]
        display.blit(font.render(string, True, COLOR,BG), (v, v*2))
        string = os.path.basename(path)
        display.blit(font.render(string, True, COLOR,BG), (v, v*1))

# Group image files by filename from PIXIV
def grouping():
    global sublist
    global subtotal
    global sub_start
    global sub_end
    sub_start=0
    leading=list[n].split("p")[0]

    sublist=[]
    for f in list:
        if(f.startswith(leading)): sublist.append(f)
        elif sublist: break
        if not sublist: sub_start+=1
    subtotal=len(sublist)
    sub_end=sub_start+subtotal-1
    # [DEBUG] print(leading,sublist,subtotal)

def reload_all_cache():
    global n
    global image_buffer
    global screen_buffer
    global info_buffer

    # Check and adjust boundries
    if n<0: n=0
    if n>total-1: n=total-1

    # Show new image without delay
    grouping()
    load(n)
    image_buffer[1]=image_cache
    screen_buffer[1]=screen_cache
    info_buffer[1]=info_cache
    show(index=1)

    # load caches in background
    if n>0:
        load(n-1)
        image_buffer[0]=image_cache
        screen_buffer[0]=screen_cache
        info_buffer[0]=info_cache
    if n<total-1:
        load(n+1)
        image_buffer[2]=image_cache
        screen_buffer[2]=screen_cache
        info_buffer[2]=info_cache

def jump(to):
    global n
    n = to
    reload_all_cache()

def step_forward():
    global n
    global image_buffer
    global screen_buffer
    global info_buffer

    if n<total-1:
        n=n+1
        if (n>sub_end or n<sub_start):
            grouping() # new grouping across group boundaries
            beepLO()
        show(index=2)
        del image_buffer[0]
        del screen_buffer[0]
        del info_buffer[0]
        if n<total-1:
            load(n+1)
            image_buffer.append(image_cache)
            screen_buffer.append(screen_cache)
            info_buffer.append(info_cache)
        else:
            image_buffer.append(None)
            screen_buffer.append(None)
            info_buffer.append(None)
    else:
        beepHI()

def step_backward():
    global n
    global image_buffer
    global screen_buffer
    global info_buffer

    if n>0:
        n=n-1
        if (n>sub_end or n<sub_start):
            grouping() # new grouping across group boundaries
            beepLO()
        show(index=0)
        del image_buffer[2]
        del screen_buffer[2]
        del info_buffer[2]
        if n>0:
            load(n-1)
            image_buffer.insert(0,image_cache)
            screen_buffer.insert(0,screen_cache)
            info_buffer.insert(0,info_cache)
        else:
            image_buffer.insert(0,None)
            screen_buffer.insert(0,None)
            info_buffer.insert(0,None)
    else:
        beepHI()

def rotate(angle):
    display.fill((0,0,0))
    z = image_buffer[1]
    rh, rw = z.get_size() # reversed order
    ratio = min(w/rw, h/rh) # fit to screen
    rotated_image = pygame.transform.rotozoom(z, angle, ratio)
    (iw,ih) = rotated_image.get_size()
    display.blit(rotated_image, (w//2-iw//2, h//2-ih//2))

def jump_to_next_group(): # Mouse side keys
    global n
    if subtotal>1 and n!=sub_end:
        n = sub_end # +1
        reload_all_cache()
    else:
        step_forward()

def jump_to_prev_group(): # Mouse side keys
    global n
    if subtotal>1 and n!=sub_start:
        n = sub_start # -1
        reload_all_cache()
    else:
        step_backward()

def open_folder(new_path=None):
    global path, list, total, n, marked_for_delete
    if not new_path: new_path=filedialog.askdirectory(initialdir=INIT_DIR)

    new_list = [] # Load image file list
    if new_path:
        img_ext = [".jpg",".png",".bmp",".webp"]
        for f in os.listdir(new_path):
            ext = os.path.splitext(f)[1]
            if ext.lower() in img_ext: new_list.append(f) # [DEBUG] print(f)

    new_total=len(new_list)
    if new_total:
        update_bookmark(n)
        list=natsorted(new_list)
        total=new_total
        path=new_path
        n=0
        if bookmark:
            for foo in bookmark:
                if foo["Folder"]==path:
                    n=foo["Bookmark"]
        marked_for_delete = set()
        reload_all_cache() # Display first image
        if not silent: print(f"Viewing {total} images at folder {path}")

def update_bookmark(nn=0):
    global bookmark
    if bookmark:
        for foo in bookmark:
            foo["Resume"]=0
            if foo["Folder"]==path:
                bookmark.remove(foo)

    bookmark.insert(0,{"Folder":path, "Bookmark":nn, "Resume":1})

def fullscreen():
    global fullscreenT,w,h
    global display
    if fullscreenT: # Toggle
        pygame.display.quit()
        pygame.display.init()
        pygame.display.set_caption(caption)
        (w,h)=(sw//2,sh//2) # Windowed mode
        display = pygame.display.set_mode((w, h)) # pygame.SHOWN default
        reload_all_cache()
        fullscreenT=0
    else:
        # [Windows] pygame.FULLSCREEN # Flickering due to changes to hardware resolution/refresh rates but good for Linux
        pygame.display.quit()
        pygame.display.init()
        pygame.display.set_caption(caption)
        (w,h)=(sw,sh) # Fullscreen mode
        if os.name == 'nt':
            display = pygame.display.set_mode((w, h))
        else:
            display = pygame.display.set_mode((w, h),pygame.FULLSCREEN)
        reload_all_cache()
        fullscreenT=1

def info_toggle(): # Toggle OSD panel
    global show_info
    show_info=not show_info
    show()

x4_mode = 0
zoom_mode = 0
zoom_ratio = 4
zoomed_image = None
backup = None
def zoom():
    global zoom_ratio
    global zoomed_image
    global backup
    global mx,my # remember mouse xy

    if not zoom_mode: # Exit zoom mode
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        if(backup is not None): display.blit(backup,(0,0)) # for first run without backup
        # if zoomed_image is not None: zoomed_image = None # don't reset here, reset at next image             
        return

    if(zoomed_image is None): # First run
        backup = pygame.Surface.copy(display)
        z = image_buffer[1] # Get original 1:1 image
        iw, ih = z.get_size()
             
        # SRCNN 2X
        start = time.perf_counter()        
        SRCNN.init_buffer(iw,ih)
        SRCNN.compute(z.get_buffer(),iw,ih) # Fixed 2X only
        zoomed_image = pygame.image.frombuffer(SRCNN.readback_buffer.readback(), (SRCNN.OUTPUT.row_pitch//4, SRCNN.OUTPUT.height), "BGRA")
        rp = SRCNN.OUTPUT.row_pitch//4
        zw, zh = zoomed_image.get_size()
        print(f"x2 SRCNN Shader compute time={time.perf_counter()-start},[{iw}x{ih}] to [{zw}x{zh}], row_pitch={rp}")
        
        if x4_mode: # run twice for 4X 
            start = time.perf_counter()        
            SRCNN.init_buffer(zw,zh)
            SRCNN.compute(zoomed_image.get_buffer(),zw,zh) # Fixed 2X only, cascaded
            zoomed_image = pygame.image.frombuffer(SRCNN.readback_buffer.readback(), (SRCNN.OUTPUT.row_pitch//4, SRCNN.OUTPUT.height), "BGRA")
            rp = SRCNN.OUTPUT.row_pitch//4
            z4w, z4h = zoomed_image.get_size()
            print(f"x4 SRCNN Shader compute time={time.perf_counter()-start},[{zw}x{zh}] to [{z4w}x{z4h}], row_pitch={rp}")
                
        if False:        
            # Find ideal zoom ratio
            if(iw>w*2 or ih>h*2): zoom_ratio=1
            elif(iw>w or ih>h): zoom_ratio=2
            else: zoom_ratio=3
            # zoomed_image = pygame.transform.smoothscale_by(z, zoom_ratio)
                
        pygame.mouse.set_pos([w//2, h//2])
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
        mx = w//2+1 # simulate mouse moved to trigger the first screen update below

    x, y = pygame.mouse.get_pos()
    if x!=mx or y!=my: # only update display if mouse moved
        display.fill((0,0,0))
        zw, zh = zoomed_image.get_size()
        #display.blit(zoomed_image, (w//2-zw//2, h//2-zh//2)) # static center
        display.blit(zoomed_image, ((x-w//2)*zoom_ratio+w//2-zw//2, (y-h//2)*zoom_ratio+h//2-zh//2))
    mx,my = pygame.mouse.get_pos()

# Main ##################################################################################
path=None
subtotal=0 # Grouping
sub_start=0 # Grouping
sub_end=0 # Grouping
show_info=1 # Display panel layer priority
auto=0
marked_for_delete=set()
image_buffer=[None,None,None]
screen_buffer=[None,None,None]
info_buffer=[None,None,None]

if not silent:
    print(f"\n{caption}")
    print(f"[Screen resolution]: {w}x{h}")
    print()
    print("[Additional Keyboard Shorcuts]")
    print("[Home][End]: Jump to first/last file of current folder")
    print("[Left][Right]: Jump to first/last and step to previous/next group")
    print("[Page Up][Page Down]: Jump back/forward 5%")
    print("[Insert]: Toggle current file for delete")
    print("[Delete]: Mark current group for delete")
    print()

# Try to load bookmkark file and resume from last session
try:
    with open(BOOKMARK, "r") as file:
        bookmark = json.load(file)
        for foo in bookmark:
            if (foo["Resume"]): # Load bookmark resume point
                path=foo["Folder"]
                n=foo["Bookmark"]
                open_folder(new_path=path)
                break
except IOError:    
    bookmark = []
    n=0
    total=0
    path=None

while not total: open_folder() # loop until target folder is not empty

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False # ESC to exit
            if event.key == pygame.K_SPACE: pass
            if event.key == pygame.K_4: x4_mode = 1 # enable X4 zoom
            if event.key == pygame.K_F1: fullscreen()
            if event.key == pygame.K_F2: open_folder()
            if event.key == pygame.K_i: info_toggle()
            if event.key == pygame.K_l: rotate(-90)
            if event.key == pygame.K_r: rotate(90)
            if event.key == pygame.K_DOWN: step_forward()
            if event.key == pygame.K_UP: step_backward()
            if event.key == pygame.K_LEFT: jump_to_prev_group()
            if event.key == pygame.K_RIGHT: jump_to_next_group()
            if event.key == pygame.K_HOME: jump(0)
            if event.key == pygame.K_END: jump(total-1)
            if event.key == pygame.K_PAGEUP: jump(n-total//20) # jump 5%
            if event.key == pygame.K_PAGEDOWN: jump(n+total//20) # jump 5%

            # File management
            if event.key == pygame.K_INSERT:  # Toggle mark/unmark single file for delete
                if list[n] not in marked_for_delete: marked_for_delete.add(list[n])
                else: marked_for_delete.remove(list[n])
                step_forward()
                beepHI()
            if event.key == pygame.K_DELETE:  # Mark current group of files for delete
                for i in range(sub_start,sub_end+1): marked_for_delete.add(list[i]) #[DEBUG] print("marked for delete",list[n])
                jump(sub_end+1)
                beepHI()

        if event.type == pygame.MOUSEBUTTONDOWN: # print(event.button)
            if event.button == 1: step_forward() # LEFT
            if event.button == 2: zoom_mode = not zoom_mode # MID
            if event.button == 3: step_backward() # RIGHT
            if event.button == 4: step_backward() # SCROLL UP
            if event.button == 5: step_forward() # SCROLL DOWN
            if event.button == 6: jump_to_next_group() # SIDE BACK
            if event.button == 7: jump_to_prev_group() # SIDE FRONT

    zoom()
    pygame.display.flip()
    clock.tick(120)
pygame.quit()

# [Exit and Clean Up] Deleting/moving marked_for_delete
RECYCLE="\\xxx"
count=0
if marked_for_delete: os.makedirs(path+RECYCLE, exist_ok=True)
for f in marked_for_delete:
    source=os.path.join(path,f)
    dest=os.path.join(path+RECYCLE,f)
    os.rename(source, dest) #[DEBUG] print(source, dest)
    count+=1
print(f"{count} marked files moved to recycle folder {RECYCLE}")

"""
if(count): # Notify delete/move completed and open in explorer for inspection
    beepHI()
    os.startfile(path)
"""

# Print bookmark info and folder progress
if count>n: n=count
progress=(n-count)*100//(total-count-1)
print(f"Bookmark saved at # {n-count}/{total-count-1} {progress}%\n")
update_bookmark(n-count) # log={"Folder": path, "Bookmark": (n-count)}
with open(BOOKMARK, "w") as f:
    json.dump(bookmark, f)
