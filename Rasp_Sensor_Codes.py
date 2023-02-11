"""
----------------------------------------------------------------------------------
This Python file contains programs for RaspberryPi Sensor Programs to Retrive data
----------------------------------------------------------------------------------
Project Name: Patient Monitoring using IOT
------------------------------------------
--------------TEAM MEMBERS----------------
SAMEER SHAIK            19KB1A1244
KOTA ARUN               19KB1A1222
N VISHNU TEJA REDDY     19KB1A1229
K DHEERAJ KRISHNA       19KB1A1223

"""
""""
  Library for the Maxim MAX30100 pulse oximetry system on Raspberry Pi

  Based on original C library for Arduino by Connor Huffine/Kontakt
  https: // github.com / kontakt / MAX30100

  September 2017
"""

import smbus

INT_STATUS   = 0x00  # Which interrupts are tripped
INT_ENABLE   = 0x01  # Which interrupts are active
FIFO_WR_PTR  = 0x02  # Where data is being written
OVRFLOW_CTR  = 0x03  # Number of lost samples
FIFO_RD_PTR  = 0x04  # Where to read from
FIFO_DATA    = 0x05  # Ouput data buffer
MODE_CONFIG  = 0x06  # Control register
SPO2_CONFIG  = 0x07  # Oximetry settings
LED_CONFIG   = 0x09  # Pulse width and power of LEDs
TEMP_INTG    = 0x16  # Temperature value, whole number
TEMP_FRAC    = 0x17  # Temperature value, fraction
REV_ID       = 0xFE  # Part revision
PART_ID      = 0xFF  # Part ID, normally 0x11

I2C_ADDRESS  = 0x57  # I2C address of the MAX30100 device


PULSE_WIDTH = {
    200: 0,
    400: 1,
    800: 2,
   1600: 3,
}

SAMPLE_RATE = {
    50: 0,
   100: 1,
   167: 2,
   200: 3,
   400: 4,
   600: 5,
   800: 6,
  1000: 7,
}

LED_CURRENT = {
       0: 0,
     4.4: 1,
     7.6: 2,
    11.0: 3,
    14.2: 4,
    17.4: 5,
    20.8: 6,
    24.0: 7,
    27.1: 8,
    30.6: 9,
    33.8: 10,
    37.0: 11,
    40.2: 12,
    43.6: 13,
    46.8: 14,
    50.0: 15
}

def _get_valid(d, value):
    try:
        return d[value]
    except KeyError:
        raise KeyError("Value %s not valid, use one of: %s" % (value, ', '.join([str(s) for s in d.keys()])))

def _twos_complement(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)
    return val

INTERRUPT_SPO2 = 0
INTERRUPT_HR = 1
INTERRUPT_TEMP = 2
INTERRUPT_FIFO = 3

MODE_HR = 0x02
MODE_SPO2 = 0x03


