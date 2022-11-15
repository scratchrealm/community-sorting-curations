import json
import spikeforest as sf
import sortingview as sv


def main():
    study_name = 'paired_boyden32c'
    recording_name = '1103_1_1'
    R = sf.load_spikeforest_recording(study_name=study_name, recording_name=recording_name)
    recording_object: dict = R.recording_object
    sorting_true_object: dict = R.sorting_true_object
    R = sv.load_recording_extractor(recording_object)
    S_true = sv.load_sorting_extractor(sorting_true_object)
    dirname = f'{study_name}/{recording_name}'
    with open(f'{dirname}/recording.json', 'w') as f:
        json.dump(recording_object, f)
    with open(f'{dirname}/sorting_true.json', 'w') as f:
        json.dump(sorting_true_object, f)

if __name__ == '__main__':
    main()