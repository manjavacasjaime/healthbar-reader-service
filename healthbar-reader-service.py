from flask import Flask, jsonify, request
from PIL import Image
import numpy as np
import sys
from matplotlib import pyplot as plt
import pytesseract as tess

app = Flask(__name__)

def show_binarized_image(img: Image, threshold: int):
    image_gray = img.convert('L')
    image_bin = image_gray.point( lambda p: 255 if p > threshold else 0 )
    image_bin.show()

def show_image_from_array(img: np.ndarray, mode: str):
    plt.imshow(img, mode)
    plt.show()

#Line gets marked with threshold color
def show_binarized_image_with_marked_line(img: np.ndarray, line: int, threshold: int):
    for i in range(len(img)):
        for j in range(len(img[i])):
            if i == line and img[i][j] > threshold:
                img[i][j] = threshold
            elif img[i][j] > threshold:
                img[i][j] = 255
            else:
                img[i][j] = 0
    show_image_from_array(img, 'gray')

#Column gets marked with threshold color
def show_binarized_image_with_marked_column(img: np.ndarray, column: int, threshold: int):
    for i in range(len(img)):
        for j in range(len(img[i])):
            if j == column and img[i][j] > threshold:
                img[i][j] = threshold
            elif img[i][j] > threshold:
                img[i][j] = 255
            else:
                img[i][j] = 0
    show_image_from_array(img, 'gray')

#Requires the script to run as administrator
def log(message: str):
    old_stdout = sys.stdout
    log_file = open('message.log', 'w')
    sys.stdout = log_file
    print(message)
    sys.stdout = old_stdout
    log_file.close()

#Check bool at lines x to y (inclusive) from index i to index j (inclusive)
def check_bool_at_lines(img: np.ndarray, boolToCheck: bool, x: int, y:int, i: int, j: int):
    line = x
    result = True
    while(line <= y):
        if check_bool_at_line(img, boolToCheck, line, i, j):
            line+=1
        else:
            result = False
            break

    return result

#Check bool at line x from index i to index j (inclusive)
def check_bool_at_line(img: np.ndarray, boolToCheck: bool, x: int, i: int, j: int):
    index = i
    result = True
    myBool = boolToCheck
    while(index <= j):
        if img[x][index] == myBool:
            index+=1
        else:
            print('Bar not found at: (' + str(x) + ', ' + str(index) + ')')
            result = False
            break
    
    return result

#Check bool at column i from line x to line y (inclusive)
def check_bool_at_column(img: np.ndarray, boolToCheck: bool, i: int, x: int, y: int):
    index = x
    result = True
    myBool = boolToCheck
    while(index <= y):
        if img[index][i] == myBool:
            index+=1
        else:
            print('Bar not found at: (' + str(index) + ', ' + str(i) + ')')
            result = False
            break
    
    return result

#Get the percentage of True bools at line x from index i to index j (inclusive)
def get_true_bool_percentage_at_line(img: np.ndarray, x: int, i: int, j: int):
    true_pixels = 0
    pixels = j - i + 1
    index = i
    while(index <= j):
        if img[x][index]:
            true_pixels+=1
        index+=1

    result = true_pixels / pixels
    result = round(result, 2)
    return result

#Get tuple (bool, float) with bool is_life_bar_found and float life_percentage
#Obtain this data from a fullHD (1920, 1080) Image
def get_life_percentage_from_apex_image(img: Image):
    img_gray_array = np.array(img.convert('L'))
    img_bool = img_gray_array > 210

    is_upper_left_map_bar = check_bool_at_lines(img_bool, True, 48, 49, 60, 120)
    is_upper_right_map_bar = check_bool_at_lines(img_bool, True, 48, 49, 220, 280)
    is_bottom_left_map_bar = check_bool_at_lines(img_bool, True, 290, 291, 60, 120)
    is_bottom_right_map_bar = check_bool_at_lines(img_bool, True, 290, 291, 220, 280)

    is_upper_left_map_black_bar = check_bool_at_line(img_bool, False, 50, 60, 120)
    is_upper_right_map_black_bar = check_bool_at_line(img_bool, False, 50, 220, 280)
    is_bottom_left_map_black_bar = check_bool_at_line(img_bool, False, 289, 60, 120)
    is_bottom_right_map_black_bar = check_bool_at_line(img_bool, False, 289, 220, 280)

    print('Has upper left map bar: ' + str(is_upper_left_map_bar))
    print('Has upper right map bar: ' + str(is_upper_right_map_bar))
    print('Has bottom left map bar: ' + str(is_bottom_left_map_bar))
    print('Has bottom right map bar: ' + str(is_bottom_right_map_bar))
    print('Has upper left black bar: ' + str(is_upper_left_map_black_bar))
    print('Has upper right black bar: ' + str(is_upper_right_map_black_bar))
    print('Has bottom left black bar: ' + str(is_bottom_left_map_black_bar))
    print('Has bottom right black bar: ' + str(is_bottom_right_map_black_bar))

    is_life_bar_found = (
        is_upper_left_map_bar and is_upper_right_map_bar and
        is_bottom_left_map_bar and is_bottom_right_map_bar and
        is_upper_left_map_black_bar and is_upper_right_map_black_bar and
        is_bottom_left_map_black_bar and is_bottom_right_map_black_bar
    )
    life_percentage = 0
    
    if is_life_bar_found:
        life_percentage = get_true_bool_percentage_at_line(img_bool, 1017, 177, 413)
        print('Life percentage: ' + str(life_percentage))

    return (is_life_bar_found, life_percentage)


