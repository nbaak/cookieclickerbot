import cv2
import numpy as np
import time
import pyautogui
import pydirectinput
import keyboard
import random
import os

from multiprocessing import Process, Value, Manager

# settings
stop_key = 'q'
pause_key = 'p'

clicks = 50
special_cookies_path = 'images/special_cookies'

# buttons
btn_main_cookie = cv2.imread('images/main_cookie.jpg', cv2.IMREAD_UNCHANGED)

btn_buy_cursor = cv2.imread('images/cursor.jpg', cv2.IMREAD_UNCHANGED)
btn_buy_grandma = cv2.imread('images/grandma.jpg', cv2.IMREAD_UNCHANGED)
btn_buy_farm = cv2.imread('images/farm.jpg', cv2.IMREAD_UNCHANGED)
btn_buy_mine = cv2.imread('images/mine.jpg', cv2.IMREAD_UNCHANGED)
btn_buy_facility = cv2.imread('images/facility.jpg', cv2.IMREAD_UNCHANGED)
btn_buy_bank = cv2.imread('images/bank.jpg', cv2.IMREAD_UNCHANGED)

btn_close = cv2.imread('images/btn_close_messages.jpg', cv2.IMREAD_UNCHANGED)
gold_cookie = cv2.imread('images/gold_cookie.jpg', cv2.IMREAD_UNCHANGED)

# special cookies
special_cookies = []
entries = os.listdir(special_cookies_path)
for entry in entries:
    special_cookies.append((cv2.imread(f'{special_cookies_path}/{entry}', cv2.IMREAD_UNCHANGED), entry))
    

def get_needle_coords(image, needle):
    result = cv2.matchTemplate(image, needle, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= .8:
        return max_loc
    else:
        return None
        
def get_needle_coords_multi(image, needle_container, return_list, threshold=.65):
    needle, name = needle_container
    result = cv2.matchTemplate(image, needle, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        print(f"found special cookie with {name}")
        print(max_val, max_loc)
        return_list.append(max_loc)
        
def try_click_coordinates(coordinates=None, x_offset=10, y_offset=10):
    '''
        @param cooridinates: tuple with coordinates (x,y)
    '''
    if coordinates:
        x,y = coordinates
        pydirectinput.click(x+x_offset, y+y_offset)

def try_move_coordinates(coordinates=None, x_offset=10, y_offset=10):
    '''
        @param cooridinates: tuple with coordinates (x,y)
    '''
    if coordinates:
        x,y = coordinates
        pydirectinput.moveTo(x+x_offset, y+y_offset)

def click_main_cookie(coordinates, clicks):
    print("clicking cookie")
    #coordinates = get_needle_coords(img, btn_main_cookie)
    try_click_coordinates(coordinates, 100, 100)
    
    index = 0    
    while not keyboard.is_pressed('p'):
        pydirectinput.click()
        # if index % 100 == 0:
        #     print(index)
            
        if index > clicks:
            break
        
        index += 1

def click_gold_cookie():
    print("gold cookie")
    img  = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    coordinates = get_needle_coords(img, gold_cookie)
    try_click_coordinates(coordinates, 5, 5)

def buy(coordinates):
    try_click_coordinates(coordinates, 10, 10)
    for i in range(2):
        pydirectinput.click()
        
def close():
    print("close")
    img  = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    coordinates = get_needle_coords(img, btn_close)
    try_click_coordinates(coordinates, 5, 5)


# multi processing stuff
def clicking(running, paused):
    while running.value:
        if not paused.value:
            pyautogui.click()
    
def move_mouse(running, paused, target_queue):
    img  = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    coordinates_main_cookie = get_needle_coords(img, btn_main_cookie)
    
    while running.value:
        if not paused.value:
            if any(target_queue):
                coordinates = target_queue.pop(0)
                print("goto: ", coordinates)
                try_move_coordinates(coordinates, 10, 10)
            else:
                try_move_coordinates(coordinates_main_cookie, 100, 100)

def detect_key_input(running, paused):
    img = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    g_c = get_needle_coords(img, btn_buy_grandma)
    
    while running.value:
        if keyboard.is_pressed(pause_key) and not paused.value:
            print("pause ")
            paused.value = True
            time.sleep(.1)
        elif keyboard.is_pressed(pause_key) and paused.value:
            print("stop pause!")
            paused.value = False
            time.sleep(.1)
        
        if keyboard.is_pressed(stop_key):
            print("STOP")
            running.value = False
            
def detect_special_cookies(running, paused, target_queue):
    search_manager = Manager()
    targets = search_manager.list()
    jobs = []
    my_special_cookies = special_cookies.copy()
    random.shuffle(my_special_cookies)
    
    # delay start
    delay = 2 * random.random()
    time.sleep(delay)
    print(f"delay start for {delay} sec")
    
    while running.value:
        img = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
        for i, needle in enumerate(my_special_cookies):
            p = Process(target=get_needle_coords_multi, args=(img,needle,target_queue, .65))
            p.start()


# debug stuff
def pure_cookie_clicking():
    img  = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    coordinates_main_cookie = get_needle_coords(img, btn_main_cookie)
    while not keyboard.is_pressed('p'):
         click_main_cookie(coordinates_main_cookie, 1_000)
        
def debug():
    list_coodrdinates = []
    img  = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    coordinates_main_cookie = get_needle_coords(img, btn_main_cookie)
    
    list_coodrdinates.append(get_needle_coords(img, btn_buy_cursor))
    list_coodrdinates.append(get_needle_coords(img, btn_buy_grandma))
    list_coodrdinates.append(get_needle_coords(img, btn_buy_farm))
    list_coodrdinates.append(get_needle_coords(img, btn_buy_mine))
    list_coodrdinates.append(get_needle_coords(img, btn_buy_facility))
    list_coodrdinates.append(get_needle_coords(img, btn_buy_bank))
    
    random.shuffle(list_coodrdinates)
    index = 0
    max_list = len(list_coodrdinates)
  
    while not keyboard.is_pressed('p'):
        for _ in range(4):
            click_main_cookie(coordinates_main_cookie, clicks)
            click_gold_cookie()
        
        # buy something
        buy(list_coodrdinates[index])
        
        close()
        index += 1
        index = index % max_list
        time.sleep(2)
        
       
        
if __name__ == '__main__':
    manager = Manager()
    target_queue = manager.list()
    running = Value('i', True)
    paused = Value('i', False)
    
    # time to start
    for i in list(range(4,0,-1)):
        print(i)
        time.sleep(1)
    
    starting_queue = [(move_mouse,(running, paused, target_queue)), 
                      (clicking,(running, paused)), 
                      (detect_key_input,(running, paused)),
                      (detect_special_cookies, (running, paused, target_queue)),
                      (detect_special_cookies, (running, paused, target_queue))]
    processes = []
    
    for function,args in starting_queue:
        p = Process(target=function, args=args)
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
    
    # pure_cookie_clicking()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    