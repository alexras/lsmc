def instr_attr(attr):
    def instr_attr_format_fn(instr):
        return getattr(instr, attr)

    return instr_attr_format_fn

def one_digit_hex_format(attr):
    def one_digit_hex_format_fn(instr):
        return "%x" % (getattr(instr, attr))

    return one_digit_hex_format_fn

def two_digit_hex_format(attr):
    def two_digit_hex_format_fn(instr):
        return "%02x" % (getattr(instr, attr))

    return two_digit_hex_format_fn

def within(attr, function):
    def within_fn(obj):
        obj = getattr(obj, attr)
        return function(obj)

    return within_fn

def len_format(instr):
    if instr.has_sound_length:
        return "%02x" % (instr.sound_length)
    else:
        return "UNLIM"

def automate_format(instr):
    if instr.automate_1:
        return "ON"
    else:
        return "OFF"

def table_format(instr):
    if instr.table is None:
        return "OFF"
    else:
        return "%02x" % (instr.table.index)