@app.route('/healthbar-reader-service/apex/fullhd', methods=['POST'])
def read_apex_image_fullhd():
    data = request.get_data()

    error_message = ''
    try:
        img = Image.frombytes('RGBA', (1920, 1080), data)
        is_image_identified = True
    except IOError as e:
        error_message = str(e)
        is_image_identified = False
    
    is_life_bar_found = False
    life_percentage = 0

    if is_image_identified:
        (is_life_bar_found, life_percentage) = get_life_percentage_from_apex_image(img)

    return jsonify({
        'isImageIdentified' : is_image_identified,
        'errorMessage' : error_message,
        'isLifeBarFound' : is_life_bar_found,
        'lifePercentage' : life_percentage,
    })

#Get tuple (bool, float) with bool is_life_bar_found and float life_percentage
#Obtain this data from a fullHD (1920, 1079) Image
def get_life_percentage_from_valorant_image(img: Image):
    img_gray = img.convert('L')
    img_gray_array = np.array(img_gray)
    img_bool = img_gray_array > 210

    #Checking if player is in lobby screen
    is_logo_center_left_white_bar = check_bool_at_column(img_bool, True, 16, 10, 15)
    is_logo_center_right_white_bar = check_bool_at_column(img_bool, True, 17, 10, 15)
    is_logo_left_black_bar = check_bool_at_column(img_bool, False, 15, 10, 15)
    is_logo_right_black_bar = check_bool_at_column(img_bool, False, 18, 12, 15)

    is_in_lobby_screen = (
        is_logo_center_left_white_bar and is_logo_center_right_white_bar and
        is_logo_left_black_bar and is_logo_right_black_bar
    )

    if is_in_lobby_screen:
        is_life_bar_found = False
        print('Player found at lobby screen.')
        print('Is healthbar found: ' + str(is_life_bar_found))
        return (is_life_bar_found, 0)

    #Checking if player is dead
    is_center_white_bar = check_bool_at_column(img_bool, True, 30, 796, 800)
    is_left_black_bar = check_bool_at_column(img_bool, False, 29, 796, 800)
    is_right_black_bar = check_bool_at_column(img_bool, False, 31, 796, 800)

    is_dead_white_bar_found = (
        is_center_white_bar and is_left_black_bar and
        is_right_black_bar
    )

    if is_dead_white_bar_found:
        is_life_bar_found = True
        life_percentage = 0
        print('Player found at dead screen.')
        print('Is healthbar found: ' + str(is_life_bar_found))
        print('Life percentage: ' + str(life_percentage))
        return (is_life_bar_found, life_percentage)

    left = 575
    top = 1000
    right = 650
    bottom = 1045

    #(left, top) is the upper left pixel of the rectangle
    #(right, bottom) is the lower right pixel
    box = (left, top, right, bottom)
    img_cropped_gray = img_gray.crop(box)

    image_bin = img_cropped_gray.point( lambda p: 255 if p > 205 else 0 )

    life_percentage_str = tess.image_to_string(image_bin, lang='eng',
        config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    
    if not life_percentage_str:
        is_life_bar_found = False
        print('Is healthbar found: ' + str(is_life_bar_found))
        return (is_life_bar_found, 0)

    life_percentage = int(life_percentage_str)

    if life_percentage >= 1 and life_percentage <= 100:
        is_life_bar_found = True
        life_percentage = life_percentage / 100
        print('Life percentage: ' + str(life_percentage))
    else:
        is_life_bar_found = False
        life_percentage = 0
    print('Is healthbar found: ' + str(is_life_bar_found))

    return (is_life_bar_found, life_percentage)


@app.route('/healthbar-reader-service/valorant/fullhd', methods=['POST'])
def read_valorant_image_fullhd():
    data = request.get_data()

    error_message = ''
    try:
        img = Image.frombytes('RGBA', (1920, 1079), data)
        is_image_identified = True
    except IOError as e:
        error_message = str(e)
        is_image_identified = False
    
    is_life_bar_found = False
    life_percentage = 0

    if is_image_identified:
        (is_life_bar_found, life_percentage) = get_life_percentage_from_valorant_image(img)

    return jsonify({
        'isImageIdentified' : is_image_identified,
        'errorMessage' : error_message,
        'isLifeBarFound' : is_life_bar_found,
        'lifePercentage' : life_percentage,
    })
    

if __name__ == '__main__':
    app.run()