##from warnings import warn as _warn
##class TypeWarning(UserWarning):pass
##
##_fs=(('1','__add__','+'),('1','__and__','&'),
##     ('1','__divmod__','divmod()'),('1','__floordiv__','//'),
##     ('1','__lshift__','<<'),('1','__mod__','%'),('1','__mul__','*'),
##     ('1','__or__','|'),('1','__pow__','** or pow()'),
##     ('-1','__radd__','+'),('-1','__rand__','&'),
##     ('-1','__rdivmod__','divmod()'),('-1','__rfloordiv__','//'),
##     ('-1','__rlshift__','<<'),('-1','__rmod__','%'),
##     ('-1','__rmul__','*'),('-1','__ror__','|'),('-1','__rpow__','**'),
##     ('-1','__rrshift__','>>'),('1','__rshift__','>>'),
##     ('-1','__rsub__','-'),('-1','__rtruediv__','/'),
##     ('-1','__rxor__','^'),('1','__sub__','-'),('1','__truediv__','/'),
##     ('1','__xor__','^'),('__abs__','abs'),('__ceil__','ceil'),
##     ('__floor__','floor'),('__invert__','~'),('__neg__','unary -'),
##     ('__pos__','+'),('__round__','round'),('__trunc__','trunc'),
##     ('conjugate','conjugate'))
##
##def _bop(op,opstr,order):
##    def _f(self,value,/):
##        self._invbop(opstr,value,order)
##        return type(self)(op(int(self),int(value))&((1<<self._size)-1))
##    return _f
##def _uop(op,opstr):
##    def _f(self,/):
##        self._invuop(opstr,value)
##        return type(self)(op(int(self))&((1<<self._size)-1))
##    return _f
##def _opm(op,default):
##    if op=="/":
##        return int.__floordiv__
##    return getattr(int,default)
##def _typename(value):
##    if hasattr(value,"_name"):
##        return value._name
##    return type(value).__name__
##def _int_t_gen(signed, size):
##    class _c(int):
##        _signed=signed
##        _size=size
##        _name=f"{'u'*signed}int{size}_t"
##        def _invbop(self,op,value,order,/):
##            if value.denominator!=1:
##                raise TypeError(
##                    f"unsupported operand type(s) for {op}: "+
##                    (f"'{self._name}' and '{_typename(value)}'"
##                     if order>0 else
##                     f"'{_typename(value)}' and '{self._name}'"))
##            if op=="/":
##                _warn(
##                    f"/ undefined for '{self._name}', using // instead",
##                    TypeWarning)
##        def _invuop(self,op,/):
##            match op:
##                case "unary -":
##                    if not self._signed:
##                        raise TypeError(
##                         f"bad operand type for {op}(): '{self._name}'")
##        def __repr__(self):
##            return f"<{self._name} {int(self)}>"
##        def __str__(self):
##            return str(int(self))
##    for m in _fs:
##        if m[0]in("1","-1"):
##            setattr(_c,m[1],_bop(_opm(m[2],m[1]),m[2],int(m[0])*2))
##        else:
##            setattr(_c,m[0],_uop(_opm(m[1],m[0]),m[1]))
##    return _c
##def _make_int_t(signed, size):
##    globals()[f"{'u'*(1-signed)}int{size}_t"]=_int_t_gen(signed,size)
##    globals()[f"{'U'*(1-signed)}INT{size}_MAX"]=(1<<size)-1
##    __all__.append(f"{'u'*(1-signed)}int{size}_t")
##    __all__.append(f"{'U'*(1-signed)}INT{size}_MAX")
##
##__all__ = []
##_make_int_t(False, 8)
##_make_int_t(False, 16)
##_make_int_t(False, 32)
##_make_int_t(False, 64)

class uint8_t:pass
class uint16_t:pass
UINT8_MAX = 255
UINT16_MAX = 65535
