from chemkin_io.writer.mechanism import elements_block as writer

ELEM_TUPLE = ('C', 'H', 'O', 'N')
ELEM_STR = 'ELEMENTS \n\nC\nH\nO\nN\n\nEND \n\n\n' 

def test__elements_write():
    """ Tests the elements writer
    """
    elem_str = writer(ELEM_TUPLE)
    assert elem_str == ELEM_STR

if __name__ == '__main__':
    test__elements_write() 

