import os
import json
import time
import spikeinterface as si
import spikeinterface.sorters as ss
import kachery_cloud as kcl
import sortingview as sv


def main():
    collection_name = 'spikeforest'
    study_name = 'paired_boyden32c'
    recording_name = '1103_1_1'
    dirname = f'datasets/{collection_name}/{study_name}/{recording_name}'
    with open(f'{dirname}/recording.json', 'r') as f:
        recording_object = json.load(f)
    recording = sv.load_recording_extractor(recording_object)
    print(f'{collection_name}/{study_name}/{recording_name}')
    print(f'Num. channels: {recording.get_num_channels()}')
    print(f'Duration (sec): {recording.get_total_duration()}')
    print(f'Sampling frequency (Hz): {recording.get_sampling_frequency()}')
    print('')
    print('Channel locations:')
    print('X:', recording.get_channel_locations()[:, 0].T)
    print('Y:', recording.get_channel_locations()[:, 1].T)

    sorter_params = {
        'detect_sign': -1,
        'adjacency_radius': 25,
        'freq_min': 300,  # Use None for no bandpass filtering
        'freq_max': 6000,
        'filter': False,
        'whiten': True,  # Whether to do channel whitening as part of preprocessing
        'clip_size': 50,
        'detect_threshold': 3,
        'detect_interval': 10
    }
    print('Running mountainsort4')
    timer = time.time()
    sorting: si.BaseSorting = ss.run_sorter(
        'mountainsort4',
        recording,
        output_folder='tmp/working',
        verbose=True,
        num_workers=4,
        **sorter_params
    )
    elapsed = time.time() - timer
    print(f'ELAPSED TIME: {elapsed}')

    print(f'Sorting extractor info: unit ids = {sorting.get_unit_ids()}, {sorting.get_sampling_frequency()} Hz')
    print('')
    for unit_id in sorting.get_unit_ids():
        st = sorting.get_unit_spike_train(unit_id=unit_id)
        print(f'Unit {unit_id}: {len(st)} events')
    print('')

    firings_npz_path = 'tmp/working/firings.npz'
    npz_file_uri = kcl.store_file(firings_npz_path, label='firings.npz')
    sorting_object = {
        'sorting_format': 'npz',
        'data': {
            'npz_file_uri': npz_file_uri
        }
    }
    sorting = sv.load_sorting_extractor(sorting_object)
    print('Unit IDs:', sorting.get_unit_ids())
    output_dirname = f'{dirname}/sortings/mountainsort4'
    os.makedirs(output_dirname, exist_ok=True)
    with open(f'{output_dirname}/sorting.json', 'w') as f:
        json.dump(sorting_object, f)

if __name__ == '__main__':
    main()