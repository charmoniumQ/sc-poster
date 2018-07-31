import matplotlib.pyplot as plt
import numpy as np

def aggregate(xs, ys, fn):
    unique_x = sorted(list(frozenset(map(tuple, xs))))
    result = []
    for x in unique_x:
        matching = (xs == x).all(axis=1)
        result.append(fn(ys[matching]))
    unique_x = np.array(unique_x)
    return unique_x, np.array(result)


def arg_nearest(array, value):
    return np.abs(array - value).argmin()

def nearest(array, value):
    return array[arg_nearest(array, value)]

def arg_nearest_2d(array, point):
    return ((array - point)**2).sum(axis=1).argmin()


# https://stackoverflow.com/a/11146645/1078199
def cartesian_product(arrays):
    la = len(arrays)
    dtype = np.find_common_type([a.dtype for a in arrays], [])
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[..., i] = a
    return arr.reshape(-1, la)


def prepare_data(series):
    for seri in series.values():
        if 'all_2d_params' in seri:
            continue
        seri['all_2d_params'] = np.vstack([seri['params'][0], seri['params'][1]]).T
        seri['ts'] = np.array(seri['ts'])
        seri['actual_2d_params'], seri['mean_ts'] = aggregate(seri['all_2d_params'], seri['ts'], np.mean)
        _, seri['std_ts'] = aggregate(seri['all_2d_params'], seri['ts'], lambda x: (np.std(x, ddof=1) if len(x) > 1 else x))
        if seri['interpolate']:
            param0 = actual_2d_params[:, 0]
            param1 = actual_2d_params[:, 1]
            seri['mean_f'] = interp2d(
                param0,
                param1,
                mean_ts,
                bounds_error=False,
                fill_value=np.NaN,
            )
            seri['std_f'] = interp2d(
                param0,
                param1,
                mean_ts,
                bounds_error=False,
                fill_value=0,
            )

        seri['params'][0] = seri['actual_2d_params'][:, 0]
        seri['params'][1] = seri['actual_2d_params'][:, 1]


def mk_params(series, param_labels):
    base_seri = next(iter(series.values()))
    params = {0: {}, 1: {}}
    for param_no, ax in [(0, 'x'), (1, 'y')]:
        param = params[param_no]
        param['param_no'] = param_no
        param['other_param_no'] = {0: 1, 1: 0}[param_no]
        param['ax'] = ax
        param['oax'] = {'x': 'y', 'y': 'x'}[param['ax']]
        param['dw_dh'] = {'x': 'dw', 'y': 'dh'}[param['ax']]
        param['raw'] = base_seri['params'][param_no]
        param['raw_unique'] = np.unique(param['raw'])
        param['epsilon'] = np.diff(param['raw_unique']).min()
        param['min'] = param['raw'].min()
        param['max'] = param['raw'].max()
        param['resampled'] = np.linspace(
            param['min'],
            param['max'],
            100,
        )
        param['const'] = 0
        param['label'] = param_labels[param['param_no']]
    return params

def export_img(seri, params):
    full_param_grid = cartesian_product([params[i]['raw_unique'] for i in range(len(params))])
    epsilon_arr = np.array([params[i]['epsilon'] for i in range(len(params))])
    actual_param_grid = seri['actual_2d_params']
    data = []
    for point in full_param_grid:
        nearest_point_arg = arg_nearest_2d(actual_param_grid, point)
        nearest_point = actual_param_grid[nearest_point_arg]
        if (np.abs(nearest_point - point) < epsilon_arr).all():
            data.append(seri['mean_ts'][nearest_point_arg])
        else:
            data.append(np.nan)
    data = np.reshape(data, tuple(len(params[i]['raw_unique']) for i in range(len(params))))

    extreme = np.fabs(data).max()
    extreme = extreme * 0.6
    plt.imshow(
        np.clip(data, -extreme, +extreme),
        extent=[params[1]['min'], params[1]['max'], params[0]['min'], params[0]['max']],
        vmin=-extreme,
        vmax=+extreme,
        cmap='RdBu',
    )
    cbar = plt.colorbar()
    plt.xticks(np.arange(params[1]['min'], params[1]['max']))
    plt.yticks(np.arange(params[0]['min'], params[0]['max']))
    plt.xlabel(params[1]['label'])
    plt.ylabel(params[0]['label'])
    return cbar
