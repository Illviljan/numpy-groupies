"""Common functionality for all aggregate implementations."""

import platform
import numpy as np

aggregate_common_doc = """
    See readme file at https://github.com/ml31415/numpy-groupies for a full
    description.  Below we reproduce the "Full description of inputs"
    section from that readme, note that the text below makes references to
    other portions of the readme that are not shown here.

    group_idx:
        this is an array of non-negative integers, to be used as the "labels"
        with which to group the values in ``a``. Although we have so far
        assumed that ``group_idx`` is one-dimensional, and the same length as
        ``a``, it can in fact be two-dimensional (or some form of nested
        sequences that can be converted to 2D).  When ``group_idx`` is 2D, the
        size of the 0th dimension corresponds to the number of dimensions in
        the output, i.e. ``group_idx[i,j]`` gives the index into the ith
        dimension in the output
        for ``a[j]``.  Note that ``a`` should still be 1D (or scalar), with
        length matching ``group_idx.shape[1]``.
    a:
        this is the array of values to be aggregated.  See above for a
        simple demonstration of what this means.  ``a`` will normally be a
        one-dimensional array, however it can also be a scalar in some cases.
    func: default='sum'
        the function to use for aggregation.  See the section above for
        details. Note that the simplest way to specify the function is using a
        string (e.g. ``func='max'``) however a number of aliases are also
        defined (e.g. you can use the ``func=np.max``, or even ``func=max``,
        where ``max`` is the
        builtin function).  To check the available aliases see ``utils.py``.
    size: default=None
        the shape of the output array. If ``None``, the maximum value in
        ``group_idx`` will set the size of the output.  Note that for
        multidimensional output you need to list the size of each dimension
        here, or give ``None``.
    fill_value: default=0
        in the example above, group 2 does not have any data, so requires some
        kind of filling value - in this case the default of ``0`` is used.  If
        you had set ``fill_value=nan`` or something else, that value would
        appear instead of ``0`` for the 2 element in the output.  Note that
        there are some subtle interactions between what is permitted for
        ``fill_value`` and the input/output ``dtype`` - exceptions should be
        raised in most cases to alert the programmer if issue arrise.
    order: default='C'
        this is relevant only for multimensional output.  It controls the
        layout of the output array in memory, can be ``'F'`` for fortran-style.
    dtype: default=None
        the ``dtype`` of the output.  By default something sensible is chosen
        based on the input, aggregation function, and ``fill_value``.
    ddof: default=0
        passed through into calculations of variance and standard deviation
        (see above).
"""

funcs_common = "first last len mean var std allnan anynan max min argmax argmin sumofsquares cumsum cumprod cummax cummin".split()
funcs_no_separate_nan = frozenset(["sort", "rsort", "array", "allnan", "anynan"])


_alias_str = {
    "or": "any",
    "and": "all",
    "add": "sum",
    "count": "len",
    "plus": "sum",
    "multiply": "prod",
    "product": "prod",
    "times": "prod",
    "amax": "max",
    "maximum": "max",
    "amin": "min",
    "minimum": "min",
    "split": "array",
    "splice": "array",
    "sorted": "sort",
    "asort": "sort",
    "asorted": "sort",
    "rsorted": "sort",
    "dsort": "sort",
    "dsorted": "rsort",
}

_alias_builtin = {
    all: "all",
    any: "any",
    len: "len",
    max: "max",
    min: "min",
    sum: "sum",
    sorted: "sort",
    slice: "array",
    list: "array",
}


_alias_numpy = {
    np.add: "sum",
    np.sum: "sum",
    np.any: "any",
    np.all: "all",
    np.multiply: "prod",
    np.prod: "prod",
    np.amin: "min",
    np.min: "min",
    np.minimum: "min",
    np.amax: "max",
    np.max: "max",
    np.maximum: "max",
    np.argmax: "argmax",
    np.argmin: "argmin",
    np.mean: "mean",
    np.std: "std",
    np.var: "var",
    np.array: "array",
    np.asarray: "array",
    np.sort: "sort",
    np.cumsum: "cumsum",
    np.cumprod: "cumprod",
    np.nansum: "nansum",
    np.nanprod: "nanprod",
    np.nanmean: "nanmean",
    np.nanvar: "nanvar",
    np.nanmax: "nanmax",
    np.nanmin: "nanmin",
    np.nanstd: "nanstd",
    np.nanargmax: "nanargmax",
    np.nanargmin: "nanargmin",
    np.nancumsum: "nancumsum",
}