class MAX30100(object):

    def __init__(self,
                 i2c=None,
                 mode=MODE_HR,
                 sample_rate=100,
                 led_current_red=11.0,
                 led_current_ir=11.0,
                 pulse_width=1600,
                 max_buffer_len=10000
                 ):

        # Default to the standard I2C bus on Pi.
        self.i2c = i2c if i2c else smbus.SMBus(1)

        self.set_mode(MODE_HR)  # Trigger an initial temperature read.
        self.set_led_current(led_current_red, led_current_ir)
        self.set_spo_config(sample_rate, pulse_width)

        # Reflectance data (latest update)
        self.buffer_red = []
        self.buffer_ir = []

        self.max_buffer_len = max_buffer_len
        self._interrupt = None

    @property
    def red(self):
        return self.buffer_red[-1] if self.buffer_red else None

    @property
    def ir(self):
        return self.buffer_ir[-1] if self.buffer_ir else None

    def set_led_current(self, led_current_red=11.0, led_current_ir=11.0):
        # Validate the settings, convert to bit values.
        led_current_red = _get_valid(LED_CURRENT, led_current_red)
        led_current_ir = _get_valid(LED_CURRENT, led_current_ir)
        self.i2c.write_byte_data(I2C_ADDRESS, LED_CONFIG, (led_current_red << 4) | led_current_ir)

    def set_mode(self, mode):
        reg = self.i2c.read_byte_data(I2C_ADDRESS, MODE_CONFIG)
        self.i2c.write_byte_data(I2C_ADDRESS, MODE_CONFIG, reg & 0x74) # mask the SHDN bit
        self.i2c.write_byte_data(I2C_ADDRESS, MODE_CONFIG, reg | mode)

    def set_spo_config(self, sample_rate=100, pulse_width=1600):
        reg = self.i2c.read_byte_data(I2C_ADDRESS, SPO2_CONFIG)
        reg = reg & 0xFC  # Set LED pulsewidth to 00
        self.i2c.write_byte_data(I2C_ADDRESS, SPO2_CONFIG, reg | pulse_width)

    def enable_spo2(self):
        self.set_mode(MODE_SPO2)

    def disable_spo2(self):
        self.set_mode(MODE_HR)

    def enable_interrupt(self, interrupt_type):
        self.i2c.write_byte_data(I2C_ADDRESS, INT_ENABLE, (interrupt_type + 1)<<4)
        self.i2c.read_byte_data(I2C_ADDRESS, INT_STATUS)

    def get_number_of_samples(self):
        write_ptr = self.i2c.read_byte_data(I2C_ADDRESS, FIFO_WR_PTR)
        read_ptr = self.i2c.read_byte_data(I2C_ADDRESS, FIFO_RD_PTR)
        return abs(16+write_ptr - read_ptr) % 16

    def read_sensor(self):
        bytes = self.i2c.read_i2c_block_data(I2C_ADDRESS, FIFO_DATA, 4)
        # Add latest values.
        self.buffer_ir.append(bytes[0]<<8 | bytes[1])
        self.buffer_red.append(bytes[2]<<8 | bytes[3])
        # Crop our local FIFO buffer to length.
        self.buffer_red = self.buffer_red[-self.max_buffer_len:]
        self.buffer_ir = self.buffer_ir[-self.max_buffer_len:]

    def shutdown(self):
        reg = self.i2c.read_byte_data(I2C_ADDRESS, MODE_CONFIG)
        self.i2c.write_byte_data(I2C_ADDRESS, MODE_CONFIG, reg | 0x80)

    def reset(self):
        reg = self.i2c.read_byte_data(I2C_ADDRESS, MODE_CONFIG)
        self.i2c.write_byte_data(I2C_ADDRESS, MODE_CONFIG, reg | 0x40)

    def refresh_temperature(self):
        reg = self.i2c.read_byte_data(I2C_ADDRESS, MODE_CONFIG)
        self.i2c.write_byte_data(I2C_ADDRESS, MODE_CONFIG, reg | (1 << 3))

    def get_temperature(self):
        intg = _twos_complement(self.i2c.read_byte_data(I2C_ADDRESS, TEMP_INTG))
        frac = self.i2c.read_byte_data(I2C_ADDRESS, TEMP_FRAC)
        return intg + (frac * 0.0625)

    def get_rev_id(self):
        return self.i2c.read_byte_data(I2C_ADDRESS, REV_ID)

    def get_part_id(self):
        return self.i2c.read_byte_data(I2C_ADDRESS, PART_ID)

    def get_registers(self):
        return {
            "INT_STATUS": self.i2c.read_byte_data(I2C_ADDRESS, INT_STATUS),
            "INT_ENABLE": self.i2c.read_byte_data(I2C_ADDRESS, INT_ENABLE),
            "FIFO_WR_PTR": self.i2c.read_byte_data(I2C_ADDRESS, FIFO_WR_PTR),
            "OVRFLOW_CTR": self.i2c.read_byte_data(I2C_ADDRESS, OVRFLOW_CTR),
            "FIFO_RD_PTR": self.i2c.read_byte_data(I2C_ADDRESS, FIFO_RD_PTR),
            "FIFO_DATA": self.i2c.read_byte_data(I2C_ADDRESS, FIFO_DATA),
            "MODE_CONFIG": self.i2c.read_byte_data(I2C_ADDRESS, MODE_CONFIG),
            "SPO2_CONFIG": self.i2c.read_byte_data(I2C_ADDRESS, SPO2_CONFIG),
            "LED_CONFIG": self.i2c.read_byte_data(I2C_ADDRESS, LED_CONFIG),
            "TEMP_INTG": self.i2c.read_byte_data(I2C_ADDRESS, TEMP_INTG),
            "TEMP_FRAC": self.i2c.read_byte_data(I2C_ADDRESS, TEMP_FRAC),
            "REV_ID": self.i2c.read_byte_data(I2C_ADDRESS, REV_ID),
            "PART_ID": self.i2c.read_byte_data(I2C_ADDRESS, PART_ID),
        }


"""
This file holds HX711 class
"""
# !/usr/bin/env python3

import statistics as stat
import time

import RPi.GPIO as GPIO


