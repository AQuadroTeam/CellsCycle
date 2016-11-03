# Message identifiers
INT = 0
EXT = 1
MIN_RANDOM = 1000
MAX_RANDOM = 9999
NO_VERSION = ''
DIE = '666'

# Message indexes
SOURCE_FLAG_INDEX = 0
VERSION_INDEX = 1
PRIORITY_INDEX = 2
RANDOM_INDEX = 3
TARGET_ID_INDEX = 4
TARGET_ADDR_INDEX = 5
TARGET_KEY_INDEX = 6
TARGET_RELATIVE_INDEX = 7
SOURCE_ID_INDEX = 8
NUM_FIELDS = 9

# Priority
DEAD = '3'
RESTORED = '3'
ADDED = '2'
ADD = '1'
ALIVE = '0'

# List communication
DEFAULT_ADDR = '127.0.0.1'

# ACK/NACK
NOK = 'NOK'
OK = 'OK'

# Node Address
MEMORY_ADDR = '127.0.0.1:8080'

# Well Known Ports
INT_PORT = '5193'
EXT_PORT = '5194'

# Try a number of times, then stop sending message
TRIES = 3
TRY_TIMEOUT = 1

# Writer Timeout
WRITER_TIMEOUT = 0.001