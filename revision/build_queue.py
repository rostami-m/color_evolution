"""Freeze all experiments before production. No data-driven stopping or gating."""
import argparse
from collections import Counter
from pathlib import Path
import sys
from .common import atomic_json
from .data import sha256


def build(project,output,seeds=30,include81=False,smoke=False,data_dir=None,backend="cpu"):
    project=Path(project).resolve();root=Path(output).resolve()
    if backend not in ('cpu','mps') or seeds < 1:
        raise ValueError('Require cpu/mps backend and at least one seed')
    if (root/'manifest.json').exists():
        raise FileExistsError('Run manifest already exists; choose a new output directory')
    python=sys.executable;data=str(Path(data_dir or project/'data').resolve())
    jobs=[];stagejobs={}
    def add(config):
        stage=config['stage']
        ident=f"{stage}_{config['condition']}_s{config.get('seed',0):02d}"
        config={**dict(n_train=4000,n_validation=800,n_test=1000,epochs=80,batch_size=128),**config,'id':ident,'training_device':'cpu' if config.get('kind')=='grounding' else backend}
        if smoke:config.update(n_train=64,n_validation=32,n_test=32,epochs=1,cma_iterations=2)
        path=root/'configs'/f'{ident}.json';atomic_json(path,config)
        dependencies=[] if config.get('synthetic') else ['prepare_data']
        jobs.append(dict(id=ident,command=[python,'-m','revision.experiments','--config',str(path),'--output',str(root),'--data-dir',data],
            depends_on=dependencies,metadata={k:config[k] for k in ('stage','condition','seed') if k in config}))
        stagejobs.setdefault(stage,[]).append(ident)
    # Download/import precedes natural jobs; explicit synthetic controls remain independent.
    jobs.append(dict(id='prepare_data',command=[python,'-m','revision.prepare_data','--data-dir',data],metadata=dict(stage='E0')))
    jobs.append(dict(id='E5g_daylight_limits',command=[python,'-m','revision.daylight_limits','--output',str(root)],metadata=dict(stage='E5g')))
    for seed in range(seeds):
        for size in (9,27):
            add(dict(stage='E0_synthetic',condition=f'p{size}',patch_size=size,synthetic=True,seed=seed,
                     probes=True,decode=seed<3))
    sizes=[9,27]+([81] if include81 else [])
    for size in sizes:
        arms=[('baseline' if size==9 else 'fixed',1,'iid')]
        if size>9:arms += [('dilated',size//9,'iid'),('coarse',1,'coarse')]
        for arm,dilation,noise in arms:
            for seed in range(seeds):
                add(dict(stage='E1',condition=f'p{size}_{arm}',patch_size=size,dilation=dilation,noise=noise,seed=seed,probes=True,decode=True))
    for context in ('intact','shuffle','boundary_shuffle'):
        for readout in ('base','center_only'):
            for seed in range(seeds):
                add(dict(stage='E2',condition=f'{context}_{readout}',patch_size=27,context=context,readout=readout,seed=seed,probes=True))
    for size in (9,27):
        for readout,b in [('fixed_b',0.),('fixed_b',.5),('fixed_b',1.),('learned_b',0.),('spatial',0.),('spatial_coarse',0.)]:
            for seed in range(seeds):
                add(dict(stage='E3',condition=f'p{size}_{readout}_{int(b*10)}',patch_size=size,readout=readout,b=b,seed=seed,
                         models=['untrained','classify','shuffled'],probes=True))
    # Loci fixed before results; natural coordinates use the historical raw-LMS BY scale.
    for locus in (-.2,0.,.2):
        for weighting in ('uniform','frequency','loss','both'):
            if weighting=='uniform' and locus!=0:continue
            for seed in range(seeds):
                add(dict(stage='E4',condition=f'{weighting}_locus{int(100*locus)+20}',patch_size=27,
                         weighting=weighting,utility_locus=locus,seed=seed,models=['classify'],probes=True))
    # Original analytic ecological formulas, accurately labeled synthetic proxies.
    from .ecological_proxies import ecological_reflectances,by_coord
    for name,spectrum in ecological_reflectances().items():
        for seed in range(seeds):
            add(dict(stage='E4_proxy',condition=f'{name}_synthetic_proxy',patch_size=27,weighting='loss',
                utility_locus=by_coord(spectrum),proxy_spectrum=spectrum.tolist(),proxy_measured=False,seed=seed,models=['classify'],probes=True))
    for size in (9,27):
        for k in (4,8,16,32):
            for b in (2,4,8):
                if k==8 and b==4:continue # base checkpoint already included in E1
                for seed in range(seeds):
                    add(dict(stage='E5a',condition=f'p{size}_k{k}_b{b}',patch_size=size,k1=k,bottleneck=b,seed=seed,models=['classify','regress','untrained','shuffled']))
    perturbations=[('cct_broad',dict(cct_range=[2500,30000])),('cct_narrow',dict(cct_range=[5000,8000])),
        ('cones_shift_pos',dict(cone_shift=10)),('cones_shift_neg',dict(cone_shift=-10)),('cones_wide',dict(cone_width=1.3)),
        ('refl_noise_hi',dict(reflectance_noise=.05)),('refl_noise_vhi',dict(reflectance_noise=.08)),
        ('surround_neutral',dict(surround_mode='neutral')),('surround_highchroma',dict(surround_mode='highchroma')),
        ('sensor_noise_hi',dict(sensor_noise=.04))]
    for size in (9,27):
        for name,kw in perturbations:
            for seed in range(seeds):
                add(dict(stage='E5b',condition=f'p{size}_{name}',patch_size=size,seed=seed,models=['classify','regress'],**kw))
    for size in (9,27):
        for seed in range(seeds):
            add(dict(stage='E5c',condition=f'p{size}_optimizer',patch_size=size,seed=seed,n_train=1500,
                     models=['classify','cma'],cma_iterations=300))
    add(dict(stage='E5f',condition='natural_spatial_statistics',kind='grounding',patch_size=27))
    for stage,dependencies in stagejobs.items():
        if stage in ('E5a','E5b'):
            dependencies=dependencies+stagejobs['E1']
        if stage=='E5b':
            dependencies=dependencies+stagejobs['E0_synthetic']
        jobs.append(dict(id=f'analyze_{stage}',command=[python,'-m','revision.aggregate','--output',str(root),'--stage',stage],depends_on=dependencies,allow_failed_dependencies=True))
    # Each stage produces its findings before the queue advances to the next.
    ordered=[j for j in jobs if j['id'] in ('prepare_data','E5g_daylight_limits')]
    by_id={j['id']:j for j in jobs}
    for stage,identifiers in stagejobs.items():
        ordered.extend(by_id[i] for i in identifiers)
        ordered.append(by_id[f'analyze_{stage}'])
    jobs=ordered
    atomic_json(root/'manifest.json',jobs)
    atomic_json(root/'source_hashes.json',{str(p.relative_to(project)):sha256(p) for folder in ('revision',) for p in sorted((project/folder).rglob('*.py'))})
    atomic_json(root/'design.json',dict(training_backend=backend,analysis_backend='cpu',smoke=smoke,seeds=seeds,include81=include81,jobs=len(jobs),stage_counts=dict(Counter(j.get('metadata',{}).get('stage','analysis') for j in jobs)),
        primary_endpoint='Per-network fraction above matched initialization threshold',
        primary_comparison='E1: change in classifier-minus-regressor opponent fraction from p9 baseline to p27 fixed kernel, paired by seed',
        secondary_endpoints=['Normalized chromatic power','Continuous double-opponency score','Task performance on its own scale','Signed local and pooled probe effects'],
        limits=dict(cpu_cores=1.5,compute_threads=2,concurrent_workers=1,worker_memory_gib=4),
        notes=['E5d decoding and E5e cardinal axes reuse E1 checkpoints.',
               'Base architecture/standard rendering reuse E1; synthetic rendering uses E0_synthetic.',
               'E5g: no original Dress image/calibration or measured-daylight protocol recovered; empirical Dress claim remains unresolved. No fabricated reproduction.',
               '81 included only if explicitly selected after resource pilot; selection is independent of scientific results.',
               'Primary n=30 is a fixed budget and does not establish statistical power.'],
        scope='All runnable experiments from the revision plan; unsupported Dress interpretation requires narrowing or a separate specified protocol.'))
    print(len(jobs),'jobs frozen at',root,flush=True)
    return jobs


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--output',required=True)
    p.add_argument('--data-dir');p.add_argument('--backend',choices=['cpu','mps'],default='cpu');p.add_argument('--seeds',type=int,default=30);p.add_argument('--include81',action='store_true');p.add_argument('--smoke',action='store_true')
    a=p.parse_args();build(a.project,a.output,a.seeds,a.include81,a.smoke,a.data_dir,a.backend)