class HX711:
    """
    HX711 represents chip for reading load cells.
    """

    def __init__(self,
                 dout_pin,
                 pd_sck_pin,
                 gain_channel_A=128,
                 select_channel='A'):
        """
        Init a new instance of HX711

        Args:
            dout_pin(int): Raspberry Pi pin number where the Data pin of HX711 is connected.
            pd_sck_pin(int): Raspberry Pi pin number where the Clock pin of HX711 is connected.
            gain_channel_A(int): Optional, by default value 128. Options (128 || 64)
            select_channel(str): Optional, by default 'A'. Options ('A' || 'B')

        Raises:
            TypeError: if pd_sck_pin or dout_pin are not int type
        """
        if (isinstance(dout_pin, int)):
            if (isinstance(pd_sck_pin, int)):
                self._pd_sck = pd_sck_pin
                self._dout = dout_pin
            else:
                raise TypeError('pd_sck_pin must be type int. '
                                'Received pd_sck_pin: {}'.format(pd_sck_pin))
        else:
            raise TypeError('dout_pin must be type int. '
                            'Received dout_pin: {}'.format(dout_pin))

        self._gain_channel_A = 0
        self._offset_A_128 = 0  # offset for channel A and gain 128
        self._offset_A_64 = 0  # offset for channel A and gain 64
        self._offset_B = 0  # offset for channel B
        self._last_raw_data_A_128 = 0
        self._last_raw_data_A_64 = 0
        self._last_raw_data_B = 0
        self._wanted_channel = ''
        self._current_channel = ''
        self._scale_ratio_A_128 = 1  # scale ratio for channel A and gain 128
        self._scale_ratio_A_64 = 1  # scale ratio for channel A and gain 64
        self._scale_ratio_B = 1  # scale ratio for channel B
        self._debug_mode = False
        self._data_filter = self.outliers_filter  # default it is used outliers_filter

        GPIO.setup(self._pd_sck, GPIO.OUT)  # pin _pd_sck is output only
        GPIO.setup(self._dout, GPIO.IN)  # pin _dout is input only
        self.select_channel(select_channel)
        self.set_gain_A(gain_channel_A)

    def select_channel(self, channel):
        """
        select_channel method evaluates if the desired channel
        is valid and then sets the _wanted_channel variable.

        Args:
            channel(str): the channel to select. Options ('A' || 'B')
        Raises:
            ValueError: if channel is not 'A' or 'B'
        """
        channel = channel.capitalize()
        if (channel == 'A'):
            self._wanted_channel = 'A'
        elif (channel == 'B'):
            self._wanted_channel = 'B'
        else:
            raise ValueError('Parameter "channel" has to be "A" or "B". '
                             'Received: {}'.format(channel))
        # after changing channel or gain it has to wait 50 ms to allow adjustment.
        # the data before is garbage and cannot be used.
        self._read()
        time.sleep(0.5)

    def set_gain_A(self, gain):
        """
        set_gain_A method sets gain for channel A.

        Args:
            gain(int): Gain for channel A (128 || 64)

        Raises:
            ValueError: if gain is different than 128 or 64
        """
        if gain == 128:
            self._gain_channel_A = gain
        elif gain == 64:
            self._gain_channel_A = gain
        else:
            raise ValueError('gain has to be 128 or 64. '
                             'Received: {}'.format(gain))
        # after changing channel or gain it has to wait 50 ms to allow adjustment.
        # the data before is garbage and cannot be used.
        self._read()
        time.sleep(0.5)

    def zero(self, readings=30):
        """
        zero is a method which sets the current data as
        an offset for particulart channel. It can be used for
        subtracting the weight of the packaging. Also known as tare.

        Args:
            readings(int): Number of readings for mean. Allowed values 1..99

        Raises:
            ValueError: if readings are not in range 1..99

        Returns: True if error occured.
        """
        if readings > 0 and readings < 100:
            result = self.get_raw_data_mean(readings)
            if result != False:
                if (self._current_channel == 'A' and
                        self._gain_channel_A == 128):
                    self._offset_A_128 = result
                    return False
                elif (self._current_channel == 'A' and
                      self._gain_channel_A == 64):
                    self._offset_A_64 = result
                    return False
                elif (self._current_channel == 'B'):
                    self._offset_B = result
                    return False
                else:
                    if self._debug_mode:
                        print('Cannot zero() channel and gain mismatch.\n'
                              'current channel: {}\n'
                              'gain A: {}\n'.format(self._current_channel,
                                                    self._gain_channel_A))
                    return True
            else:
                if self._debug_mode:
                    print('From method "zero()".\n'
                          'get_raw_data_mean(readings) returned False.\n')
                return True
        else:
            raise ValueError('Parameter "readings" '
                             'can be in range 1 up to 99. '
                             'Received: {}'.format(readings))

    def set_offset(self, offset, channel='', gain_A=0):
        """
        set offset method sets desired offset for specific
        channel and gain. Optional, by default it sets offset for current
        channel and gain.

        Args:
            offset(int): specific offset for channel
            channel(str): Optional, by default it is the current channel.
                Or use these options ('A' || 'B')

        Raises:
            ValueError: if channel is not ('A' || 'B' || '')
            TypeError: if offset is not int type
        """
        channel = channel.capitalize()
        if isinstance(offset, int):
            if channel == 'A' and gain_A == 128:
                self._offset_A_128 = offset
                return
            elif channel == 'A' and gain_A == 64:
                self._offset_A_64 = offset
                return
            elif channel == 'B':
                self._offset_B = offset
                return
            elif channel == '':
                if self._current_channel == 'A' and self._gain_channel_A == 128:
                    self._offset_A_128 = offset
                    return
                elif self._current_channel == 'A' and self._gain_channel_A == 64:
                    self._offset_A_64 = offset
                    return
                else:
                    self._offset_B = offset
                    return
            else:
                raise ValueError('Parameter "channel" has to be "A" or "B". '
                                 'Received: {}'.format(channel))
        else:
            raise TypeError('Parameter "offset" has to be integer. '
                            'Received: '+str(offset)+'\n')

    def set_scale_ratio(self, scale_ratio, channel='', gain_A=0):
        """
        set_scale_ratio method sets the ratio for calculating
        weight in desired units. In order to find this ratio for
        example to grams or kg. You must have known weight.

        Args:
            scale_ratio(float): number > 0.0 that is used for
                conversion to weight units
            channel(str): Optional, by default it is the current channel.
                Or use these options ('a'|| 'A' || 'b' || 'B')
            gain_A(int): Optional, by default it is the current channel.
                Or use these options (128 || 64)
        Raises:
            ValueError: if channel is not ('A' || 'B' || '')
            TypeError: if offset is not int type
        """
        channel = channel.capitalize()
        if isinstance(gain_A, int):
            if channel == 'A' and gain_A == 128:
                self._scale_ratio_A_128 = scale_ratio
                return
            elif channel == 'A' and gain_A == 64:
                self._scale_ratio_A_64 = scale_ratio
                return
            elif channel == 'B':
                self._scale_ratio_B = scale_ratio
                return
            elif channel == '':
                if self._current_channel == 'A' and self._gain_channel_A == 128:
                    self._scale_ratio_A_128 = scale_ratio
                    return
                elif self._current_channel == 'A' and self._gain_channel_A == 64:
                    self._scale_ratio_A_64 = scale_ratio
                    return
                else:
                    self._scale_ratio_B = scale_ratio
                    return
            else:
                raise ValueError('Parameter "channel" has to be "A" or "B". '
                                 'received: {}'.format(channel))
        else:
            raise TypeError('Parameter "gain_A" has to be integer. '
                            'Received: '+str(gain_A)+'\n')

    def set_data_filter(self, data_filter):
        """
        set_data_filter method sets data filter that is passed as an argument.

        Args:
            data_filter(data_filter): Data filter that takes list of int numbers and
                returns a list of filtered int numbers.

        Raises:
            TypeError: if filter is not a function.
        """
        if callable(data_filter):
            self._data_filter = data_filter
        else:
            raise TypeError('Parameter "data_filter" must be a function. '
                            'Received: {}'.format(data_filter))

    def set_debug_mode(self, flag=False):
        """
        set_debug_mode method is for turning on and off
        debug mode.

        Args:
            flag(bool): True turns on the debug mode. False turns it off.

        Raises:
            ValueError: if fag is not bool type
        """
        if flag == False:
            self._debug_mode = False
            print('Debug mode DISABLED')
            return
        elif flag == True:
            self._debug_mode = True
            print('Debug mode ENABLED')
            return
        else:
            raise ValueError('Parameter "flag" can be only BOOL value. '
                             'Received: {}'.format(flag))

    def _save_last_raw_data(self, channel, gain_A, data):
        """
        _save_last_raw_data saves the last raw data for specific channel and gain.

        Args:
            channel(str):
            gain_A(int):
            data(int):
        Returns: False if error occured
        """
        if channel == 'A' and gain_A == 128:
            self._last_raw_data_A_128 = data
        elif channel == 'A' and gain_A == 64:
            self._last_raw_data_A_64 = data
        elif channel == 'B':
            self._last_raw_data_B = data
        else:
            return False

    def _ready(self):
        """
        _ready method check if data is prepared for reading from HX711

        Returns: bool True if ready else False when not ready
        """
        # if DOUT pin is low data is ready for reading
        if GPIO.input(self._dout) == 0:
            return True
        else:
            return False

    def _set_channel_gain(self, num):
        """
        _set_channel_gain is called only from _read method.
        It finishes the data transmission for HX711 which sets
        the next required gain and channel.

        Args:
            num(int): how many ones it sends to HX711
                options (1 || 2 || 3)

        Returns: bool True if HX711 is ready for the next reading
            False if HX711 is not ready for the next reading
        """
        for _ in range(num):
            start_counter = time.perf_counter()
            GPIO.output(self._pd_sck, True)
            GPIO.output(self._pd_sck, False)
            end_counter = time.perf_counter()
            # check if hx 711 did not turn off...
            if end_counter-start_counter >= 0.00006:
                # if pd_sck pin is HIGH for 60 us and more than the HX 711 enters power down mode.
                if self._debug_mode:
                    print('Not enough fast while setting gain and channel')
                    print(
                        'Time elapsed: {}'.format(end_counter-start_counter))
                # hx711 has turned off. First few readings are inaccurate.
                # Despite it, this reading was ok and data can be used.
                result = self.get_raw_data_mean(6)  # set for the next reading.
                if result == False:
                    return False
        return True

    def _read(self):
        """
        _read method reads bits from hx711, converts to INT
        and validate the data.

        Returns: (bool || int) if it returns False then it is false reading.
            if it returns int then the reading was correct
        """
        GPIO.output(self._pd_sck, False)  # start by setting the pd_sck to 0
        ready_counter = 0
        while (not self._ready() and ready_counter <= 40):
            time.sleep(0.01)  # sleep for 10 ms because data is not ready
            ready_counter += 1
            if ready_counter == 50:  # if counter reached max value then return False
                if self._debug_mode:
                    print('self._read() not ready after 40 trials\n')
                return False

        # read first 24 bits of data
        data_in = 0  # 2's complement data from hx 711
        for _ in range(24):
            start_counter = time.perf_counter()
            # request next bit from hx 711
            GPIO.output(self._pd_sck, True)
            GPIO.output(self._pd_sck, False)
            end_counter = time.perf_counter()
            if end_counter-start_counter >= 0.00006:  # check if the hx 711 did not turn off...
                # if pd_sck pin is HIGH for 60 us and more than the HX 711 enters power down mode.
                if self._debug_mode:
                    print('Not enough fast while reading data')
                    print(
                        'Time elapsed: {}'.format(end_counter-start_counter))
                return False
            # Shift the bits as they come to data_in variable.
            # Left shift by one bit then bitwise OR with the new bit.
            data_in = (data_in << 1) | GPIO.input(self._dout)

        if self._wanted_channel == 'A' and self._gain_channel_A == 128:
            if not self._set_channel_gain(1):  # send only one bit which is 1
                return False  # return False because channel was not set properly
            else:
                self._current_channel = 'A'  # else set current channel variable
                self._gain_channel_A = 128  # and gain
        elif self._wanted_channel == 'A' and self._gain_channel_A == 64:
            if not self._set_channel_gain(3):  # send three ones
                return False  # return False because channel was not set properly
            else:
                self._current_channel = 'A'  # else set current channel variable
                self._gain_channel_A = 64
        else:
            if not self._set_channel_gain(2):  # send two ones
                return False  # return False because channel was not set properly
            else:
                self._current_channel = 'B'  # else set current channel variable

        if self._debug_mode:  # print 2's complement value
            print('Binary value as received: {}'.format(bin(data_in)))

        # check if data is valid
        if (data_in == 0x7fffff
                or  # 0x7fffff is the highest possible value from hx711
                data_in == 0x800000
        ):  # 0x800000 is the lowest possible value from hx711
            if self._debug_mode:
                print('Invalid data detected: {}\n'.format(data_in))
            return False  # rturn false because the data is invalid

        # calculate int from 2's complement
        signed_data = 0
        # 0b1000 0000 0000 0000 0000 0000 check if the sign bit is 1. Negative number.
        if (data_in & 0x800000):
            signed_data = -(
                    (data_in ^ 0xffffff)+1)  # convert from 2's complement to int
        else:  # else do not do anything the value is positive number
            signed_data = data_in

        if self._debug_mode:
            print('Converted 2\'s complement value: {}'.format(signed_data))

        return signed_data

    def get_raw_data_mean(self, readings=30):
        """
        get_raw_data_mean returns mean value of readings.

        Args:
            readings(int): Number of readings for mean.

        Returns: (bool || int) if False then reading is invalid.
            if it returns int then reading is valid
        """
        # do backup of current channel befor reading for later use
        backup_channel = self._current_channel
        backup_gain = self._gain_channel_A
        data_list = [ ]
        # do required number of readings
        for _ in range(readings):
            data_list.append(self._read())
        data_mean = False
        if readings > 2 and self._data_filter:
            filtered_data = self._data_filter(data_list)
            if not filtered_data:
                return False
            if self._debug_mode:
                print('data_list: {}'.format(data_list))
                print('filtered_data list: {}'.format(filtered_data))
                print('data_mean:', stat.mean(filtered_data))
            data_mean = stat.mean(filtered_data)
        else:
            data_mean = stat.mean(data_list)
        self._save_last_raw_data(backup_channel, backup_gain, data_mean)
        return int(data_mean)

    def get_data_mean(self, readings=30):
        """
        get_data_mean returns average value of readings minus
        offset for the channel which was read.

        Args:
            readings(int): Number of readings for mean

        Returns: (bool || int) False if reading was not ok.
            If it returns int then reading was ok
        """
        result = self.get_raw_data_mean(readings)
        if result != False:
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                return result-self._offset_A_128
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                return result-self._offset_A_64
            else:
                return result-self._offset_B
        else:
            return False

    def get_weight_mean(self, readings=30):
        """
        get_weight_mean returns average value of readings minus
        offset divided by scale ratio for a specific channel
        and gain.

        Args:
            readings(int): Number of readings for mean

        Returns: (bool || float) False if reading was not ok.
            If it returns float then reading was ok
        """
        result = self.get_raw_data_mean(readings)
        if result != False:
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                return float(
                    (result-self._offset_A_128) / self._scale_ratio_A_128)
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                return float(
                    (result-self._offset_A_64) / self._scale_ratio_A_64)
            else:
                return float((result-self._offset_B) / self._scale_ratio_B)
        else:
            return False

    def get_current_channel(self):
        """
        get current channel returns the value of current channel.

        Returns: ('A' || 'B')
        """
        return self._current_channel

    def get_data_filter(self):
        """
        get data filter.

        Returns: self._data_filter
        """
        return self._data_filter

    def get_current_gain_A(self):
        """
        get current gain A returns the value of current gain on channel A

        Returns: (128 || 64) current gain on channel A
        """
        return self._gain_channel_A

    def get_last_raw_data(self, channel='', gain_A=0):
        """
        get last raw data returns the last read data for a
        channel and gain. By default for current one.

        Args:
            channel(str): select channel ('A' || 'B'). If not then it returns the current one.
            gain_A(int): select gain (128 || 64). If not then it returns the current one.

        Raises:
            ValueError: if channel is not ('A' || 'B' || '') or gain_A is not (128 || 64 || 0)
                '' and 0 is default value.

        Returns: int the last data that was received for the chosen channel and gain
        """
        channel = channel.capitalize()
        if channel == 'A' and gain_A == 128:
            return self._last_raw_data_A_128
        elif channel == 'A' and gain_A == 64:
            return self._last_raw_data_A_64
        elif channel == 'B':
            return self._last_raw_data_B
        elif channel == '':
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                return self._last_raw_data_A_128
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                return self._last_raw_data_A_64
            else:
                return self._last_raw_data_B
        else:
            raise ValueError(
                'Parameter "channel" has to be "A" or "B". '
                'Received: {} \nParameter "gain_A" has to be 128 or 64. Received {}'
                    .format(channel, gain_A))

    def get_current_offset(self, channel='', gain_A=0):
        """
        get current offset returns the current offset for
        a particular channel and gain. By default the current one.

        Args:
            channel(str): select for which channel ('A' || 'B')
            gain_A(int): select for which gain (128 || 64)

        Raises:
            ValueError: if channel is not ('A' || 'B' || '') or gain_A is not (128 || 64 || 0)
                '' and 0 is default value.

        Returns: int the offset for the chosen channel and gain
        """
        channel = channel.capitalize()
        if channel == 'A' and gain_A == 128:
            return self._offset_A_128
        elif channel == 'A' and gain_A == 64:
            return self._offset_A_64
        elif channel == 'B':
            return self._offset_B
        elif channel == '':
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                return self._offset_A_128
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                return self._offset_A_64
            else:
                return self._offset_B
        else:
            raise ValueError(
                'Parameter "channel" has to be "A" or "B". '
                'Received: {} \nParameter "gain_A" has to be 128 or 64. Received {}'
                    .format(channel, gain_A))

    def get_current_scale_ratio(self, channel='', gain_A=0):
        """
        get current scale ratio returns the current scale ratio
        for a particular channel and gain. By default
        the current one.

        Args:
            channel(str): select for which channel ('A' || 'B')
            gain_A(int): select for which gain (128 || 64)

        Returns: int the scale ratio for the chosen channel and gain
        """
        channel = channel.capitalize()
        if channel == 'A' and gain_A == 128:
            return self._scale_ratio_A_128
        elif channel == 'A' and gain_A == 64:
            return self._scale_ratio_A_64
        elif channel == 'B':
            return self._scale_ratio_B
        elif channel == '':
            if self._current_channel == 'A' and self._gain_channel_A == 128:
                return self._scale_ratio_A_128
            elif self._current_channel == 'A' and self._gain_channel_A == 64:
                return self._scale_ratio_A_64
            else:
                return self._scale_ratio_B
        else:
            raise ValueError(
                'Parameter "channel" has to be "A" or "B". '
                'Received: {} \nParameter "gain_A" has to be 128 or 64. Received {}'
                    .format(channel, gain_A))

    def power_down(self):
        """
        power down method turns off the hx711.
        """
        GPIO.output(self._pd_sck, False)
        GPIO.output(self._pd_sck, True)
        time.sleep(0.01)

    def power_up(self):
        """
        power up function turns on the hx711.
        """
        GPIO.output(self._pd_sck, False)
        time.sleep(0.01)

    def reset(self):
        """
        reset method resets the hx711 and prepare it for the next reading.

        Returns: True if error encountered
        """
        self.power_down()
        self.power_up()
        result = self.get_raw_data_mean(6)
        if result:
            return False
        else:
            return True

    def outliers_filter(self, data_list, stdev_thresh=1.0):
        """
        It filters out outliers from the provided list of int.
        Median is used as an estimator of outliers.
        Outliers are compared to the standard deviation from the median
        Default filter is of 1.0 standard deviation from the median

        Args:
            data_list([int]): List of int. It can contain Bool False that is removed.

        Returns: list of filtered data. Excluding outliers.
        """
        # filter out -1 which indicates no signal
        # filter out booleans
        data = [ num for num in data_list if (num != -1 and num != False and num != True) ]
        if not data:
            return [ ]

        median = stat.median(data)
        dists_from_median = [ (abs(measurement-median)) for measurement in data ]
        stdev = stat.stdev(dists_from_median)
        if stdev:
            ratios_to_stdev = [ (dist / stdev) for dist in dists_from_median ]
        else:
            # stdev is 0. Therefore return just the median
            return [ median ]
        filtered_data = [ ]
        for i in range(len(data)):
            if ratios_to_stdev [ i ] < stdev_thresh:
                filtered_data.append(data [ i ])
        return filtered_data

    import time
    import RPi.GPIO as GPIO
    import max30100

    # Set up the MAX30100 sensor
    sensor = max30100.MAX30100()
    sensor.begin()

    # Set up the Raspberry Pi GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)

    # Continuously read data from the sensor and print it
    while True:
        red, ir = sensor.read_sensor()
        print("Red: ", red, "IR: ", ir)
        time.sleep(0.2)


