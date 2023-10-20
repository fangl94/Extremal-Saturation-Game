from flask import Flask, render_template, request, jsonify,json, session
from itertools import combinations
from math import atan2
import random

app = Flask(__name__)
points = []
n = None
m = None

def convert_to_input_format(json_points):
    # Convert JSON-style points to the format suitable for the code
    points = [(float(p["x"]), float(p["y"])) for p in json_points]
    return points

def convert_to_output_format(convex_hull):
    if not convex_hull:
        return []  # Return an empty list if no convex n-gon was found
    return [{"x": p[0], "y": p[1]} for p in convex_hull]

def is_convex(polygon):
    if len(polygon) < 3:
        return False

    def cross_product(p1, p2, p3):
        return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

    positive, negative = False, False
    for i in range(len(polygon)):
        p1, p2, p3 = polygon[i], polygon[(i + 1) % len(polygon)], polygon[(i + 2) % len(polygon)]
        cp = cross_product(p1, p2, p3)
        if cp > 0:
            positive = True
        elif cp < 0:
            negative = True

    return not (positive and negative)

def find_convex_ngon(points, n):
    # Sort the points in counterclockwise order
    center = tuple(map(lambda x: sum(x) / len(x), zip(*points)))
    points.sort(key=lambda p: atan2(p[1] - center[1], p[0] - center[0]))
    if len(points) < n:
        return False

    for subset in combinations(points, n):
        if is_convex(list(subset)):
            return list(subset)  # Found an n-gon.

    return False  # Return an empty list if no convex n-gon was found.

# Define a function to check if three points are in a straight line
def are_three_points_in_line(points):
    if len(points) < 3:
        return False

    for i in range(len(points) - 2):
        for j in range(i + 1, len(points) - 1):
            for k in range(j + 1, len(points)):
                x1, y1 = points[i]['x'], points[i]['y']
                x2, y2 = points[j]['x'], points[j]['y']
                x3, y3 = points[k]['x'], points[k]['y']

                # Check if the points are collinear using the slope formula
                if (x2 - x1) * (y3 - y1) == (x3 - x1) * (y2 - y1):
                     collinear_points = [
                        {'x': x1, 'y': y1},
                        {'x': x2, 'y': y2},
                        {'x': x3, 'y': y3}
                    ]
                     return collinear_points

    return False

@app.route('/')
def index():
    return render_template('index.html')





@app.route('/add_point', methods=['POST'])
def add_point():
    data = request.get_json()
    added_point = None
    message = ""

    if 'points' in data:
       received_points = data['points']
       points.extend(received_points)

    added_point = points[-1]

        # Check if three points are in a straight line
    if are_three_points_in_line(points):
      message = "You lose the game: three lines in a line."
      game_status = "lost"
    else:
       message = "Game is in progress."
       game_status = "continue"
    print(message)

    if len(points) > 0:
    # Convert input JSON-style points to the format suitable for the code
       input_points = convert_to_input_format(points)

    # Find the convex hull
       convex_ngon = find_convex_ngon(input_points, n)

    # Convert the convex hull to JSON-style format
       output_points = convert_to_output_format(convex_ngon)

       print (n)
       print (output_points)
       if convex_ngon:
          print(f"Found a convex {n}-gon: {convex_ngon}")
          print(f"Found a convex {n}-gon in Json form: {output_points}")
          message2 = "You lose the game: You form a convex hull with the given n vertices."
          game_status = "lost"
       else:
        print(f"No convex {n}-gon found.")
        message2 = "Game is in progress."
        game_status = "continue"

    if len(points) == 2 ** (n- 2) and game_status != "lost":
       game_status = "win"
       message2 = "You win the  game"


    print(message)
    print(f'Current point list: {points}')  # Print the current list of points
    print(f'Point added at {points[-1]}')  # Print the added point
    return jsonify({'status': 'OK', 'added_point': added_point, 'points': points, 'message': message,'messages2':message2,'game_status': game_status, 'convex_ngon':output_points})


@app.route('/check_game_status', methods=['GET'])
def check_game_status():
    message = ""
    game_status = "continue"
    losing_points = []

    # Check if three points are in a straight line and get the losing points
    losing_points = are_three_points_in_line(points)

    if losing_points:
        message = "You lose the game."
        game_status = "lost"
        print(f'The three points in a line are:', losing_points)
    else:
        message = "Game is in progress."

    return jsonify({'message': message, 'game_status': game_status, 'losing_points': losing_points})


