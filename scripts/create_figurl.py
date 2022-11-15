import json
import spikeforest as sf
import spikeinterface as si
import spikeinterface.preprocessing as spre
import sortingview as sv
import sortingview.views as vv
from sortingview.SpikeSortingView import SpikeSortingView


def main():
    collection_name = 'spikeforest'
    study_name = 'paired_boyden32c'
    recording_name = '1103_1_1'
    sorting_name = 'mountainsort4'
    github_issue_url = 'https://github.com/scratchrealm/community-sorting-curations/issues/2'

    instructions = f'''
Thank you for curating this dataset. Please mark all good units with the "accept" label and
merge any units that you determine belong to the same neuron. Once you have completed
the curation, save a snapshot, copy the sha1:// URI and then
[submit it as a comment on this GitHub issue]({github_issue_url}). 
'''

    dirname = f'datasets/{collection_name}/{study_name}/{recording_name}'
    sorting_dirname = f'{dirname}/sortings/{sorting_name}'

    with open(f'{dirname}/recording.json', 'r') as f:
        recording_object = json.load(f)
    with open(f'{sorting_dirname}/sorting.json', 'r') as f:
        sorting_object = json.load(f)

    recording = sv.load_recording_extractor(recording_object)
    sorting = sv.load_sorting_extractor(sorting_object)

    view = _create_view(R=recording, S=sorting, instructions=instructions)

    label = f'{collection_name}.{study_name}.{recording_name}.{sorting_name}'
    url = view.url(label=label)
    with open(f'{sorting_dirname}/figurl.url', 'w') as f:
        f.write(url)
    with open(f'{sorting_dirname}/figurl.md', 'w') as f:
        f.write(f'''
## {label}

[Follow this link to start curation]({url})
''')
    print(url)

def _create_view(*, R: si.BaseRecording, S: si.BaseSorting, instructions: str):
    print("Preparing spikesortingview data")
    X = SpikeSortingView.create(
        recording=R,
        sorting=S,
        segment_duration_sec=60 * 20,
        snippet_len=(20, 20),
        max_num_snippets_per_segment=100,
        channel_neighborhood_size=7,
        bandpass_filter=True,
        use_cache=True
    )
    # create a fake unit similiarity matrix (for future reference)
    # similarity_scores = []
    # for u1 in X.unit_ids:
    #     for u2 in X.unit_ids:
    #         similarity_scores.append(
    #             vv.UnitSimilarityScore(
    #                 unit_id1=u1,
    #                 unit_id2=u2,
    #                 similarity=similarity_matrix[(X.unit_ids==u1),(X.unit_ids==u2)]
    #             )
    #         )
    # Create the similarity matrix view
    # unit_similarity_matrix_view = vv.UnitSimilarityMatrix(
    #    unit_ids=X.unit_ids,
    #    similarity_scores=similarity_scores
    #    )

    print('Preparing views')
    # Assemble the views in a layout
    # You can replace this with other layouts
    raster_plot_subsample_max_firing_rate=50
    spike_amplitudes_subsample_max_firing_rate=50

    v_ut = X.units_table_view(unit_ids=X.unit_ids)
    v_ac = X.autocorrelograms_view(unit_ids=X.unit_ids)
    v_cc = X.cross_correlograms_view(unit_ids=X.unit_ids)
    v_aw = X.average_waveforms_view(unit_ids=X.unit_ids)
    v_sa = X.spike_amplitudes_view(
        unit_ids=X.unit_ids,
        _subsample_max_firing_rate=spike_amplitudes_subsample_max_firing_rate,
    )
    v_rp = X.raster_plot_view(
        unit_ids=X.unit_ids,
        _subsample_max_firing_rate=raster_plot_subsample_max_firing_rate,
    )
    v_curation = vv.SortingCuration2()

    v_tab0 = vv.Markdown(instructions)
    v_tab1 = vv.Splitter(
        direction='vertical',
        item1=vv.LayoutItem(v_ac),
        item2=vv.LayoutItem(v_aw)
    )
    v_tab2 = vv.Splitter(
        direction='vertical',
        item1=vv.LayoutItem(v_rp),
        item2=vv.LayoutItem(v_sa)
    )
    v_tab3 = vv.Box(
        direction='horizontal',
        items=[vv.LayoutItem(v_cc)]
    )
    v_left = vv.Splitter(
        direction='vertical',
        item1=vv.LayoutItem(v_ut),
        item2=vv.LayoutItem(v_curation)
    )
    view = (
        vv.Splitter(
            direction='horizontal',
            item1=vv.LayoutItem(
                view=v_left,
                max_size=300
            ),
            item2=vv.LayoutItem(
                view=vv.TabLayout(
                    items=[
                        vv.TabLayoutItem(
                            label='Instructions',
                            view=v_tab0
                        ),
                        vv.TabLayoutItem(
                            label='AC & AW',
                            view=v_tab1
                        ),
                        vv.TabLayoutItem(
                            label='RP & SA',
                            view=v_tab2
                        ),
                        vv.TabLayoutItem(
                            label='CC',
                            view=v_tab3
                        )
                    ]
                )
            )
        )
    )
    return view

if __name__ == '__main__':
    main()