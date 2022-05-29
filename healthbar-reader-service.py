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
    img_bool = img_gray_array > 129

    is_upper_left_map_bar = check_bool_at_lines(img_bool, True, 48, 49, 52, 123)
    is_upper_right_map_bar = check_bool_at_lines(img_bool, True, 48, 49, 215, 286)
    is_bottom_left_map_bar = check_bool_at_lines(img_bool, True, 290, 291, 52, 123)
    is_bottom_right_map_bar = check_bool_at_lines(img_bool, True, 290, 291, 215, 286)

    is_upper_black_bar = check_bool_at_lines(img_bool, False, 956, 967, 217, 329)
    is_middle_black_bar = check_bool_at_lines(img_bool, False, 986, 995, 177, 329)
    is_bottom_black_bar = check_bool_at_lines(img_bool, False, 1020, 1026, 217, 392)

    print('Has upper left map bar: ' + str(is_upper_left_map_bar))
    print('Has upper right map bar: ' + str(is_upper_right_map_bar))
    print('Has bottom left map bar: ' + str(is_bottom_left_map_bar))
    print('Has bottom right map bar: ' + str(is_bottom_right_map_bar))
    print('Has black upper bar: ' + str(is_upper_black_bar))
    print('Has black middle bar: ' + str(is_middle_black_bar))
    print('Has black bottom bar: ' + str(is_bottom_black_bar))

    is_life_bar_found = (
        is_upper_left_map_bar and is_upper_right_map_bar and
        is_bottom_left_map_bar and is_bottom_right_map_bar and
        is_upper_black_bar and is_middle_black_bar and
        is_bottom_black_bar
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
    is_life_bar_found = False

    #determine if is_life_bar_found
    is_life_bar_found = True

    left = 575
    top = 1000
    right = 650
    bottom = 1045

    #(left, top) is the upper left pixel of the rectangle
    #(right, bottom) is the lower right pixel
    box = (left, top, right, bottom)
    img_cropped = img.crop(box)

    img_cropped_gray = img_cropped.convert('L')
    image_bin = img_cropped_gray.point( lambda p: 255 if p <= 129 else 0 )

    life_percentage = int(tess.image_to_string(image_bin, lang='eng',
        config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'))

    if is_life_bar_found and life_percentage > 0 and life_percentage <= 100:
        life_percentage = life_percentage / 100
    else:
        life_percentage = 0

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
    app.run(debug=True, port=8080)