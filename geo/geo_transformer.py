from typing import Any
import os
import numpy as np

IS_WINDOWS = os.name == 'nt'


def _strip_warning(ret):
    
    if ret[0].startswith('Warning'):
        _ret = list(ret)
        _ret[0] = '\n'.join(ret[0].split('\n')[1:])
        return _ret

    return ret


class GeoTransformer(object):
    def __init__(self, src_proj4=None, src_epsg=None, dst_proj4=None, dst_epsg=None):
        assert src_proj4 or src_epsg
        assert dst_proj4 or dst_epsg
        
        self.src_proj4 = src_proj4
        self.src_epsg = src_epsg
        self.dst_proj4 = dst_proj4
        self.dst_epsg = dst_epsg

    def transform(self, x, y, reverse=False):
        src_proj4 = self.src_proj4
        src_epsg = self.src_epsg
        dst_proj4 = self.dst_proj4
        dst_epsg = self.dst_epsg

        if reverse:
            src_proj4, src_epsg, dst_proj4, dst_epsg = \
                dst_proj4, dst_epsg, src_proj4, src_epsg

        if IS_WINDOWS:
            from pyproj import Proj, transform
            if self.src_proj4:
                src_proj = Proj(src_proj4)
            else:
                src_proj = Proj('EPSG:%i' % src_epsg)
    
            if dst_proj4:
                dst_proj = Proj(dst_proj4)
            else:
                dst_proj = Proj('EPSG:%i' % dst_epsg)
                
            return transform(src_proj, dst_proj, x, y)
        else:
            if self.src_proj4:
                s_srs = src_proj4
            else:
                s_srs = 'EPSG:%i' % src_epsg

            if dst_proj4:
                t_srs = dst_proj4
            else:
                t_srs = 'EPSG:%i' % dst_epsg

            from subprocess import Popen, PIPE, STDOUT
            cmd = ['gdaltransform', '-s_srs', s_srs, '-t_srs', t_srs, '-output_xy']

            if np.isscalar(x):

                p = Popen(cmd, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=STDOUT, 
                          universal_newlines=True)
                ret = p.communicate('{x} {y}'.format(x=x, y=y))
                ret = _strip_warning(ret)
                try:
                    return tuple(float(v) for v in ret[0].strip().split())
                except:
                    print(f'Error: {ret}')
                    raise ValueError('gdaltransform failed to transform coordinates. '
                                     'Check the input coordinates and projection parameters.')
            else:
                _ret = []
                for _x, _y in zip(x, y):
                    p = Popen(cmd, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=STDOUT, 
                              universal_newlines=True)
                    ret = p.communicate('{x} {y}'.format(x=_x, y=_y))
                    ret = _strip_warning(ret)   
                    try:
                        _ret.append(tuple(float(v) for v in ret[0].strip().split()))
                    except:
                        print(f'Error: {ret}')
                        raise ValueError('gdaltransform failed to transform coordinates. '
                                        'Check the input coordinates and projection parameters.')
                return _ret

    def reverse(self, x, y):
        return self.transform(x, y, reverse=True)


if __name__ == "__main__":
    _dst_proj4 = '+proj=lcc +lat_1=25 +lat_2=60 +lat_0=42.5 +lon_0=-100 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs'
    _wgs_2_lcc = GeoTransformer(src_epsg=4326, dst_proj4=_dst_proj4)
    e, n = _wgs_2_lcc.transform(-117.0, 47.0)
    print(e, n)
