""" molecular geometry and structure readers
"""

import numbers
import autoread as ar
import autoparse.pattern as app
import autoparse.find as apf
import automol


def opt_geometry(output_string):
    """ get optimized geometry from output
    """
    syms, xyzs = ar.geom.read(
        output_string,
        start_ptt=app.padded(app.NEWLINE).join([
            app.escape('Coordinates (in bohr)'),
            app.LINE, app.LINE, '']),
        line_sep_ptt=app.UNSIGNED_INTEGER,)
    geo = automol.geom.from_data(syms, xyzs, angstrom=False)

    return geo


def opt_zmatrix(output_string):
    """ get optimized z-matrix geometry from output
    """

    # complicated string patterns for the initial matrix read
    mat_ptt = app.padded(app.NEWLINE).join([
        app.LINESPACES.join([app.escape('Input from ZMAT file'),
                             app.escape('*')]),
        app.LINE, app.LINE, ''])

    nam_ptt = (app.LETTER +
               app.one_or_more(
                   app.one_of_these([app.LETTER, app.UNDERSCORE, app.DIGIT])) +
               app.maybe(app.escape('*')))

    # read the matrix from the beginning of the output
    syms, key_mat, name_mat = ar.zmatrix.matrix.read(
        output_string,
        start_ptt=mat_ptt,
        sym_ptt=ar.par.Pattern.ATOM_SYMBOL + app.maybe(app.UNSIGNED_INTEGER),
        key_ptt=app.one_of_these([app.UNSIGNED_INTEGER, app.VARIABLE_NAME]),
        name_ptt=nam_ptt,
        last=False)

    # Remove any asterisks(*) from the entries in the name matrix
    name_mat = tuple([[name.replace('*', '')
                       if name is not None else None for name in name_row]
                      for name_row in name_mat])

    # complicated string patterns for the value dictionary read
    start_ptt = app.padded(app.NEWLINE).join(
        [app.padded('Final ZMATnew file', app.NONNEWLINE)] +
        [app.LINE for i in range(len(syms)+3)] + [''])

    # read the values from the end of the output
    if len(syms) == 1:
        val_dct = {}
    else:
        val_dct = ar.zmatrix.setval.read(
            output_string,
            start_ptt=start_ptt,
            entry_sep_ptt='=',
            last=True)

    # for the case when variable names are used instead of integer keys:
    # (otherwise, does nothing)
    key_dct = dict(map(reversed, enumerate(syms)))
    key_dct[None] = 0
    key_mat = [[key_dct[val]+1 if not isinstance(val, numbers.Real) else val
                for val in row] for row in key_mat]
    sym_ptt = app.STRING_START + app.capturing(ar.par.Pattern.ATOM_SYMBOL)
    syms = [apf.first_capture(sym_ptt, sym) for sym in syms]

    # call the automol constructor
    zma = automol.zmatrix.from_data(
        syms, key_mat, name_mat, val_dct,
        one_indexed=True, angstrom=True, degree=True)

    return zma
