#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\encodings\cp775.py
import codecs

class Codec(codecs.Codec):

    def encode(self, input, errors = 'strict'):
        return codecs.charmap_encode(input, errors, encoding_map)

    def decode(self, input, errors = 'strict'):
        return codecs.charmap_decode(input, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final = False):
        return codecs.charmap_encode(input, self.errors, encoding_map)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final = False):
        return codecs.charmap_decode(input, self.errors, decoding_table)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='cp775', encode=Codec().encode, decode=Codec().decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)


decoding_map = codecs.make_identity_dict(range(256))
decoding_map.update({128: 262,
 129: 252,
 130: 233,
 131: 257,
 132: 228,
 133: 291,
 134: 229,
 135: 263,
 136: 322,
 137: 275,
 138: 342,
 139: 343,
 140: 299,
 141: 377,
 142: 196,
 143: 197,
 144: 201,
 145: 230,
 146: 198,
 147: 333,
 148: 246,
 149: 290,
 150: 162,
 151: 346,
 152: 347,
 153: 214,
 154: 220,
 155: 248,
 156: 163,
 157: 216,
 158: 215,
 159: 164,
 160: 256,
 161: 298,
 162: 243,
 163: 379,
 164: 380,
 165: 378,
 166: 8221,
 167: 166,
 168: 169,
 169: 174,
 170: 172,
 171: 189,
 172: 188,
 173: 321,
 174: 171,
 175: 187,
 176: 9617,
 177: 9618,
 178: 9619,
 179: 9474,
 180: 9508,
 181: 260,
 182: 268,
 183: 280,
 184: 278,
 185: 9571,
 186: 9553,
 187: 9559,
 188: 9565,
 189: 302,
 190: 352,
 191: 9488,
 192: 9492,
 193: 9524,
 194: 9516,
 195: 9500,
 196: 9472,
 197: 9532,
 198: 370,
 199: 362,
 200: 9562,
 201: 9556,
 202: 9577,
 203: 9574,
 204: 9568,
 205: 9552,
 206: 9580,
 207: 381,
 208: 261,
 209: 269,
 210: 281,
 211: 279,
 212: 303,
 213: 353,
 214: 371,
 215: 363,
 216: 382,
 217: 9496,
 218: 9484,
 219: 9608,
 220: 9604,
 221: 9612,
 222: 9616,
 223: 9600,
 224: 211,
 225: 223,
 226: 332,
 227: 323,
 228: 245,
 229: 213,
 230: 181,
 231: 324,
 232: 310,
 233: 311,
 234: 315,
 235: 316,
 236: 326,
 237: 274,
 238: 325,
 239: 8217,
 240: 173,
 241: 177,
 242: 8220,
 243: 190,
 244: 182,
 245: 167,
 246: 247,
 247: 8222,
 248: 176,
 249: 8729,
 250: 183,
 251: 185,
 252: 179,
 253: 178,
 254: 9632,
 255: 160})