def get_aliasing(*extra):
    """
    Assembles a dictionary that maps both strings and functions to a list of supported function names.

    Examples:
        alias['add'] = 'sum'
        alias[sorted] = 'sort'

    This function should only be called during import.
    """
    alias = dict((k, k) for k in funcs_common)
    alias.update(_alias_str)
    alias.update((fn, fn) for fn in _alias_builtin.values())
    alias.update(_alias_builtin)
    for d in extra:
        alias.update(d)
    alias.update((k, k) for k in set(alias.values()))
    # Treat nan-functions as firstclass member and add them directly
    for key in set(alias.values()):
        if key not in funcs_no_separate_nan and not key.startswith("nan"):
            key = "nan" + key
            alias[key] = key
    return alias


aliasing_py = get_aliasing()
aliasing = get_aliasing(_alias_numpy)


def get_func(func, aliasing, implementations):
    """Return the key of a found implementation or the func itself"""
    try:
        func_str = aliasing[func]
    except KeyError:
        if callable(func):
            return func
    else:
        if func_str in implementations:
            return func_str
        if func_str.startswith("nan") and func_str[3:] in funcs_no_separate_nan:
            raise ValueError(f"{func_str[3:]} does not have a nan-version")
        else:
            raise NotImplementedError("No such function available")
    raise ValueError(
        f"func {func} is neither a valid function string nor a callable object"
    )


def check_boolean(x):
    if x not in (0, 1):
        raise ValueError("Value not boolean")


_next_int_dtype = dict(
    bool=np.int8,
    uint8=np.int16,
    int8=np.int16,
    uint16=np.int32,
    int16=np.int32,
    uint32=np.int64,
    int32=np.int64,
)

_next_float_dtype = dict(
    float16=np.float32,
    float32=np.float64,
    float64=np.complex64,
    complex64=np.complex128,
)


def minimum_dtype(x, dtype=np.bool_):
    """
    Returns the "most basic" dtype which represents `x` properly, which provides at least the same
    value range as the specified dtype.
    """

    def check_type(x, dtype):
        try:
            with np.errstate(invalid="ignore"):
                converted = np.array(x).astype(dtype)
        except (ValueError, OverflowError, RuntimeWarning):
            return False
        # False if some overflow has happened
        return converted == x or np.isnan(x)

    def type_loop(x, dtype, dtype_dict, default=None):
        while True:
            try:
                dtype = np.dtype(dtype_dict[dtype.name])
                if check_type(x, dtype):
                    return np.dtype(dtype)
            except KeyError:
                if default is not None:
                    return np.dtype(default)
                raise ValueError(f"Can not determine dtype of {x!r}")

    dtype = np.dtype(dtype)
    if check_type(x, dtype):
        return dtype

    if np.issubdtype(dtype, np.inexact):
        return type_loop(x, dtype, _next_float_dtype)
    else:
        return type_loop(x, dtype, _next_int_dtype, default=np.float32)


def minimum_dtype_scalar(x, dtype, a):
    if dtype is None:
        dtype = np.dtype(type(a)) if isinstance(a, (int, float)) else a.dtype
    return minimum_dtype(x, dtype)


_forced_types = {
    "array": object,
    "all": bool,
    "any": bool,
    "nanall": bool,
    "nanany": bool,
    "len": np.int64,
    "nanlen": np.int64,
    "allnan": bool,
    "anynan": bool,
    "argmax": np.int64,
    "argmin": np.int64,
    "nanargmin": np.int64,
    "nanargmax": np.int64,
}
if platform.architecture()[0] == "32bit":
    _forced_types = {
        "array": object,
        "all": bool,
        "any": bool,
        "nanall": bool,
        "nanany": bool,
        "len": np.int32,
        "nanlen": np.int32,
        "allnan": bool,
        "anynan": bool,
        "argmax": np.int32,
        "argmin": np.int32,
        "nanargmin": np.int32,
        "nanargmax": np.int32,
    }
_forced_float_types = {"mean", "var", "std", "nanmean", "nanvar", "nanstd"}
_forced_same_type = {
    "min",
    "max",
    "first",
    "last",
    "nanmin",
    "nanmax",
    "nanfirst",
    "nanlast",
}


