class OneZeroHeader(object):
    """
    1.0版本
    """

    def __init__():
        pass

    def read_header(f):
        pass


class OneOneHeader(object):
    """
    1.1版本
    """

    def __init__():
        pass

    def read_header(f):
        pass


class OneTwoHeader(object):
    """
    1.2版本
    """

    def __init__():
        pass

    def read_header(f):
        pass


class OneThreeHeader(object):
    """
    1.3版本
    """

    def __init__():
        pass

    def read_header(f):
        pass


class OneFourHeader(object):
    """
    1.4版本
    """

    def __init__():
        pass

    def read_header(f):
        pass


def get_header(f, version):
    """
    根据不同版本读取不同头
    """
    if version == (1, 0):
        new_header = OneZeroHeader()
    elif version == (1, 1):
        new_header = OneOneHeader()
    elif version == (1, 2):
        new_header = OneTwoHeader()
    elif version == (1, 3):
        new_header = OneThreeHeader()
    elif version == (1, 4):
        new_header = OneFourHeader()
    else:
        raise Exception("未找到对应文件版本")

    new_header.read_header(f)
    return new_header
