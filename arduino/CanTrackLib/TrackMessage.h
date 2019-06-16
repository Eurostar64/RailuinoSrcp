
#include <Arduino.h>
#include <Printable.h>

#include <SPI.h>
#include "mcp_can.h"

class TrackMessage : public Printable {

  public:

  /**
   * The command number.
   */
  byte command;
  
  /**
   * The hash that is used for avoiding device/message collisions.
   */
  word hash;

  /**
   * Whether this is a response to a request.
   */
  boolean response;

  /**
   * The number of data bytes in the payload.
   */
  byte length;

  /**
   * The actual message data bytes.
   */
  byte data[8];

  /**
   * Clears the message, setting all values to zero. Provides for
   * easy recycling of TrackMessage objects.
   */
  void clear();

  /**
   * Prints the message to the given Print object, which could be a
   * Serial object, for instance. The message format looks like this
   *
   * HHHH R CC L DD DD DD DD DD DD DD DD
   *
   * with all numbers being hexadecimals and the data bytes being
   * optional beyond what the message length specifies. Exactly one
   * whitespace is inserted between different fields as a separator.
   */
  virtual size_t printTo(Print &p) const;

  /**
   * Parses the message from the given String. Returns true on
   * success, false otherwise. The message must have exactly the
   * format that printTo creates. This includes each and every
   * whitespace. If the parsing fails the state of the object is
   * undefined afterwards, and a clear() is recommended.
   */
  boolean parseFrom(String &s);

};


class TrackController {

    private:

    /**
     * Holds the CAN controller which implements all the CAN magic
     * provided by the MCP CAN library
     */
    MCP_CAN CAN;

	/**
	 * Stores the hash of our controller. This must not conflict with
	 * hashes of other devices in the setup (most likely the MS2 and
	 * the connector box).
	 */
	word mHash;

	/**
	 * Stores the debug flag. When debugging is on, all outgoing and
	 * incoming messages are printed to the Serial console.
	 */
	boolean mDebug;

	/**
	 * Generates a new hash and makes sure it does not conflict
	 * with those of other devices in the setup.
	 */
	void generateHash();

    public:

	/**
	 * Creates a new TrackController with default values. This should
	 * be fine for most use cases. Further configuration can be done
	 * by using the init() method.
	 */
    TrackController();


    /**
     * Set the debug flag
     */
    void setDebugging(boolean debug);

    /**
     * Queries the hash used by the TrackController.
     */
    word getHash();

    /**
     * Sends a message and reports true on success. Internal method.
     * Normally you don't want to use this, but the more convenient
     * methods below instead.
     */
    boolean sendMessage(TrackMessage &message);

    /**
     * Receives an arbitrary message, if available, and reports true
     * on success. Does not block. Internal method. Normally you
     * don't want to use this, but the more convenient methods below
     * instead.
     */
    boolean receiveMessage(TrackMessage &message);

    /**
     * Initializes the CAN hardware and starts receiving CAN
     * messages. CAN messages are put into an internal buffer of
     * limited size, so they don't get lost, but you have to take
     * care of them in time. Otherwise the buffer might overflow.
     */
    void begin();
};