def check_dtype(dtype, func_str, a, n):
    if np.isscalar(a) or not a.shape:
        if func_str not in ("sum", "prod", "len"):
            raise ValueError(
                "scalar inputs are supported only for 'sum', 'prod' and 'len'"
            )
        a_dtype = np.dtype(type(a))
    else:
        a_dtype = a.dtype

    if dtype is not None:
        # dtype set by the user
        # Careful here: np.bool != np.bool_ !
        if np.issubdtype(dtype, np.bool_) and not (
            "all" in func_str or "any" in func_str
        ):
            raise TypeError(
                f"function {func_str} requires a more complex datatype than bool"
            )
        if not np.issubdtype(dtype, np.integer) and func_str in ("len", "nanlen"):
            raise TypeError(f"function {func_str} requires an integer datatype")
        # TODO: Maybe have some more checks here
        return np.dtype(dtype)
    else:
        try:
            return np.dtype(_forced_types[func_str])
        except KeyError:
            if func_str in _forced_float_types:
                if np.issubdtype(a_dtype, np.floating):
                    return a_dtype
                else:
                    return np.dtype(np.float64)
            else:
                if func_str == "sum":
                    # Try to guess the minimally required int size
                    if np.issubdtype(a_dtype, np.int64):
                        # It's not getting bigger anymore
                        # TODO: strictly speaking it might need float
                        return np.dtype(np.int64)
                    elif np.issubdtype(a_dtype, np.integer):
                        maxval = np.iinfo(a_dtype).max * n
                        return minimum_dtype(maxval, a_dtype)
                    elif np.issubdtype(a_dtype, np.bool_):
                        return minimum_dtype(n, a_dtype)
                    else:
                        # floating, inexact, whatever
                        return a_dtype
                elif func_str in _forced_same_type:
                    return a_dtype
                else:
                    if isinstance(a_dtype, np.integer):
                        return np.dtype(np.int64)
                    else:
                        return a_dtype


def minval(fill_value, dtype):
    dtype = minimum_dtype(fill_value, dtype)
    if issubclass(dtype.type, np.floating):
        return -np.inf
    if issubclass(dtype.type, np.integer):
        return np.iinfo(dtype).min
    return np.finfo(dtype).min


def maxval(fill_value, dtype):
    dtype = minimum_dtype(fill_value, dtype)
    if issubclass(dtype.type, np.floating):
        return np.inf
    if issubclass(dtype.type, np.integer):
        return np.iinfo(dtype).max
    return np.finfo(dtype).max


def check_fill_value(fill_value, dtype, func=None):
    if func in ("all", "any", "allnan", "anynan"):
        check_boolean(fill_value)
    else:
        try:
            return dtype.type(fill_value)
        except ValueError:
            raise ValueError(
                f"fill_value must be convertible into {dtype.type.__name__}"
            )


def check_group_idx(group_idx, a=None, check_min=True):
    if a is not None and group_idx.size != a.size:
        raise ValueError("The size of group_idx must be the same as a.size")
    if not issubclass(group_idx.dtype.type, np.integer):
        raise TypeError("group_idx must be of integer type")
    if check_min and np.min(group_idx) < 0:
        raise ValueError("group_idx contains negative indices")


def _ravel_group_idx(group_idx, a, axis, size, order, method="ravel"):
    ndim_a = a.ndim
    # Create the broadcast-ready multidimensional indexing.
    # Note the user could do this themselves, so this is
    # very much just a convenience.
    size_in = int(np.max(group_idx)) + 1 if size is None else size
    group_idx_in = group_idx
    group_idx = []
    size = []
    for ii, s in enumerate(a.shape):
        if method == "ravel":
            ii_idx = group_idx_in if ii == axis else np.arange(s)
            ii_shape = [1] * ndim_a
            ii_shape[ii] = s
            group_idx.append(ii_idx.reshape(ii_shape))
        size.append(size_in if ii == axis else s)
    # Use the indexing, and return. It's a bit simpler than
    # using trying to keep all the logic below happy
    if method == "ravel":
        group_idx = np.ravel_multi_index(group_idx, size, order=order, mode="raise")
    elif method == "offset":
        group_idx = offset_labels(group_idx_in, a.shape, axis, order, size_in)
    return group_idx, size


def offset_labels(group_idx, inshape, axis, order, size):
    """
    Offset group labels by dimension. This is used when we reduce over a subset of the dimensions of
    group_idx. It assumes that the reductions dimensions have been flattened in the last dimension
    Copied from
    https://stackoverflow.com/questions/46256279/bin-elements-per-row-vectorized-2d-bincount-for-numpy
    """

    newaxes = tuple(ax for ax in range(len(inshape)) if ax != axis)
    group_idx = np.broadcast_to(np.expand_dims(group_idx, newaxes), inshape)
    if axis not in (-1, len(inshape) - 1):
        group_idx = np.moveaxis(group_idx, axis, -1)
    newshape = group_idx.shape[:-1] + (-1,)

    group_idx = (
        group_idx
        + np.arange(np.prod(newshape[:-1]), dtype=int).reshape(newshape) * size
    )
    if axis not in (-1, len(inshape) - 1):
        return np.moveaxis(group_idx, -1, axis)
    else:
        return group_idx