@app.route('/post_n', methods=['POST'])
def post_n():
    data = request.get_json()
    global n
    n = data.get('n')
   # session['n'] = n
    print(n)
    return jsonify({'message': f"Received n = {n}"}), 200


@app.route('/are_there_n_convex_gon', methods=['GET'])
def are_there_n_convex_gon():
    # Define the initial game status as "continue"
    game_status = "continue"

    # Convert input JSON-style points to the format suitable for the code
    input_points = convert_to_input_format(points)

    # Find the convex hull
    convex_ngon = find_convex_ngon(input_points, n)
        # Convert the convex hull to JSON-style format
    output_points = convert_to_output_format(convex_ngon)

    response_data={}

    if len(points) > 0:
       print (n)
       print (output_points)
       if convex_ngon:
          print(f"Found a convex {n}-gon: {convex_ngon}")
          print(f"Found a convex {n}-gon in Json form: {output_points}")
          response_data = {
            'message': f"You form a convex {n}-gon, you lose, please restart",
            'convex_ngon': output_points,
        }

          game_status = "lost"
       else:
        print(f"No convex {n}-gon found.")
        game_status = "continue"

    if len(points) == 2**(n-2) and game_status != "lost":
       game_status = "win"
       response_data = {'message': f"You win the game"}

    # Return the game status and response data
    return jsonify({'game_status': game_status, **response_data}), 200

# This route retrieves the current list of points using a GET request
@app.route('/get_points', methods=['GET'])
def get_points():
    return jsonify({'points': points})

@app.route('/clear_points', methods=['POST'])
def clear_points():
    data = request.get_json()
    if 'clear' in data and data['clear'] == True:
        points.clear()
        return jsonify({'status': 'OK', 'message': 'Points cleared'})
    else:
        return jsonify({'status': 'Error', 'message': 'Invalid request'})
    
@app.route('/saturation_game', methods=['GET'])
def saturation_game():
    return render_template('saturation_game.html')

@app.route('/extremal_game')
def extremal_game():
    return render_template('extremal_game.html')


@app.route('/post_m', methods=['POST'])
def post_():
    data = request.get_json()
    global m
    m = data.get('m')
   # session['n'] = n
    print("m is:",m)
    return jsonify({'message': f"Received m = {m}"}), 200


@app.route('/send_point_saturation', methods=['GET'])
def send_point_saturation():

    if m == 4:
        points_saturation = []  # Clear the points list
        lists = [
            [{'x': 99.0, 'y': 196.125}, {'x': 201.0, 'y': 156.125}, {'x': 289.0, 'y': 146.125}],
            [{'x': 198, 'y': 196.125}, {'x': 201.0, 'y': 156.125}, {'x': 289.0, 'y': 146.125}],
            [{'x': 72, 'y': 196.125}, {'x': 231.0, 'y': 156.125}, {'x': 289.0, 'y': 146.125}],
            [ { "x": 217, "y": 158.125 }, { "x": 116, "y": 418.125 }, { "x": 437, "y": 360.125 } ]
        ]
        random_list = random.choice(lists)
        points_saturation.extend(random_list)
        return jsonify({'message': f"Received m = {m}", 'current_points': points_saturation}), 200

    if m == 5:
        points_saturation = []  # Clear the points list
        lists = [
            [{ "x": 133, "y": 142.125 }, { "x": 109, "y": 449.125 }, { "x": 401, "y": 262.125 }, { "x": 154, "y": 267.125 }, { "x": 255, "y": 200.125 }, { "x": 258, "y": 318.125 }, { "x": 219, "y": 275.125 } ],
            [ { "x": 199, "y": 113.125 }, { "x": 82, "y": 411.125 }, { "x": 425, "y": 394.125 }, { "x": 179, "y": 256.125 }, { "x": 285, "y": 225.125 }, { "x": 236, "y": 372.125 }, { "x": 243, "y": 298.125 } ],
            [ { "x": 96, "y": 151.125 }, { "x": 426, "y": 145.125 }, { "x": 102, "y": 382.125 }, { "x": 319, "y": 290.125 }, { "x": 176, "y": 209.125 }, { "x": 247, "y": 263.125 } ],
            [ { "x": 149, "y": 157.125 }, { "x": 147, "y": 400.125 }, { "x": 333, "y": 150.125 }, { "x": 335, "y": 401.125 }, { "x": 74, "y": 98.125 }, { "x": 55, "y": 466.125 }, { "x": 399, "y": 98.125 } ],
        ]
        random_list = random.choice(lists)
        points_saturation.extend(random_list)
        return jsonify({'message': f"Received m = {m}", 'current_points': points_saturation}), 200

    if m == 6:
        points_saturation = []  # Clear the points list
        lists = [
            [ { "x": 205, "y": 70.125 }, { "x": 49, "y": 449.125 }, { "x": 446, "y": 437.125 }, { "x": 436, "y": 142.125 }, { "x": 96, "y": 184.125 }, { "x": 146, "y": 356.125 }, { "x": 350, "y": 354.125 }, { "x": 168, "y": 224.125 }, { "x": 325, "y": 219.125 } ]
            
        ]
        random_list = random.choice(lists)
        points_saturation.extend(random_list)
        return jsonify({'message': f"Received m = {m}", 'current_points': points_saturation}), 200

    print("The chosen points are: ", points, "The length of the points is: ", len(points))




