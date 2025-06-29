import pygame
import sys
import random
import cv2
import threading

pygame.init()
width = 180
height = 110
pixsize = 8
screenWidth = width * pixsize 
screenHeight = height * pixsize 
grd = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Sand Simulation with Custom Color")

check = None
canvas = [[check for _ in range(height)] for _ in range(width)]
g = 0.25
Vterm = 3.0
ax = 0
posx = 0
mousedown = False
currentradius = 3
currentcolor = pygame.K_s
custom_color = None
eraser_mode = False

input_active = False
input_text = ""
font = pygame.font.SysFont(None, 24)
input_box_rect = pygame.Rect(10, 10, 200, 30)

class cellState:
    def __init__(self, colorkey=pygame.K_s, rgb=None):
        self.color = rgb
        self.colorS = (random.randint(205, 215), random.randint(195, 205), random.randint(125, 135))
        self.colorB = (random.randint(0, 10), random.randint(0, 10), random.randint(245, 255))
        self.colorG = (random.randint(0, 10), random.randint(245, 255), random.randint(0, 10))
        self.colorR = (random.randint(245, 255), random.randint(0, 10), random.randint(0, 10))
        self.colorW = (random.randint(245, 255), random.randint(245, 255), random.randint(245, 255))
        self.color0 = (random.randint(0, 25), random.randint(0, 25), random.randint(0, 25))
        self.colorkey = colorkey
        self.vy = 1
        self.vx = 0

def drawGrid():
    for x in range(width):
        for y in range(height):
            color = (0,0,0)
            if isinstance(canvas[x][y], cellState):
                cell = canvas[x][y]
                if cell.colorkey == pygame.K_r:
                    color = cell.colorR
                elif cell.colorkey == pygame.K_g:
                    color = cell.colorG
                elif cell.colorkey == pygame.K_b:
                    color = cell.colorB
                elif cell.colorkey == pygame.K_s:
                    color = cell.colorS
                elif cell.colorkey == pygame.K_w:
                    color = cell.colorW
                elif cell.colorkey == pygame.K_0:
                    color = cell.color0
                elif cell.colorkey == pygame.K_c:
                    color = cell.color
                else:
                    color = cell.color
            pygame.draw.rect(grd, color, (x*pixsize, y*pixsize, pixsize, pixsize))

def drawInputBox():
    pygame.draw.rect(grd, (255, 255, 255), input_box_rect)
    txt_surface = font.render(input_text, True, (0, 0, 0))
    grd.blit(txt_surface, (input_box_rect.x + 5, input_box_rect.y + 5))

def drawUI():
    if eraser_mode:
        eraser_text = font.render("ERASER MODE", True, (255, 100, 100))
        grd.blit(eraser_text, (screenWidth - 120, 10))

def placeSand():
    mouse_pressed = pygame.mouse.get_pressed()[0]
    if mouse_pressed:
        mx, my = pygame.mouse.get_pos()
        gx, gy = mx // pixsize, my // pixsize
        if 0 <= gx < width and 0 <= gy < height:
            if eraser_mode:
                erase_particles(gx, gy, currentradius)
            else:
                draw_circlePlacement(gx, gy, currentradius, chance=0.5)
    return mouse_pressed

def erase_particles(centerx, centery, radius):
    """Erase particles in a circular area"""
    if radius == 1:
        if 0 <= centerx < width and 0 <= centery < height:
            canvas[centerx][centery] = None
    else:
        for i in range(-radius, radius + 1):
            for k in range(-radius, radius + 1):
                x = centerx + i
                y = centery + k
                if 0 <= x < width and 0 <= y < height:
                    if i**2 + k**2 <= radius**2:
                        canvas[x][y] = None

def draw_circlePlacement(centerx, centery, radius, chance=1.0):
    if radius == 1:
        if 0 <= centerx < width and 0 <= centery < height:
            new_cell = cellState(currentcolor, rgb=custom_color if custom_color else None)
            new_cell.vx = ax
            canvas[centerx][centery] = new_cell
    else:
        for i in range(-radius, radius + 1):
            for k in range(-radius, radius + 1):
                x = centerx + i
                y = centery + k
                if 0 <= x < width and 0 <= y < height:
                    if i**2 + k**2 <= radius**2:
                        if random.random() < chance:
                            new_cell = cellState(currentcolor, rgb=custom_color if custom_color else None)
                            new_cell.vx = ax
                            canvas[x][y] = new_cell