def input_validation(
    group_idx,
    a,
    size=None,
    order="C",
    axis=None,
    ravel_group_idx=True,
    check_bounds=True,
    func=None,
):
    """
    Do some fairly extensive checking of group_idx and a, trying to give the user as much help as
    possible with what is wrong. Also, convert ndim-indexing to 1d indexing.
    """
    if not isinstance(a, (int, float, complex)) and not is_duck_array(a):
        a = np.asanyarray(a)
    if not is_duck_array(group_idx):
        group_idx = np.asanyarray(group_idx)

    if not np.issubdtype(group_idx.dtype, np.integer):
        raise TypeError("group_idx must be of integer type")

    # This check works for multidimensional indexing as well
    if check_bounds and np.any(group_idx < 0):
        raise ValueError("negative indices not supported")

    ndim_idx = np.ndim(group_idx)
    ndim_a = np.ndim(a)

    # Deal with the axis arg: if present, then turn 1d indexing into
    # multi-dimensional indexing along the specified axis.
    if axis is None:
        if ndim_a > 1:
            raise ValueError(
                "a must be scalar or 1 dimensional, use .ravel to flatten. Alternatively specify axis."
            )
    elif axis >= ndim_a or axis < -ndim_a:
        raise ValueError("axis arg too large for np.ndim(a)")
    else:
        axis = axis if axis >= 0 else ndim_a + axis  # negative indexing
        if ndim_idx > 1:
            # TODO: we could support a sequence of axis values for multiple
            # dimensions of group_idx.
            raise NotImplementedError(
                "only 1d indexing currently supported with axis arg."
            )
        elif a.shape[axis] != len(group_idx):
            raise ValueError("a.shape[axis] doesn't match length of group_idx.")
        elif size is not None and not np.isscalar(size):
            raise NotImplementedError(
                "when using axis arg, size must be None or scalar."
            )
        else:
            is_form_3 = group_idx.ndim == 1 and a.ndim > 1 and axis is not None
            orig_shape = a.shape if is_form_3 else group_idx.shape
            if isinstance(func, str) and "arg" in func:
                unravel_shape = orig_shape
            else:
                unravel_shape = None

            method = "offset" if axis == ndim_a - 1 else "ravel"
            group_idx, size = _ravel_group_idx(
                group_idx, a, axis, size, order, method=method
            )
            flat_size = np.prod(size)
            ndim_idx = ndim_a
            size = (
                orig_shape
                if is_form_3 and not callable(func) and "cum" in func
                else size
            )
            return (
                group_idx.ravel(),
                a.ravel(),
                flat_size,
                ndim_idx,
                size,
                unravel_shape,
            )

    if ndim_idx == 1:
        if size is None:
            size = int(np.max(group_idx)) + 1
        else:
            if not np.isscalar(size):
                raise ValueError("output size must be scalar or None")
            if check_bounds and np.any(group_idx > size - 1):
                raise ValueError(f"one or more indices are too large for size {size}")
        flat_size = size
    else:
        if size is None:
            size = np.max(group_idx, axis=1).astype(int) + 1
        elif np.isscalar(size):
            raise ValueError(f"output size must be of length {len(group_idx)}")
        elif len(size) != len(group_idx):
            raise ValueError(
                f"{len(size)} sizes given, but {len(group_idx)} output dimensions specified in index"
            )
        if ravel_group_idx:
            group_idx = np.ravel_multi_index(group_idx, size, order=order, mode="raise")
        flat_size = np.prod(size)

    if not (np.ndim(a) == 0 or len(a) == group_idx.size):
        raise ValueError(
            "group_idx and a must be of the same length, or a can be scalar"
        )

    return group_idx, a, flat_size, ndim_idx, size, None


# General tools


def unpack(group_idx, ret):
    """
    Take an aggregate packed array and uncompress it to the size of group_idx. This is equivalent to
    ret[group_idx].
    """
    return ret[group_idx]


def allnan(x):
    return np.all(np.isnan(x))


def anynan(x):
    return np.any(np.isnan(x))


def nanfirst(x):
    return x[~np.isnan(x)][0]


def nanlast(x):
    return x[~np.isnan(x)][-1]


