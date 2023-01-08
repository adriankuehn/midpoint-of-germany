import os
import numpy as np
from PIL import Image


def create_list_coord(txt_data):
    list_coord = []
    for line in txt_data:
        line.rstrip()
        coordinates, number = line.replace(',', '.').split('       ')
        coord_1, coord_2 = coordinates.split(' ')
        list_coord.append([round(float(coord_1), 3), round(float(coord_2), 3), int(number)])
    return list_coord


def get_max_min(list_k):
    return max(list_k, key=lambda x:x[0])[0], max(list_k, key=lambda x:x[1])[1], min(list_k, key=lambda x:x[0])[0], min(list_k, key=lambda x:x[1])[1]


def determine_squares(list_coord, max_x, max_y, min_x, min_y, acc_y):
    step = (max_y - min_y) / acc_y
    l_square_inside, z_yyy = [], 0
    yyy = min_y - step
    while yyy < max_y:  # Devide area in many small squares with coordinates (xxx, yyy)
        if z_yyy % 50 == 0: print('Progress fill squares:  ', round((yyy - min_y + step) / (max_y - min_y) * 100, 1), '%')
        yyy = round(yyy + step, 2)
        list_intersections = []
        for ko in range(0, len(list_coord) - 1, 1):  # Calculate all the intersection with the borders in X-direction
            if (list_coord[ko][1] > yyy and list_coord[ko + 1][1] < yyy) or (list_coord[ko][1] < yyy and list_coord[ko + 1][1] > yyy):
                p1, p2 = list_coord[ko], list_coord[ko + 1]
                dif_p_x = p2[0] - p1[0]
                dif_q_y = p1[1] - yyy
                dif_p_y = p1[1] - p2[1]
                intersection_x = p1[0] + dif_p_x * (dif_q_y / dif_p_y)
                list_intersections.append(intersection_x)

        xxx = min_x - step
        while xxx < max_x:  # Determine all squares which are inside the area based on the intersections from list_intersections
            xxx = round(xxx + step, 2)
            number_inter = 0
            for inter_x in list_intersections:
                if inter_x > xxx: number_inter += 1
            if number_inter % 2 != 0: l_square_inside.append([xxx, yyy])
        z_yyy += 1

    number_squares = len(l_square_inside)
    print('Number of filled squares: ', number_squares)
    print()

    """ Calculate sum of distances for each square to all other squares:
        This is the part in the programm which costs the most runtime. All other parts (Creating the picture or fillling
        the area with squares) have linear runtime. This part has exponential runtime. Therefore numpy is 
        used in order to make the calculation as fast as possible. To use one outer for-loop here is actually faster
        than V2 and V3. Also with V2 and V3 you will get memory problems for high accuracies... """
    arr, arr_dis = np.array(l_square_inside), np.zeros(number_squares)
    for i_a in range(len(arr)):
        if i_a % 5000 == 0: print('Progress calc sums:  ', round(i_a / number_squares * 100, 1), '%')
        arr_dis[i_a] = np.sum(((arr[i_a, 0] - arr[:, 0]) ** 2 + (arr[i_a, 1] - arr[:, 1]) ** 2) ** 0.5)
    # V2: arr_dis = np.sum(np.sum((arr - arr.reshape((-1, 1, 2))) ** 2, axis=2) ** 0.5, axis=1)
    # V3: arr_dis = np.sum( ((arr[:, 0] - arr[:, 0].reshape(-1, 1)) ** 2 + (arr[:, 1] - arr[:, 1].reshape(-1, 1)) ** 2) ** 0.5, axis=1)

    return np.hstack((arr, arr_dis.reshape(-1, 1)))


def main(size, pix_size_q, pix_size_r, acc_y, folder_name):
    list_coordinates = [[369803.619, 5932471.326, 3359]]  # Intersection point of all islands to connect with two lines
    for data in os.listdir(folder_name):
        Data_Main = open(folder_name + '/' + data, 'r')  # Read all the coordinates
        list_coordinates.extend(create_list_coord(Data_Main))
        list_coordinates.append([369803.619, 5932471.326, 3359])

    max_x, max_y, min_x, min_y = get_max_min(list_coordinates)
    print('Read in coordinates:    Finished')

    list_squares = determine_squares(list_coordinates, max_x, max_y, min_x, min_y, acc_y)  # Calculate midpoint
    midpoint = list(min(list_squares, key=lambda x:x[2]))
    outpoint = list(max(list_squares, key=lambda x:x[2]))
    print()
    print('midpoint:                           ', midpoint)
    print('outpoint:                           ', outpoint)
    print('Calculation:    Finished')


    img = Image.new('RGB', [size, size], "white")  # Plot the squares and save as picture
    data = img.load()
    rmax_x, rmax_y, rmin_x, rmin_y = max_x * 1.05, max_y * 1.05, min_x * 0.95, min_y * 0.95

    for kk in list_coordinates:
        xx = ((kk[0] - rmin_x) / (rmax_x - rmin_x)) * size * ((rmax_x - rmin_x) / (rmax_y - rmin_y))
        yy = (1 - ((kk[1] - rmin_y) / (rmax_y - rmin_y))) * size
        for pix_y in range(-pix_size_r, pix_size_r + 1, 1):
            for pix_x in range(-pix_size_r, pix_size_r + 1, 1):
                data[xx + pix_x, yy + pix_y] = (0, 0, 255,)
    for qq in list_squares:
        xx = ((qq[0] - rmin_x) / (rmax_x - rmin_x)) * size * ((rmax_x - rmin_x) / (rmax_y - rmin_y))
        yy = (1 - ((qq[1] - rmin_y) / (rmax_y - rmin_y))) * size
        value = int(((qq[2] - midpoint[2]) / (outpoint[2] - midpoint[2])) * 255)
        if list(qq[0:2]) == midpoint[0:2]: Farbe = (255, 0, 0,)
        elif list(qq[0:2]) == outpoint[0:2]: Farbe = (0, 255, 0,)
        else: Farbe = (value, value, value,)
        for pix_y in range(-pix_size_q, pix_size_q + 1, 1):
            for pix_x in range(-pix_size_q, pix_size_q + 1, 1):
                data[xx + pix_x, yy + pix_y] = Farbe
    img.save('Result.png')
    print('Plot and save as .png:    Finished')


# Parameters:
folder = "Festland_und_Inseln"
image_size = 20000
pixel_size_quad = 6
pixel_size_border = 5
accuracy_y = 1000      # Runtimes:  500=1min  1000=45min  1500=7h
# Area of Germany in km² = (876 / accuracy_y)^2 * number_of_filled_squares

main(image_size, pixel_size_quad, pixel_size_border, accuracy_y, folder)
print()
print('The coordinates can be converted and depicted on a map using this website: www.koordinaten-umrechner.de')
print('The coordinates are based on the coordinate reference system ETRS89/UTM')
