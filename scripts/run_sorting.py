import os
import json
import time
import click
import spikeinterface as si
import spikeinterface.extractors as se
import spikeinterface.sorters as ss
import kachery_cloud as kcl
import sortingview as sv


@click.command(help="Run spike sorting")
@click.option('--collection')
@click.option('--study')
@click.option('--recording')
@click.option('--sorter')
def run_sorting(collection: str, study: str, recording: str, sorter: str):
    collection_name = collection
    study_name = study
    recording_name = recording
    sorter_name = sorter

    dirname = f'datasets/{collection_name}/{study_name}/{recording_name}'
    with open(f'{dirname}/recording.json', 'r') as f:
        recording_object = json.load(f)
    rec = sv.load_recording_extractor(recording_object)
    print(f'{collection_name}/{study_name}/{recording_name}')
    print(f'Num. channels: {rec.get_num_channels()}')
    print(f'Duration (sec): {rec.get_total_duration()}')
    print(f'Sampling frequency (Hz): {rec.get_sampling_frequency()}')
    print('')
    print('Channel locations:')
    print('X:', rec.get_channel_locations()[:, 0].T)
    print('Y:', rec.get_channel_locations()[:, 1].T)

    if sorter_name == 'mountainsort4':
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
            rec,
            output_folder='tmp/working',
            verbose=True,
            num_workers=4,
            **sorter_params
        )
        elapsed = time.time() - timer
        print(f'ELAPSED TIME: {elapsed}')
    elif sorter_name == 'spykingcircus':
        sorter_params = {
            'detect_sign': -1,  # -1 - 1 - 0
            'adjacency_radius': 100,  # Channel neighborhood adjacency radius corresponding to geom file
            'detect_threshold': 6,  # Threshold for detection
            'template_width_ms': 3,  # Spyking circus parameter
            'filter': True,
            'merge_spikes': True,
            'auto_merge': 0.75,
            'whitening_max_elts': 1000,  # I believe it relates to subsampling and affects compute time
            'clustering_max_elts': 10000,  # I believe it relates to subsampling and affects compute time
        }
        print('Running spykingcircus')
        timer = time.time()
        sorting: si.BaseSorting = ss.run_sorter(
            'spykingcircus',
            rec,
            output_folder='tmp/working',
            verbose=True,
            num_workers=4,
            **sorter_params
        )
        elapsed = time.time() - timer
        print(f'ELAPSED TIME: {elapsed}')
    else:
        raise Exception(f'Unexpected sorter name: {sorter_name}')
    print(f'Sorting extractor info: unit ids = {sorting.get_unit_ids()}, {sorting.get_sampling_frequency()} Hz')
    print('')
    for unit_id in sorting.get_unit_ids():
        st = sorting.get_unit_spike_train(unit_id=unit_id)
        print(f'Unit {unit_id}: {len(st)} events')
    print('')

    sorting = sv.copy_sorting_extractor(sorting, upload_firings=True)
    sorting_object = sv.get_sorting_object(sorting)
    print('Unit IDs:', sorting.get_unit_ids())
    output_dirname = f'{dirname}/sortings/{sorter_name}'
    os.makedirs(output_dirname, exist_ok=True)
    with open(f'{output_dirname}/sorting.json', 'w') as f:
        json.dump(sorting_object, f)

if __name__ == '__main__':
    run_sorting()