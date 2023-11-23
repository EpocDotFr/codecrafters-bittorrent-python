from collections import namedtuple

KeepAliveMessage = namedtuple('KeepAliveMessage', [])
ChokeMessage = namedtuple('ChokeMessage', [])
UnchokeMessage = namedtuple('UnchokeMessage', [])
InterestedMessage = namedtuple('InterestedMessage', [])
NotInterestedMessage = namedtuple('NotInterestedMessage', [])
HaveMessage = namedtuple('HaveMessage', ['piece_index'])
BitfieldMessage = namedtuple('BitfieldMessage', ['bits'])
RequestMessage = namedtuple('RequestMessage', ['index', 'begin', 'length'])
PieceMessage = namedtuple('PieceMessage', ['index', 'begin', 'block'])
CancelMessage = namedtuple('CancelMessage', ['index', 'begin', 'length'])