import RPi.GPIO as GPIO
import time


class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck
        self.DOUT = dout

        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0
        self.REFERENCE_UNIT = 1  # The value returned by the hx711 that corresponds to your reference unit AFTER dividing by the SCALE.

        self.OFFSET = 1
        self.lastVal = long(0)

        self.LSByte = [ 2, -1, -1 ]
        self.MSByte = [ 0, 3, 1 ]

        self.MSBit = [ 0, 8, 1 ]
        self.LSBit = [ 7, -1, -1 ]

        self.byte_range_values = self.LSByte
        self.bit_range_values = self.LSBit

        self.set_gain(gain)

    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        self.read()

    def read(self):
        while not self.is_ready():
            # print("WAITING")
            pass

        data = self.read_byte()
        data = (data << 8) | self.read_byte()
        data = data >> self.bit_range_values [ self.GAIN ]
        return data

    def read_byte(self):
        bytes = [ 0, 0, 0 ]
        for i in range(self.byte_range_values [ self.GAIN ]):
            GPIO.output(self.PD_SCK, True)
            bytes [ i ] = GPIO.input(self.DOUT)
            GPIO.output(self.PD_SCK, False)
        return self.twos_complement(bytes)

    def twos_complement(self, bytes):
        value = 0
        for i in range(len(bytes)):
            value = (value << 1) | bytes [ i ]
        if (value & (1 << (len(bytes))-1)):
            value -= (1 << len(bytes))
        return value

    def get_binary_string(self, number):
        return format(number, 'b').zfill(8)


