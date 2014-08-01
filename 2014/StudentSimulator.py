import subprocess
import pandas as pd
import re
import argparse
import sys
import numpy as np
import math

kc_stats = {'max': 2.46, 'avg': 0.7062, 'min': -0.473, 'sd': 1.0539, 'N': 5}
ex_diff = [2.46, 1.147, 0.633, -0.236, -0.473]
#print kc_stats
ex = []
for i in range(kc_stats["N"]):
    ex.append(pd.Series({"exercise_id": i, "irtDiff": ex_diff[i]}))
               # "irtDiff": np.random.normal(loc=kc_stats['avg'], 
               #                             scale=kc_stats['sd'])})
ex = sorted(ex, key=lambda x: x['irtDiff'])
ex_r = list(ex)
ex_r.reverse()
# print ex
# print ex_r
exercises = pd.DataFrame(ex)
exercises_r = pd.DataFrame(ex_r)
# print exercises
# print exercises_r
var = kc_stats['N']/(kc_stats['N']-1) * (
    np.power(exercises['irtDiff'],2).mean() - exercises['irtDiff'].mean()**2)
kc_stats = {'max': exercises['irtDiff'].max(),
            'avg': exercises['irtDiff'].mean(),
            'min': exercises['irtDiff'].min(),
            'sd' : math.sqrt(var),
            'N' : len(exercises['irtDiff'])}
#print exercises
#print exercises_r
#print kc_stats

sys.path.append('/home/uande18/code/adaptivelearningservice')
import als.da_irt.irtRecomendations as rec
from als.da_irt.skillProbability import studentSkill

parser = argparse.ArgumentParser(description='simulate some students')
parser.add_argument('mults', nargs='*', type=float)
parser.add_argument('--minErr', type=float, default=0.0)
args = parser.parse_args()

errs = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]
#errs = [0.0]
trialsPerErr = 100
student_resp = lambda e: int(np.random.random() + 1 - e)

recommender = rec.Recommendations()
minErr = args.minErr*kc_stats['sd']

output_fields = ['errRate', 'minErr', 'mastered',
          'prob', 'tries', 'skill', 'skill_err']
out_str = ','.join(['{' + key + '}' for key in output_fields])
output = { key : None for key in output_fields }

for im in args.mults:
    output_file = open('studentSimulator_mult{0}_min{1:.2f}.csv'.format(im,
                                                                    minErr),
                       'w')
    output_file.write(','.join([x for x in output_fields]) + '\n')
    print 'beginning {0:.1f} ...'.format(im)
    for err in errs:
        print 'running err: {0:.2f}'.format(err),
        output['errRate'] = err
        output['minErr'] = minErr
        for i in range(trialsPerErr):
            st = studentSkill(-1, kc_stats['avg']-kc_stats['sd'],
                              kc_stats['sd']*im)
            first_item = recommender.firstItemLogic(
                ex, kc_stats)
            first_ans = student_resp(err)

            st.updateSkillProbability(first_ans, first_item.irtDiff)
            st.theta_err = max(st.theta_err, minErr)
            mastery = recommender.kcPrediction.predictFromStats(st, kc_stats)

            tries = 0

            while (mastery[0] == False) and (tries < 100):
                next_item = recommender.nextItemLogic(ex_r, st)
                next_ans = student_resp(err)
                st.updateSkillProbability(next_ans, next_item.irtDiff)
                st.theta_err = max(st.theta_err, minErr)
                mastery = recommender.kcPrediction.predictFromStats(st,
                                                                    kc_stats)
                tries += 1

            output['mastered'] = mastery[0]
            output['prob'] = mastery[1]
            output['tries'] = tries
            output['skill'] = st.theta
            output['skill_err'] = st.theta_err

            # print out_str.format(**output)

            output_file.write(out_str.format(**output) + '\n')
            if i%10 == 0:
                print '.',
                sys.stdout.flush()
        print 'finished'
    print 'finished {0:.1f}'.format(im)
            
    output_file.close()
            
            
