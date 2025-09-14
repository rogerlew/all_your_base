from urllib.request import urlopen

from ...all_your_base import isfloat


wmesque_url = 'https://wepp.cloud/webservices/wmesque/'


def wmesque_retrieve(dataset, extent, fname, cellsize, resample=None):
    global wmesque_url

    assert isfloat(cellsize)

    assert all([isfloat(v) for v in extent])
    assert len(extent) == 4

    extent = ','.join([str(v) for v in extent])

    if fname.lower().endswith('.tif'):
        fmt = 'GTiff'

    elif fname.lower().endswith('.asc'):
        fmt = 'AAIGrid'

    elif fname.lower().endswith('.png'):
        fmt = 'PNG'

    else:
        raise ValueError('fname must end with .tif, .asc, or .png')

    url = f'{wmesque_url}{dataset}/?bbox={extent}&cellsize={cellsize}&format={fmt}'

    if resample is not None:
        url += f'&resample={resample}'

    try:
        output = urlopen(url, timeout=60)
        with open(fname, 'wb') as fp:
            fp.write(output.read())
    except Exception:
        raise Exception("Error retrieving: %s" % url)

    return 1

if __name__ == "__main__":
    wmesque_retrieve('ned1/2022',
                     [-116.42555236816408, 45.233799855252855, -116.32701873779298, 45.303146403608935],
                     '/home/roger/output.tif',
                     30.0)