if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)

        hx = HX711(dout=21, pd_sck=20, gain=128)

        while True:
            val = hx.read()
            print(val)
            time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit)

        import smbus
        import time

        # ADXL345 constants
        EARTH_GRAVITY_MS2 = 9.80665
        SCALE_MULTIPLIER = 0.004

        DATA_FORMAT = 0x31
        BW_RATE = 0x2C
        POWER_CTL = 0x2D

        BW_RATE_1600HZ = 0x0F
        BW_RATE_800HZ = 0x0E
        BW_RATE_400HZ = 0x0D
        BW_RATE_200HZ = 0x0C
        BW_RATE_100HZ = 0x0B
        BW_RATE_50HZ = 0x0A
        BW_RATE_25HZ = 0x09

        RANGE_2G = 0x00
        RANGE_4G = 0x01
        RANGE_8G = 0x02
        RANGE_16G = 0x03

        MEASURE = 0x08
        AXES_DATA = 0x32


        class ADXL345:

            address = None

            def __init__(self, address=0x53):
                self.address = address
                self.bus = smbus.SMBus(1)
                self.bus.write_byte_data(self.address, POWER_CTL, MEASURE)
                self.bus.write_byte_data(self.address, DATA_FORMAT, RANGE_2G)
                self.bus.write_byte_data(self.address, BW_RATE, BW_RATE_100HZ)

            def getAxes(self):
                bytes = self.bus.read_i2c_block_data(self.address, AXES_DATA, 6)

                x = bytes [ 0 ] | (bytes [ 1 ] << 8)
                if (x & (1 << 16-1)):
                    x = x-(1 << 16)

                y = bytes [ 2 ] | (bytes [ 3 ] << 8)
                if (y & (1 << 16-1)):
                    y = y-(1 << 16)

                z = bytes [ 4 ] | (bytes [ 5 ] << 8)
                if (z & (1 << 16-1)):
                    z = z-(1 << 16)

                x = x * SCALE_MULTIPLIER
                y = y * SCALE_MULTIPLIER
                z = z * SCALE_MULTIPLIER

                return {"x": x, "y": y, "z": z}

