"""Airtime transmission dev challenge."""
import socket
import collections

ADDRESS = ("challenge2.airtime.com", 2323)
EMAIL = "zbwener@gmail.com"

def get_int(byte_ar):
    """Get int from a big-endian bytearray"""
    return int(reduce(lambda x, y: x | y,
                      [x << i * 8 for i, x in enumerate(byte_ar[::-1])]))

def do_handshake(cnx):
    """Perform handshake with the server"""
    handshake = cnx.recv(4096)
    challenge_number = handshake[handshake.find(":") + 1:].strip()
    cnx.send("IAM:{0}:{1}:at\n".format(challenge_number, EMAIL))
    success = cnx.recv(4096)
    return success

def checksum(seq, data):
    """Computes checksum"""
    out = seq
    for i in range(0, len(data) - 3, 4):
        chunk = data[i:i + 4]
        out = bytearray([(out[j] ^ chunk[j]) & 0xFF for j in range(4)])
    leftovers = len(data) % 4
    if leftovers:
        lastchunk = bytearray(data[-(leftovers):])
        lastchunk += bytearray([0xAB for i in range(4 - leftovers)])
        out = bytearray([(out[j] ^ lastchunk[j]) & 0xFF for j in range(4)])
    return out

def stream():
    """Connect to the tcp server and stream the transmission. All the PCM data
    is stored in memory before written to disk--this works for this challenge,
    but it would have to be smarter at scale."""
    cnx = socket.create_connection(ADDRESS)
    success = do_handshake(cnx)
    if not success:
        raise Exception("Couldn't establish socket connection.")

    chunks = {}
    with open("data.pcm", "w") as file_obj:
        data = bytearray(cnx.recv(2048))
        while data:
            seq = data[:4]
            sequence_number = get_int(seq)
            chk = data[4:8]
            length = get_int(data[8:12])
            content = data[12:12 + length]
            computed_checksum = checksum(seq, content)
            # If the checksum matches, the content is good.
            if computed_checksum == chk:
                chunks[sequence_number] = content
            # Slice data to start of next packet and add new data if it exists.
            data = data[12 + length:]
            data += bytearray(cnx.recv(2048))
            ordered_chunks = collections.OrderedDict(sorted(chunks.items(),
                                                            key=lambda t: t[0]))
        for i in ordered_chunks:
            file_obj.write(ordered_chunks[i])
    # Finish connection.
    cnx.shutdown()
    cnx.close()

if __name__ == "__main__":
    stream()
