import sys
import subprocess
import os.path
import re

DEVICES = {}
LOCATION = 'static/sf-workspace/'

# get device info from file


def init():
    try:
        with open(LOCATION + 'devices.txt', 'r') as f:
            for line in f:
                line = line.strip('\n')
                line = line.split(', ')
                if len(line) != 5:
                    continue
                DEVICES[line[0].lower()] = {
                    'name': line[0],
                    'dev_width': int(line[1]),
                    'dev_height': int(line[2]),
                    'eff_width': int(line[3]),
                    'eff_height': int(line[4]),
                }
        return 0
    except FileNotFoundError:
        print("Devices file not found.")
        return -1
    except IOError as e:
        print("An error occurred while working with the file:", e)
        return -1

# add a device to DEVICES dictionary


def add_device(name, dev_width, dev_height, eff_width, eff_height):
    DEVICES[name.lower()] = {
        'name': name,
        'dev_width': dev_width,
        'dev_height': dev_height,
        'eff_width': eff_width,
        'eff_height': eff_height,
    }

# write device info to file


def end():
    try:
        with open(LOCATION + 'devices.txt', 'w') as f:
            for device in DEVICES:
                f.write(DEVICES[device]['name'] + ', ' + str(DEVICES[device]['dev_width']) + ', ' + str(DEVICES[device]['dev_height']) + ', ' + str(
                    DEVICES[device]['eff_width']) + ', ' + str(DEVICES[device]['eff_height']) + '\n')
    except FileNotFoundError:
        print("Devices file not found.")
    except IOError as e:
        print("An error occurred while working with the file:", e)


def get_image_size(image_file):
    # get image size
    try:
        result = subprocess.run([
            'identify',
            image_file,
        ], capture_output=True)
    except subprocess.CalledProcessError as e:
        print("Error occurred while getting image size:", e)
        sys.exit(1)

    # parse result
    result = result.stdout.decode('utf-8')
    match = re.search(r'(\d+)x(\d+)', result)
    if match:
        width = match.group(1)
        return {
            'width': int(match.group(1)),
            'height': int(match.group(2))
        }

    return -1


def resize_image(image_file, dimension, val, output_file):
    try:
        if dimension == 'width':
            # resize width
            subprocess.run([
                'convert',
                image_file,
                '-resize', str(val) + 'x',
                output_file,
            ])
        else:
            # resize height
            subprocess.run([
                'convert',
                image_file,
                '-resize', 'x' + str(val),
                output_file,
            ])
    
    except subprocess.CalledProcessError as e:
        print("Error occurred while resizing image:", e)
        sys.exit(1)

    return output_file


# add border to top and bottom of image
def add_border(file, size):
    try:
        subprocess.run([
            'convert',
            file,
            '-bordercolor', 'black',
            '-border', '0x' + str(size),
            file,
        ])
    except subprocess.CalledProcessError as e:
        print("Error occurred while adding border:", e)
        sys.exit(1)


def crop_image_half(input_file, output_file):
    try:
        subprocess.run([
            'convert',
            input_file,
            '-crop', '50%x100%',  # Crop vertically into two equal parts
            output_file,
        ])
    except subprocess.CalledProcessError as e:
        print("Error occurred while cropping image in half:", e)
        sys.exit(1)

    return output_file.split('.')[0] + '-0.jpg', output_file.split('.')[0] + '-1.jpg'


def create_canvas(width, height, filename='canvas.jpg'):
    try:
        subprocess.run([
            'convert',
            '-size', str(width) + 'x' + str(height),
            'canvas:black',
            filename,
        ])
    except subprocess.CalledProcessError as e:
        print("Error occurred while creating canvas:", e)
        sys.exit(1)

    return filename


def add_images_to_canvas(canvas_file, image1, x1, y1, image2, x2, y2):
    image1_size = get_image_size(image1)
    if image1_size == -1:
        print("image size error")
        return -1
    
    try:
        subprocess.run([
            'convert',
            canvas_file,
            image1,
            '-geometry', '+' + str(x1) + '+' + str(y1),
            '-colorspace', 'sRGB',
            '-composite',
            canvas_file,
        ])

        subprocess.run([
            'convert',
            canvas_file,
            image2,
            '-geometry', '+' + str(x2) + '+' + str(y2),
            '-colorspace', 'sRGB',
            '-composite',
            canvas_file,
        ])
    except subprocess.CalledProcessError as e:
        print("Error occurred while adding image to canvas:", e)
        sys.exit(1)


