"""Airtime labyrinth challenge."""
import requests
import json

URL = "http://challenge2.airtime.com:7182"
HEADERS = {"X-Labyrinth-Email": "zbwener@gmail.com"}


def get_writing(room):
    """Get the writing on the wall of a room.
    Returns: tuple of (writing, order)."""
    response = requests.get(URL + "/wall",
                            params={"roomId": room},
                            headers=HEADERS)
    body = json.loads(response.text)
    return (body['writing'], int(body['order']))

def get_neighbors(room):
    """Get the neighbors for a given room."""
    neighbors = []
    response = requests.get(URL + "/exits", params={"roomId": room},
                            headers=HEADERS)
    directions = json.loads(response.text)["exits"]
    if not directions:
        return []
    for direction in directions:
        adj_room_response = requests.get(URL + "/move",
                                         params={"roomId": room,
                                                 "exit": direction},
                                         headers=HEADERS)
        neighbors.append(json.loads(adj_room_response.text)["roomId"])
    return neighbors

def main():
    """Run the search through the labyrinth"""
    broken = []
    wall_writing = []
    start_response = requests.get(URL + "/start", headers=HEADERS)
    start_room = json.loads(start_response.text)['roomId']
    # Do breadth-first search through the labyrinth.
    queue = [start_room]
    visited_rooms = {}
    while queue:
        curr_room = queue.pop(0)
        visited_rooms[curr_room] = True
        # Get the writing on current wall
        writing, order = get_writing(curr_room)
        if order == -1:
            broken.append(curr_room)
        else:
            # Keep track of (writing, order) tuples.
            wall_writing.append((writing, order))
        # Get new neighbors
        neighbors = get_neighbors(curr_room)
        for neighbor in neighbors:
            if neighbor not in visited_rooms:
                queue.append(neighbor)

    # Done with search through the labyrinth, so we can submit our data.
    challenge_code = ''.join([x[0] for x in
                              sorted(wall_writing, key=lambda x: x[1])])
    data = json.dumps({"roomIds": broken, "challenge": challenge_code})
    submit = requests.post(URL + "/report", data=data, headers=HEADERS)
    return submit.text

if __name__ == "__main__":
    print main()