def newtonize():
    praticlesmoving = False
    for y in range(height - 2, -1, -1):
        x_range = list(range(width-2, -2, -1))
        random.shuffle(x_range)
        for x in x_range:
            cell = canvas[x][y]
            if isinstance(cell, cellState):
                cell.vy = min(cell.vy + g, Vterm)
                cell.vx *= 1
                for i in range(int(cell.vy)):
                    if y + 1 + i >= height - 1:
                        break
                    hx = int(cell.vx) if i == int(cell.vy) - 1 else 0
                    target_x = max(0, min(width - 1, x + hx))
                    below = canvas[x][y + 1 + i]
                    belowLeft = canvas[x - 1][y + 1 + i] if x > 0 else cell
                    belowRight = canvas[x + 1][y + 1 + i] if x < width - 1 else cell
                    diagonal_target = canvas[target_x][y + 1 + i] if target_x != x else below
                    if isinstance(canvas[x][y + i], cellState):
                        if hx != 0 and diagonal_target is None:
                            canvas[target_x][y + 1 + i] = canvas[x][y + i]
                            canvas[x][y + i] = None
                            praticlesmoving = True
                        elif below is None:
                            canvas[x][y + 1 + i] = canvas[x][y + i]
                            canvas[x][y + i] = None
                            praticlesmoving = True
                        elif belowRight is None:
                            canvas[x + 1][y + 1 + i] = canvas[x][y + i]
                            canvas[x][y + i] = None
                            praticlesmoving = True
                        elif belowLeft is None:
                            canvas[x - 1][y + 1 + i] = canvas[x][y + i]
                            canvas[x][y + i] = None
                            praticlesmoving = True
                        else:
                            cell.vy = 0
                            cell.vx *= 0.8
                            break
    return praticlesmoving

def lateralAcceleration():
    global posx, ax, mousedown
    if mousedown:
        currentmosx = pygame.mouse.get_pos()[0]
        dx = currentmosx - posx
        ax = dx * 0.05
        posx = currentmosx
    else:
        ax = 0

def pixelizepic():

    for num in range(3, 0, -1):
        grd.fill((0, 0, 0))  
        drawGrid()
        font_size2 = 100
        font2 = pygame.font.SysFont('arial', font_size2)       
        countdown_text = font2.render(str(num), True, (255, 255, 255))
        grd.blit(countdown_text, (screenWidth // 2 - 10, screenHeight // 2 - 10))
        pygame.display.flip()
        pygame.time.delay(1000)
    
    grd.fill((255, 255, 255))
    pygame.display.flip()
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    grd.fill((0, 0, 0))
    pygame.display.flip()

    if not ret:
        print("Failed to take image from camera.")
        return
    
    loadingtxt = font2.render("Creating Image!", True, (255, 255, 255))
    grd.fill((0,0,0))
    grd.blit(loadingtxt, (screenWidth // 2 - loadingtxt.get_width() // 2, screenHeight // 2 - loadingtxt.get_height() // 2))
    pygame.display.flip()
    
    frame_small = cv2.resize(frame, (width, height))
    frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
    
    pixels_per_frame = 15  
    pixel_queue = []

    for y in reversed(range(height)):
        for x in range(width):
            color = tuple(frame_rgb[y][x])
            pixel_queue.append((x, color))
    
    while pixel_queue:
        for _ in range(min(pixels_per_frame, len(pixel_queue))):
            if pixel_queue:
                x, color = pixel_queue.pop(0)
                canvas[x][0] = cellState(colorkey=pygame.K_c, rgb=color)
        
        lateralAcceleration()
        newtonize()
        grd.fill((0, 0, 0))
        drawGrid()
        pygame.display.flip()
        clock.tick(60)

clock = pygame.time.Clock()
needs_redraw = True
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mousedown = True
            posx = pygame.mouse.get_pos()[0]

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mousedown = False

        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    try:
                        parts = [int(x.strip()) for x in input_text.split(",")]
                        if len(parts) == 3:
                            custom_color = tuple(parts)
                            print(parts)
                            print("Custom color set to:", custom_color)
                    except:
                        print("Invalid RGB input")
                    input_active = False
                    input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
            else:
                if event.key == pygame.K_RETURN:
                    input_active = True
                    input_text = ""
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    currentradius = event.key - pygame.K_0
                elif event.key == pygame.K_p:
                    pixelizepic()
                elif event.key == pygame.K_e:
                    eraser_mode = not eraser_mode
                    print("Eraser mode:", "ON" if eraser_mode else "OFF")
                else:
                    validbuttons = [pygame.K_r, pygame.K_g, pygame.K_b, pygame.K_s, pygame.K_w, pygame.K_0]
                    if custom_color:
                        validbuttons.append(pygame.K_c)
                    if event.key in validbuttons:
                        currentcolor = event.key
                        eraser_mode = False
                    else:
                        print("unbound key clicked")

    if not input_active:
        lateralAcceleration()
        mouseactive = placeSand()
        praticlesmoving = newtonize()
    else:
        praticlesmoving = False
        mouseactive = False

    if praticlesmoving or mouseactive or needs_redraw or input_active:
        grd.fill((0, 0, 0))
        drawGrid()
        drawUI()
        if input_active:
            drawInputBox()
        pygame.display.flip()
        needs_redraw = False

    clock.tick(60)

pygame.quit()
sys.exit()