decoding_table = u'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\u0106\xfc\xe9\u0101\xe4\u0123\xe5\u0107\u0142\u0113\u0156\u0157\u012b\u0179\xc4\xc5\xc9\xe6\xc6\u014d\xf6\u0122\xa2\u015a\u015b\xd6\xdc\xf8\xa3\xd8\xd7\xa4\u0100\u012a\xf3\u017b\u017c\u017a\u201d\xa6\xa9\xae\xac\xbd\xbc\u0141\xab\xbb\u2591\u2592\u2593\u2502\u2524\u0104\u010c\u0118\u0116\u2563\u2551\u2557\u255d\u012e\u0160\u2510\u2514\u2534\u252c\u251c\u2500\u253c\u0172\u016a\u255a\u2554\u2569\u2566\u2560\u2550\u256c\u017d\u0105\u010d\u0119\u0117\u012f\u0161\u0173\u016b\u017e\u2518\u250c\u2588\u2584\u258c\u2590\u2580\xd3\xdf\u014c\u0143\xf5\xd5\xb5\u0144\u0136\u0137\u013b\u013c\u0146\u0112\u0145\u2019\xad\xb1\u201c\xbe\xb6\xa7\xf7\u201e\xb0\u2219\xb7\xb9\xb3\xb2\u25a0\xa0'
encoding_map = {0: 0,
 1: 1,
 2: 2,
 3: 3,
 4: 4,
 5: 5,
 6: 6,
 7: 7,
 8: 8,
 9: 9,
 10: 10,
 11: 11,
 12: 12,
 13: 13,
 14: 14,
 15: 15,
 16: 16,
 17: 17,
 18: 18,
 19: 19,
 20: 20,
 21: 21,
 22: 22,
 23: 23,
 24: 24,
 25: 25,
 26: 26,
 27: 27,
 28: 28,
 29: 29,
 30: 30,
 31: 31,
 32: 32,
 33: 33,
 34: 34,
 35: 35,
 36: 36,
 37: 37,
 38: 38,
 39: 39,
 40: 40,
 41: 41,
 42: 42,
 43: 43,
 44: 44,
 45: 45,
 46: 46,
 47: 47,
 48: 48,
 49: 49,
 50: 50,
 51: 51,
 52: 52,
 53: 53,
 54: 54,
 55: 55,
 56: 56,
 57: 57,
 58: 58,
 59: 59,
 60: 60,
 61: 61,
 62: 62,
 63: 63,
 64: 64,
 65: 65,
 66: 66,
 67: 67,
 68: 68,
 69: 69,
 70: 70,
 71: 71,
 72: 72,
 73: 73,
 74: 74,
 75: 75,
 76: 76,
 77: 77,
 78: 78,
 79: 79,
 80: 80,
 81: 81,
 82: 82,
 83: 83,
 84: 84,
 85: 85,
 86: 86,
 87: 87,
 88: 88,
 89: 89,
 90: 90,
 91: 91,
 92: 92,
 93: 93,
 94: 94,
 95: 95,
 96: 96,
 97: 97,
 98: 98,
 99: 99,
 100: 100,
 101: 101,
 102: 102,
 103: 103,
 104: 104,
 105: 105,
 106: 106,
 107: 107,
 108: 108,
 109: 109,
 110: 110,
 111: 111,
 112: 112,
 113: 113,
 114: 114,
 115: 115,
 116: 116,
 117: 117,
 118: 118,
 119: 119,
 120: 120,
 121: 121,
 122: 122,
 123: 123,
 124: 124,
 125: 125,
 126: 126,
 127: 127,
 160: 255,
 162: 150,
 163: 156,
 164: 159,
 166: 167,
 167: 245,
 169: 168,
 171: 174,
 172: 170,
 173: 240,
 174: 169,
 176: 248,
 177: 241,
 178: 253,
 179: 252,
 181: 230,
 182: 244,
 183: 250,
 185: 251,
 187: 175,
 188: 172,
 189: 171,
 190: 243,
 196: 142,
 197: 143,
 198: 146,
 201: 144,
 211: 224,
 213: 229,
 214: 153,
 215: 158,
 216: 157,
 220: 154,
 223: 225,
 228: 132,
 229: 134,
 230: 145,
 233: 130,
 243: 162,
 245: 228,
 246: 148,
 247: 246,
 248: 155,
 252: 129,
 256: 160,
 257: 131,
 260: 181,
 261: 208,
 262: 128,
 263: 135,
 268: 182,
 269: 209,
 274: 237,
 275: 137,
 278: 184,
 279: 211,
 280: 183,
 281: 210,
 290: 149,
 291: 133,
 298: 161,
 299: 140,
 302: 189,
 303: 212,
 310: 232,
 311: 233,
 315: 234,
 316: 235,
 321: 173,
 322: 136,
 323: 227,
 324: 231,
 325: 238,
 326: 236,
 332: 226,
 333: 147,
 342: 138,
 343: 139,
 346: 151,
 347: 152,
 352: 190,
 353: 213,
 362: 199,
 363: 215,
 370: 198,
 371: 214,
 377: 141,
 378: 165,
 379: 163,
 380: 164,
 381: 207,
 382: 216,
 8217: 239,
 8220: 242,
 8221: 166,
 8222: 247,
 8729: 249,
 9472: 196,
 9474: 179,
 9484: 218,
 9488: 191,
 9492: 192,
 9496: 217,
 9500: 195,
 9508: 180,
 9516: 194,
 9524: 193,
 9532: 197,
 9552: 205,
 9553: 186,
 9556: 201,
 9559: 187,
 9562: 200,
 9565: 188,
 9568: 204,
 9571: 185,
 9574: 203,
 9577: 202,
 9580: 206,
 9600: 223,
 9604: 220,
 9608: 219,
 9612: 221,
 9616: 222,
 9617: 176,
 9618: 177,
 9619: 178,
 9632: 254}
