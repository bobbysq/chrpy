class ChrpFile:
    # TODO: Write proper setters for variables
    def __init__(self, data):
        self.size = len(data)

        self.chrp_version = int.from_bytes(data[0:4], 'little')

        self.checksum = int.from_bytes(data[-4:],'little')
        expected_checksum = 2**32 - 1 - sum(data[4:self.size-4])

        if (expected_checksum != self.checksum):
            raise InvalidChecksumException()
    
        num_tracks = int.from_bytes(data[4:6], 'little')
        total_notes = 0
        self.tracks = []
    
        for i in range(num_tracks):
            addr = 6 + i * 2
            track_len = int.from_bytes(data[addr:addr+2], 'little')
            track_addr = total_notes + 6 + num_tracks * 2

            self.tracks += [ChrpTrack(data, track_addr, track_len)]
            total_notes += track_len


class ChrpTrack:
    def __init__(self, data, start, length):
        self._notes = []

        for i in range(start, start + length * 12, 12):
            new_note = ChrpNote()

            new_note.note = int.from_bytes(data[i:i+2], 'little')
            new_note.vel = int.from_bytes(data[i+2:i+4], 'little')
            new_note.on = int.from_bytes(data[i+4:i+8], 'little')
            new_note.off = int.from_bytes(data[i+8:i+12], 'little')

            self._notes += [new_note]

    def __sizeof__(self) -> int:
        return len(self._notes)
    
    def __iter__(self):
        for note in self._notes:
            yield note

    def __getitem__(self, key):
        return self._notes[key]
    
    def __repr__(self) -> str:
        out = '['
        for note in self._notes:
            out += str(note) + ', '
        out = out.rstrip(', ')
        out += ']'
        return out
    
class ChrpNote:
    def __init__(self):
        self.note = 0
        self.vel = 0
        self.on = 0
        self.off = 0

    def to_byte_arr(self):
        arr = b''

        arr += self.note.to_bytes(2,'little')
        arr += self.vel.to_bytes(2,'little')
        arr += self.on.to_bytes(4,'little')
        arr += self.off.to_bytes(4,'little')

        return arr
    
    def __repr__(self) -> str:
        return f'ChrpNote: [note: {self.note}, vel: {self.vel}, on: {self.on}, off: {self.off}]'

class InvalidChecksumException(Exception):
    pass

def from_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    return ChrpFile(data)