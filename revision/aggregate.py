"""Network-level summaries and paired comparisons; preserve all failures."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
from .analysis import bootstrap
from .common import atomic_json


def aggregate(root,stage):
    root=Path(root)
    if stage=='E5f':
        paths=list((root/'jobs').glob('E5f_*/grounding.json'))
        destination=root/'analysis';destination.mkdir(exist_ok=True)
        if not paths:
            atomic_json(destination/'E5f.json',dict(status='missing',reason='Spatial-grounding worker did not produce results'))
            (destination/'E5f_Findings.md').write_text('# Natural-scene statistics\n\nNo result was produced. Inspect the worker failure; no environmental claim is verified.\n')
            return
        record=json.loads(paths[0].read_text())
        atomic_json(destination/'E5f.json',record)
        lines=['# Natural-scene statistics','', 'Statistics are observational and measured in pixels. Confidence intervals resample scenes, not individual pixels.',
               '', '| Separation (pixels) | Intact-versus-shuffled MSE improvement [95% CI] |','|---:|---|']
        for d,summary in record['summaries'].items():
            s=summary['mse_improvement'];lines.append(f"| {d} | {s['mean']} {s['ci95']} |")
        lines+=['','These correlations describe the measured scenes. Uniform two-surface training does not reproduce them, so they cannot establish its learning mechanism.','']
        (destination/'E5f_Findings.md').write_text('\n'.join(lines))
        return
    groups=defaultdict(list); paired=defaultdict(dict);missing=[]
    for configpath in sorted((root/'configs').glob('*.json')):
        config=json.loads(configpath.read_text())
        extra_base=stage in ('E5a','E5b') and config.get('stage')=='E1' and config['condition'] in ('p9_baseline','p27_fixed')
        extra_synthetic=stage=='E5b' and config.get('stage')=='E0_synthetic'
        if (config.get('stage')!=stage and not extra_base and not extra_synthetic) or config.get('kind')=='grounding':
            continue
        job=root/'jobs'/config['id']
        for mode in config.get('models',['untrained','classify','regress','shuffled']):
            path=job/f'{mode}.json'
            if not path.exists():
                missing.append(dict(id=config['id'],mode=mode));continue
            row=json.loads(path.read_text())
            condition=config['condition']+('_synthetic' if extra_synthetic else '')
            groups[(condition,mode)].append(row)
            paired[(condition,config['seed'])][mode]=row
    summaries=[];comparisons=[]
    metrics=('normalized_chromatic_power','double_opponency_score','double_opponent_fraction')
    for (condition,mode),rows in groups.items():
        result=dict(condition=condition,mode=mode,n_networks=len(rows),
                    metrics={m:bootstrap([r['metrics'][m] for r in rows]) for m in metrics},
                    validation_pass_count=sum(r['validation_gate'] is True for r in rows))
        result['performance']={key:bootstrap([r['performance']['test'].get(key) for r in rows])
            for key in ('accuracy','balanced_accuracy','r2','rmse_kelvin')}
        result['validation_gated_metrics']={m:bootstrap([r['metrics'][m] for r in rows if r['validation_gate'] is True]) for m in metrics}
        effects=[]
        for r in rows:
            illusion=r.get('illusions',{}).get('axes',{})
            if not illusion:continue
            for axis,record in illusion.items():
                for probe in record['simultaneous']:
                    effects.append(dict(seed=r['seed'],axis=axis,contrast=probe['surround_contrast'],shift=probe['readout_shift']))
        result['signed_simultaneous_raw']=effects
        probe_values=defaultdict(list)
        for row in rows:
            for axis,probes in row.get('illusions',{}).get('axes',{}).items():
                for probe in probes['simultaneous']:
                    for field in ('readout_shift','local_target_shift','local_interior_shift'):
                        probe_values[f'{axis}/simultaneous/{probe["surround_contrast"]}/{field}'].append(probe[field])
                for probe in probes['checkerboard']:
                    for field in ('readout_shift','local_target_shift'):
                        probe_values[f'{axis}/checker/{probe["cell_pixels"]}/{probe["phase"]}/{field}'].append(probe[field])
                for probe in probes['cornsweet']:
                    probe_values[f'{axis}/cornsweet/{probe["polarity"]}/distant_signed_difference'].append(probe['distant_signed_difference'])
                    probe_values[f'{axis}/cornsweet/{probe["polarity"]}/near_signed_difference'].append(probe['near_signed_difference'])
                for probe in probes['mach']:
                    for field in ('low_join_signed_residual','high_join_signed_residual'):
                        probe_values[f'{axis}/mach/{probe["control"]}/{field}'].append(probe[field])
                for control,probe in probes['watercolor'].items():
                    for field in ('near_contour_shift','far_interior_shift'):
                        probe_values[f'{axis}/watercolor/{control}/{field}'].append(probe[field])
            for point in row.get('sensitivity',{}).get('rows',[]):
                probe_values[f'sensitivity/{point["target_contrast"]}'].append(point['normalized_sensitivity'])
        result['probe_summaries']={key:bootstrap(values) for key,values in probe_values.items()}
        summaries.append(result)
    for condition in sorted(set(k[0] for k in paired)):
        blocks=[v for (c,s),v in paired.items() if c==condition and 'classify' in v and 'regress' in v]
        if not blocks:continue
        diffs=[b['classify']['metrics']['double_opponent_fraction']-b['regress']['metrics']['double_opponent_fraction'] for b in blocks]
        nonzero=[x for x in diffs if x!=0]
        p=binomtest(sum(x>0 for x in nonzero),len(nonzero),.5).pvalue if nonzero else 1.
        comparisons.append(dict(condition=condition,comparison='classifier minus regressor opponent fraction',
            summary=bootstrap(diffs),differences=diffs,sign_test_two_sided_p=p))
    if stage=='E1':
        interaction=[];seed_ids=[]
        for (condition,seed),small in paired.items():
            large=paired.get(('p27_fixed',seed),{})
            if condition!='p9_baseline' or not all(m in small and m in large for m in ('classify','regress')):
                continue
            gap=lambda block:block['classify']['metrics']['double_opponent_fraction']-block['regress']['metrics']['double_opponent_fraction']
            interaction.append(gap(large)-gap(small));seed_ids.append(seed)
        nonzero=[x for x in interaction if x!=0]
        comparisons.append(dict(condition='PRIMARY_scale_by_objective',
            comparison='(classifier minus regressor fraction at 27 fixed) minus (classifier minus regressor fraction at 9 baseline)',
            summary=bootstrap(interaction),differences=interaction,paired_seeds=seed_ids,
            sign_test_two_sided_p=binomtest(sum(x>0 for x in nonzero),len(nonzero),.5).pvalue if nonzero else 1.))
    # Holm adjustment within this declared stage family; no filter-level p-values.
    order=np.argsort([r['sign_test_two_sided_p'] for r in comparisons])
    maximum=0.
    for rank,index in enumerate(order):
        maximum=max(maximum,(len(order)-rank)*comparisons[index]['sign_test_two_sided_p'])
        comparisons[index]['holm_p']=min(1.,maximum)
    # Between-configuration scale/context/utility comparisons are paired by seed.
    cross=[]
    for mode in sorted(set(k[1] for k in groups)):
        conditions=sorted(c for c,m in groups if m==mode)
        if not conditions:continue
        reference=next((c for c in conditions if 'baseline' in c),conditions[0])
        ref={r['seed']:r for r in groups[(reference,mode)]}
        for condition in conditions:
            if condition==reference:continue
            rows={r['seed']:r for r in groups[(condition,mode)]}
            common=sorted(ref.keys() & rows.keys())
            cross.append(dict(mode=mode,reference=reference,condition=condition,paired_seeds=common,
                metrics={metric:bootstrap([rows[s]['metrics'][metric]-ref[s]['metrics'][metric] for s in common]) for metric in metrics},
                interpretation='Exploratory paired contrasts; reference chosen by declared baseline when present'))
    training_backends=sorted({r.get('training_device','cpu') for rows in groups.values() for r in rows if r['mode']!='untrained'})
    if len(training_backends)>1:raise ValueError('Refusing unstratified mixed-backend comparison')
    artifact=dict(stage=stage,groups=summaries,objective_comparisons=comparisons,training_backends=training_backends,analysis_backend='cpu',
        cross_condition_comparisons=cross,missing=missing,inference_unit='paired network seed',
        caveats=['Thirty seeds are a fixed planning budget, not a power guarantee.',
                 'Bootstrap intervals are descriptive; no equivalence margin was defined.',
                 'Source-scene generalization is limited by the eight-scene dataset.',
                 'Failed or low-performing seeds are retained in the primary analysis.'])
    destination=root/'analysis';destination.mkdir(exist_ok=True)
    atomic_json(destination/f'{stage}.json',artifact)
    lines=[f'# {stage} findings','',f'Analyzed {sum(len(v) for v in groups.values())} networks; {len(missing)} missing model records.',
        '', 'These are corrected reruns; they are not recovered historical results. All-seed summaries are primary.',
        '', '| Condition | Model | N | Opponent fraction mean [95% bootstrap CI] |', '|---|---|---:|---|']
    for group in summaries:
        s=group['metrics']['double_opponent_fraction']
        lines.append(f"| {group['condition']} | {group['mode']} | {group['n_networks']} | {s['mean']} {s['ci95']} |")
    lines+=['','Claim checks: classifier/regressor differences, failed convergence, and signed illusion controls must be reviewed before manuscript revision.',
        'Distant local filling-in is impossible for this strictly local architecture; global readout changes must be described separately.',
        'Analytic ecological spectra remain synthetic proxies; sensitivity is not a human JND.','']
    (destination/f'{stage}_Findings.md').write_text('\n'.join(lines))
    if summaries:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        selected=[g for g in summaries if g['mode'] in ('classify','regress','cma')]
        fig,ax=plt.subplots(figsize=(max(7,len(selected)*.3),4))
        for i,g in enumerate(selected):
            s=g['metrics']['double_opponent_fraction'];ci=s['ci95']
            ax.errorbar(i,s['mean'],yerr=None if ci is None else [[max(0,s['mean']-ci[0])],[max(0,ci[1]-s['mean'])]],fmt='o',color='C0' if g['mode']=='classify' else 'C1')
        ax.set_xticks(range(len(selected)),[f"{g['condition']}\n{g['mode']}" for g in selected],rotation=90)
        ax.set_ylabel('Fraction above matched initialization threshold')
        ax.set_title(f'{stage}: all seeds; descriptive 95% bootstrap intervals')
        fig.tight_layout();fig.savefig(destination/f'{stage}.pdf');plt.close(fig)
    print(stage,'analyzed',len(summaries),'groups;',len(missing),'missing',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--stage',required=True)
    a=p.parse_args();aggregate(a.output,a.stage)
