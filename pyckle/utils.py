# various private helper functions for pyckle

# for a proper error reporting, one needs to print a line
# and line number - therefor string input is tokenizes
# in order to produce such information
def _split_lines(src):

    import tokenize
    from io import BytesIO
    
    lastline = 0

    ret = list()


    for toktype, tokstring, (srow, scol), (erow, ecol), line in tokenize.tokenize(BytesIO(src.encode('utf-8')).readline):

        if srow != erow:
            raise SyntaxError("srow({}) != erow({}), on line `{}'!, which is not supported".format(srow, erow, line))

        # ignore ENCODING(56) and ENDMARKER(0) tokens
        if toktype in (56, 0):
            continue

        if erow != lastline:
            ret.append(line)
            lastline = erow

    return ret