def multi_arange(n):
    """By example:

        #    0  1  2  3  4  5  6  7  8
        n = [0, 0, 3, 0, 0, 2, 0, 2, 1]
        res = [0, 1, 2, 0, 1, 0, 1, 0]

    That is it is equivalent to something like this :

        hstack((arange(n_i) for n_i in n))

    This version seems quite a bit faster, at least for some possible inputs, and at any rate it
    encapsulates a task in a function.
    """
    if n.ndim != 1:
        raise ValueError("n is supposed to be 1d array.")

    n_mask = n.astype(bool)
    n_cumsum = np.cumsum(n)
    ret = np.ones(n_cumsum[-1] + 1, dtype=int)
    ret[n_cumsum[n_mask]] -= n[n_mask]
    ret[0] -= 1
    return np.cumsum(ret)[:-1]


def label_contiguous_1d(X):
    """
    WARNING: API for this function is not liable to change!!!

    By example:

        X =      [F T T F F T F F F T T T]
        result = [0 1 1 0 0 2 0 0 0 3 3 3]

    Or:
        X =      [0 3 3 0 0 5 5 5 1 1 0 2]
        result = [0 1 1 0 0 2 2 2 3 3 0 4]

    The ``0`` or ``False`` elements of ``X`` are labeled as ``0`` in the output. If ``X`` is a boolean
    array, each contiguous block of ``True`` is given an integer label, if ``X`` is not boolean, then
    each contiguous block of identical values is given an integer label. Integer labels are 1, 2, 3,
    ..... (i.e. start a 1 and increase by 1 for each block with no skipped numbers.)
    """

    if X.ndim != 1:
        raise ValueError("this is for 1d masks only.")

    is_start = np.empty(len(X), dtype=bool)
    is_start[0] = X[0]  # True if X[0] is True or non-zero

    if X.dtype.kind == "b":
        is_start[1:] = ~X[:-1] & X[1:]
        M = X
    else:
        M = X.astype(bool)
        is_start[1:] = X[:-1] != X[1:]
        is_start[~M] = False

    L = np.cumsum(is_start)
    L[~M] = 0
    return L


def relabel_groups_unique(group_idx):
    """
    See also ``relabel_groups_masked``.

    keep_group:  [0 3 3 3 0 2 5 2 0 1 1 0 3 5 5]
    ret:         [0 3 3 3 0 2 4 2 0 1 1 0 3 4 4]

    Description of above: unique groups in input was ``1,2,3,5``, i.e.
    ``4`` was missing, so group 5 was relabled to be ``4``.
    Relabeling maintains order, just "compressing" the higher numbers
    to fill gaps.
    """

    keep_group = np.zeros(np.max(group_idx) + 1, dtype=bool)
    keep_group[0] = True
    keep_group[group_idx] = True
    return relabel_groups_masked(group_idx, keep_group)


def relabel_groups_masked(group_idx, keep_group):
    """
    group_idx: [0 3 3 3 0 2 5 2 0 1 1 0 3 5 5]

                 0 1 2 3 4 5
    keep_group: [0 1 0 1 1 1]

    ret:       [0 2 2 2 0 0 4 0 0 1 1 0 2 4 4]

    Description of above in words: remove group 2, and relabel group 3,4, and 5 to be 2, 3 and 4
    respectively, in order to fill the gap.  Note that group 4 was never used in the input group_idx,
    but the user supplied mask said to keep group 4, so group 5 is only moved up by one place to fill
    the gap created by removing group 2.

    That is, the mask describes which groups to remove, the remaining groups are relabled to remove the
    gaps created by the falsy elements in ``keep_group``. Note that ``keep_group[0]`` has no particular
    meaning because it refers to the zero group which cannot be "removed".

    ``keep_group`` should be bool and ``group_idx`` int. Values in ``group_idx`` can be any order.
    """

    keep_group = keep_group.astype(bool, copy=not keep_group[0])
    if not keep_group[0]:  # ensuring keep_group[0] is True makes life easier
        keep_group[0] = True

    relabel = np.zeros(keep_group.size, dtype=group_idx.dtype)
    relabel[keep_group] = np.arange(np.count_nonzero(keep_group))
    return relabel[group_idx]


def is_duck_array(value):
    """This function was copied from xarray/core/utils.py under the terms of Xarray's Apache-2 license."""

    if isinstance(value, np.ndarray):
        return True
    return (
        hasattr(value, "ndim")
        and hasattr(value, "shape")
        and hasattr(value, "dtype")
        and hasattr(value, "__array_function__")
        and hasattr(value, "__array_ufunc__")
    )


def iscomplexobj(x):
    """Copied from np.iscomplexobj so that we place fewer requirements on duck array types."""

    try:
        dtype = x.dtype
        type_ = dtype.type
    except AttributeError:
        type_ = np.asarray(x).dtype.type
    return issubclass(type_, np.complexfloating)
