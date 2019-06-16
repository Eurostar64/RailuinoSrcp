
#include "TrackMessage.h"
#include "mcp_can.h"

size_t printHex(Print &p, unsigned long hex, int digits) {
    size_t size = 0;

    String s = String(hex, HEX);

    for (int i = s.length(); i < digits; i++) {
        size += p.print("0");
    }

    size += p.print(s);

    return size;
}

int parseHex(String &s, int start, int end, boolean *ok) {
    int value = 0;

    for (int i = start; i < end; i++) {
    	char c = s.charAt(i);

        if (c >= '0' && c <= '9') {
            value = 16 * value + c - '0';
        } else if (c >= 'a' && c <= 'f') {
            value = 16 * value + 10 + c - 'a';
        } else if (c >= 'A' && c <= 'F') {
            value = 16 * value + 10 + c - 'A';
        } else {
        	ok = false;
            return -1;
        }
    }

    return value;
}


void TrackMessage::clear() {
	command = 0;
	hash = 0;
	response = false;
	length = 0;
	for (int i = 0; i < 8; i++) {
		data[i] = 0;
	}
}

size_t TrackMessage::printTo(Print& p) const {
    size_t size = 0;

    size += printHex(p, hash, 4);
    size += p.print(response ? " R " : "   ");
    size += printHex(p, command, 2);
    size += p.print(" ");
    size += printHex(p, length, 1);

    for (int i = 0; i < length; i++) {
        size += p.print(" ");
        size += printHex(p, data[i], 2);
    }

    return size;
}

boolean TrackMessage::parseFrom(String &s) {
	boolean result = true;

	clear();

	if (s.length() < 11) {
		return false;
	}

	hash = parseHex(s, 0, 4, &result);
	response = s.charAt(5) != ' ';
	command = parseHex(s, 7, 9, &result);
	length = parseHex(s, 10, 11, &result);

	if (length > 8) {
		return false;
	}

	if (s.length() < 11 + 3 * length) {
		return false;
	}

	for (int i = 0; i < length; i++) {
		data[i] = parseHex(s, 12 + 3 * i, 12 + 3 * i + 2, &result);
	}

	return result;
}

// TRACK Controller

// the cs pin of the version after v1.1 is default to D9
// v0.9b and v1.0 is default D10
TrackController::TrackController() : CAN(9) {
	mHash = 0;
	mDebug = false;
}

void TrackController::setDebugging(boolean debug) {
	mDebug = debug;
}

word TrackController::getHash() {
	return mHash;
}

void TrackController::begin() {

	while (CAN_OK != CAN.begin(CAN_250KBPS))              // init can bus : baudrate = 250k
    {
        Serial.println("### CAN BUS Shield init fail");
        Serial.println("### Init CAN BUS Shield again");
        delay(100);
    }
    Serial.println("### CAN BUS Shield init ok!");

    // TrackMessage message;

    // message.clear();
    // message.command = 0x1b;
    // message.length = 0x05;
    // message.data[4] = 0x11;

    // sendMessage(message);

	if (mHash == 0) {
		generateHash();
	}
	
	Serial.println("### Startup complete");
}

void TrackController::generateHash() {
	TrackMessage message;

	boolean ok = false;

	while(!ok) {
		mHash = random(0x10000) & 0xff7f | 0x0300;

		if (mDebug) {
			Serial.print(F("### Trying new hash "));
			printHex(Serial, mHash, 4);
			Serial.println();
		}

		message.clear();
		message.command = 0x18;

		sendMessage(message);

		delay(500);

		ok = true;
		while(receiveMessage(message)) {
			if (message.hash == mHash) {
				ok = false;
			}
		}
	}

	if (mDebug) {
        Serial.println(F("### New hash looks good"));
	}
}


boolean TrackController::sendMessage(TrackMessage &message) {
	
	unsigned char len = 0;
	unsigned char stmp[8] = {0, 0, 0, 0, 0, 0, 0, 0};

	message.hash = mHash;
    
    unsigned long canId = ((uint32_t)message.command) << 17 | (uint32_t)message.hash;

    len = message.length;
    for (int i = 0; i < message.length; i++) {
        stmp[i] = message.data[i];
    }

    if (mDebug) {
	    Serial.print("==> ");
	    Serial.println(message);
	}

    return CAN.sendMsgBuf(canId, 1, 0, 8, stmp, true);
}

boolean TrackController::receiveMessage(TrackMessage &message) {


    unsigned char len = 0;
    unsigned char buf[8];

    if(CAN_MSGAVAIL == CAN.checkReceive())            // check if data coming
    {
        CAN.readMsgBuf(&len, buf);    // read data,  len: data length, buf: data buf

        unsigned long canId = CAN.getCanId();

        message.clear();
        message.command = (canId >> 17) & 0xff;
        message.hash = canId & 0xffff;
        message.response = bitRead(canId, 16) || (false);
        message.length = len;

        for (int i = 0; i < len; i++) {
            message.data[i] = buf[i];
        }

        if (mDebug) {
                Serial.print("<== ");
                Serial.println(message);
        }

        return true;
    }
    else
    {
        return false;
    }

}