def format_stereo(img, device, output_filename='output.jpg'):

    output = LOCATION + output_filename

    # get device info
    device = device.lower()
    device = DEVICES[device]

    size = get_image_size(img)
    if size == -1:
        print("image size error")
        return

    # check if new width is greater than device width if height is scaled to eff_height
    new_width = (device['eff_height'] / size['height']) * size['width']

    if new_width > device['dev_width']:

        # resize image width to device width
        resize_image(img, 'width', device['dev_width'], output)

        # add black borders to top and bottom until height = device height
        new_size = get_image_size(output)
        if new_size == -1:
            print('image size error')
            return

        if new_size['height'] < device['dev_height']:
            add_border(
                output, (device['dev_height'] - new_size['height']) // 2)

        new_size = get_image_size(output)
        if new_size == -1:
            print('image size error')
            return
        if new_size['height'] < device['dev_height']:

            # add extra pixels if needed to make it device height
            try:
                subprocess.run([
                    'convert',
                    output,
                    '-background', 'black',
                    '-gravity', 'south',
                    '-splice', '0x' +
                    str(device['dev_height'] - new_size['height']),
                    output,
                ])
            except subprocess.CalledProcessError as e:
                print("Error occurred while adding extra pixels to height:", e)
                return

        elif new_size['height'] > device['dev_height']:

            # crop image if needed to make it device height
            try:
                subprocess.run([
                    'convert',
                    output,
                    '-crop', str(device['dev_width']) + 'x' +
                    str(device['dev_height']) + '+0+0',
                    output,
                ])
            except subprocess.CalledProcessError as e:
                print("Error occurred while getting image size:", e)
                return

        try:
            subprocess.run([
                'convert',
                output,
                '-quality', '97',
                output,
            ])
        except subprocess.CalledProcessError as e:
            print("Error occurred while converting image quality:", e)
            return

    else:
        # resize image height to eff_height
        resize_image(img, 'height', device['eff_height'], output)
        new_size = get_image_size(output)
        if new_size == -1:
            print('image size error')
            return

        # crop image in half
        half1, half2 = crop_image_half(output, output)

        # canvas is the same as the goal: device width x device height
        canvas = create_canvas(
            device['dev_width'], device['dev_height'], output)

        gap = device['eff_width'] - new_size['width']

        # Start first half where there is an extra border around it if needed to make the image width = device width
        w1_start = (device['dev_width'] - new_size['width'] - gap) // 2

        # Start second half of image after the gap
        h2_size = get_image_size(half2)['width']
        if h2_size == -1:
            print('image size error')
            return
        
        w2_start = device['dev_width'] -  w1_start - h2_size

        # if device width == eff width, center images within each half
        if w1_start == 0:
            w1_start = gap // 4
            w2_start = device['dev_width'] - w1_start - h2_size

        # Start both halves where there is a top/bottom border to make the image height = device height
        height = (device['dev_height'] - new_size['height']) // 2

        add_images_to_canvas(canvas, half1, w1_start,
                             height, half2, w2_start, height)

        try:
            subprocess.run([
                'convert',
                output,
                '-quality', '97',
                output,
            ])
        except subprocess.CalledProcessError as e:
            print("Error occurred while converting image quality:", e)
            return

        # remove temporary files
        fname = output.split('.', 1)
        if os.path.exists(fname[0] + '-0.' + fname[1]):
            os.remove(fname[0] + '-0.' + fname[1])
        if os.path.exists(fname[0] + '-1.' + fname[1]):
            os.remove(fname[0] + '-1.' + fname[1])

    return output


def start():
    # not enough arguments
    if len(sys.argv) < 2:
        print(
            "Usage: \npython3 stereo-formatting.py -f <input image> <device> [output file name]\npython3 stereo-formatting.py -a <device> <device width> <device height> <effective width> <effective height>")
        return

    flag = sys.argv[1]

    # formatting image
    if flag == '-f':

        # incorrect format arguments
        if len(sys.argv) < 4 or len(sys.argv) > 5:
            print(
                "Usage: python3 stereo-formatting.py -f <input image> <device> [output file name]")
            return
        else:
            # get file and check it exists
            img = sys.argv[2]
            if not os.path.isfile(img):
                print("File does not exist")
                return

            # get device and check it exists
            device = sys.argv[3]
            device = device.lower()
            if device not in DEVICES:
                print("Device not found")
                return

            # get output file name if user specified one
            file = ""
            if len(sys.argv) == 5:
                if sys.argv[4].count('.') != 1 or sys.argv[4].split('.')[1].lower() != 'jpg':
                    print("Invalid output file name")
                    return
                file = format_stereo(img, device, sys.argv[4])
            else:
                file = format_stereo(img, device)

            print("Your new image is:", file)

    # adding device
    elif flag == '-a':

        # incorrect add arguments
        if len(sys.argv) != 7:
            print(
                "Usage: python3 stereo-formatting.py -a <device> <device width> <device height> <effective width> <effective height>")
            return

        else:
            device = sys.argv[2]

            # get device info and check that inputs are numbers
            if not sys.argv[3].isdigit():
                print("Invalid device width")
                return
            dev_width = int(sys.argv[3])

            if not sys.argv[4].isdigit():
                print("Invalid device height")
                return
            dev_height = int(sys.argv[4])

            if not sys.argv[5].isdigit():
                print("Invalid effective width")
                return
            eff_width = int(sys.argv[5])

            if not sys.argv[6].isdigit():
                print("Invalid effective height")
                return
            eff_height = int(sys.argv[6])

            add_device(device, dev_width, dev_height, eff_width, eff_height)

            print("Device added")
    else:
        print(
            "Usage: \npython3 stereo-formatting.py -f <input image> <device> [output file name]\npython3 stereo-formatting.py -a <device> <device width> <device height> <effective width> <effective height>")
        return


if __name__ == '__main__':
    res = init()
    if res == 0:
        start()
        end()