import RPi.GPIO as GPIO
import time

# Set the GPIO pin numbers for the HX711 clock and data pins
CLK = 21
DAT = 20

# Set the reference unit for the HX711 sensor
referenceUnit = -1

def setupHX711():
    # Set the GPIO pin numbering mode
    GPIO.setmode(GPIO.BCM)
    # Set the clock and data pins as input
    GPIO.setup(CLK, GPIO.IN)
    GPIO.setup(DAT, GPIO.IN)
    # Wait for the HX711 to settle
    time.sleep(0.1)

def readHX711():
    # Pulse the clock pin 24 times to read the data
    data = 0
    for i in range(24):
        GPIO.output(CLK, True)
        data = data << 1
        GPIO.output(CLK, False)
        if(GPIO.input(DAT)):
            data += 1
    # Pulse the clock pin to read the parity bit
    GPIO.output(CLK, True)
    GPIO.output(CLK, False)
    # Check the parity bit and return the data
    if(GPIO.input(DAT)):
        data = data | 0x800000
    return data

def getWeight(referenceUnit):
    # Set the clock pin low
    GPIO.output(CLK, False)
    # Read the data from the HX711 and return the weight in grams
    data = readHX711()
    weight = (data - referenceUnit) / -1000.0
    return weight

# Set up the HX711 sensor
setupHX711()
# Set the reference unit for the sensor
referenceUnit = readHX711()
# Continuously read and print the weight in grams
while True:
    weight = getWeight(referenceUnit)
    print("Weight: {:.3f} g".format(weight))
    time.sleep(0.5)

import smbus
import time

# Create an instance of the I2C bus
bus = smbus.SMBus(1)

# MAX30100 address
MAX30100_ADDRESS = 0x57

# Register addresses
REG_INT_STATUS = 0x00
REG_INT_ENABLE = 0x02
REG_FIFO_WRITE = 0x04
REG_FIFO_READ = 0x06
REG_FIFO_DATA = 0x07
REG_FIFO_CONFIG = 0x08
REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED_CONFIG = 0x0C

# Function to read data from a register
def read_register(address):
    return bus.read_byte_data(MAX30100_ADDRESS, address)

# Function to write data to a register
def write_register(address, data):
    bus.write_byte_data(MAX30100_ADDRESS, address, data)

# Configure the sensor
write_register(REG_INT_ENABLE, 0x00)
write_register(REG_FIFO_CONFIG, 0x0F)
write_register(REG_MODE_CONFIG, 0x03)
write_register(REG_SPO2_CONFIG, 0x27)
write_register(REG_LED_CONFIG, 0x24)

while True:
    # Read the data from the FIFO
    fifo_data = read_register(REG_FIFO_DATA)
    print("FIFO data: ", fifo_data)
    time.sleep(1)