@app.route('/add_point_saturation', methods=['POST'])
def add_point_saturation():
    data = request.get_json()
    added_point = None
    message = ""

    if 'points' in data:
       received_points = data['points']
       points.extend(received_points)

    added_point = points[-1]

        # Check if three points are in a straight line
    if are_three_points_in_line(points):
      message = "You lose the game: three lines in a line."
      game_status = "lost"
    else:
       message = "Game is in progress."
       game_status = "continue"
    print(message)

    if len(points) > 0:
    # Convert input JSON-style points to the format suitable for the code
       input_points = convert_to_input_format(points)

    # Find the convex hull
       convex_ngon = find_convex_ngon(input_points, m)

    # Convert the convex hull to JSON-style format
       output_points = convert_to_output_format(convex_ngon)

       print (m)
       print (output_points)
       if convex_ngon:
          print(f"Found a convex {m}-gon: {convex_ngon}")
          print(f"Found a convex {m}-gon in Json form: {output_points}")
          message2 = "You lose the game: You form a convex hull with the given n vertices."
          game_status = "lost"
       else:
        print(f"No convex {m}-gon found.")
        message2 = "Game is in progress."
        game_status = "continue"

    if len(points) == 2**(m-2) and game_status != "lost":
       game_status = "win"
       message2 = "You win the  game"


    print(message)
    print(f'Current point list: {points}')  # Print the current list of points
    print(f'Point added at {points[-1]}')  # Print the added point
    return jsonify({'status': 'OK', 'added_point': added_point, 'points': points, 'message': message,'messages2':message2,'game_status': game_status, 'convex_ngon':output_points})


@app.route('/are_there_n_convex_gon_saturation', methods=['GET'])
def are_there_n_convex_gon_saturation():
    # Define the initial game status as "continue"
    game_status = "continue"

    # Convert input JSON-style points to the format suitable for the code
    input_points = convert_to_input_format(points)

    # Find the convex hull
    convex_ngon = find_convex_ngon(input_points, m)
        # Convert the convex hull to JSON-style format
    output_points = convert_to_output_format(convex_ngon)

    response_data={}

    if len(points) > 0:
       print (m)
       print (output_points)
       if convex_ngon:
          print(f"Found a convex {m}-gon: {convex_ngon}")
          print(f"Found a convex {m}-gon in Json form: {output_points}")
          response_data = {
            'message': f"You form a convex {m}-gon, you lose, please restart",
            'convex_ngon': output_points,
        }

          game_status = "lost"
       else:
        print(f"No convex {m}-gon found.")
        game_status = "continue"

    if len(points) == 2**(m-2) and game_status != "lost":
       game_status = "win"
       response_data = {'message': f"You win the game"}

    # Return the game status and response data
    return jsonify({'game_status': game_status, **response_data}), 200

if __name__ == '__main__':
    app.run(debug=True)
