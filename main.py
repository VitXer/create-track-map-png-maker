import requests
import datetime
from PIL import Image, ImageDraw, ImageFont


def fetch_data():
    url_trains = "http://192.168.1.40:3876/api/trains"
    url_network = "http://192.168.1.40:3876/api/network"

    try:
        response_trains = requests.get(url_trains)
        response_trains.raise_for_status()  # Raises exception for 4xx or 5xx status codes
        data_trains = response_trains.json()  # Parse response as JSON

        response_network = requests.get(url_network)
        response_network.raise_for_status()  # Raises exception for 4xx or 5xx status codes
        data_network = response_network.json()  # Parse response as JSON

        return data_trains, data_network

    except requests.exceptions.RequestException as e:
        print("Wystąpił błąd podczas żądania HTTP:", e)
        return None, None


def plot_map(trains_data, network_data):
    if trains_data is None or network_data is None:
        return
    minx = float('inf')
    maxx = -float('inf')
    miny = float('inf')
    maxy = -float('inf')

    for track in network_data['tracks']:
        for path in track['path']:
            if path['x'] > maxx:
                maxx = path['x']
            if path['x'] < minx:
                minx = path['x']
            if path['z'] > maxy:
                maxy = path['z']
            if path['z'] < miny:
                miny = path['z']

    img_size_x = maxx - minx + 30
    img_size_y = maxy - miny + 30

    addx = -minx + 15
    addz = -miny + 15

    with Image.new('RGBA', (int(img_size_x), int(img_size_y)), (255, 255, 255, 255)) as im:

        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("arial.ttf", 12)

        for track in network_data['tracks']:
            draw_track(draw, addx, addz, track)

        for train in trains_data['trains']:
            for car in train['cars']:
                draw.line(
                    (addx + car['leading']['location']['x'], addz + car['leading']['location']['z'],
                     addx + car['trailing']['location']['x'], addz + car['trailing']['location']['z']),
                    (255, 0, 127, 255), width=3
                )

            draw.text(
                (addx + train['cars'][0]['leading']['location']['x'] - 3,
                 addz + train['cars'][0]['leading']['location']['z'] - 6), train['name'], fill=(0, 255, 0, 255),
                font=font
            )

        im.save(f"{int(datetime.datetime.timestamp(datetime.datetime.now()))}.png", "PNG")


def draw_track(draw, addx, addz, track, color=(0, 0, 0, 255), width=0, segments=5):
    path = track['path']
    points = path if len(path) != 4 else bezier_curve(*path, segments=segments)
    draw.line([(addx + point['x'], addz + point['z']) for point in points], color, width)


def bezier_curve(p0, p1, p2, p3, segments):
    points = []
    for i in range(segments + 1):
        t = i / segments
        x = (1 - t) ** 3 * p0['x'] + 3 * (1 - t) ** 2 * t * p1['x'] + 3 * (1 - t) * t ** 2 * p2['x'] + t ** 3 * p3['x']
        y = (1 - t) ** 3 * p0['z'] + 3 * (1 - t) ** 2 * t * p1['z'] + 3 * (1 - t) * t ** 2 * p2['z'] + t ** 3 * p3['z']
        points.append({'x': x, 'z': y})
    return points


def main():
    trains_data, network_data = fetch_data()
    plot_map(trains_data, network_data)


if __name__ == "__main__":
    main()
