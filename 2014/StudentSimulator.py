import subprocess
import pandas as pd
import re
import argparse
import sys
import numpy as np
import math

kc_stats = {'max': 2.46, 'avg': 0.7062, 'min': -0.473, 'sd': 1.1783, 'N': 5}
ex_diff = [2.46, 1.147, 0.633, -0.236, -0.473]
print kc_stats
ex = []
for i in range(kc_stats["N"]*10):
    ex.append(pd.Series({"exercise_id": i, 
                         #"irtDiff": ex_diff[i]}))
                         "irtDiff": np.random.normal(loc=kc_stats['avg'], 
                                                     scale=kc_stats['sd'])}))
ex = pd.DataFrame(ex)
exercises = ex.sort('irtDiff')
# exercises_r = ex.sort('irtDiff', ascending=False)
print exercises
# print exercises_r
kc_stats = {'max': exercises['irtDiff'].max(),
            'avg': exercises['irtDiff'].mean(),
            'min': exercises['irtDiff'].min(),
            'sd' : exercises['irtDiff'].std(ddof=1),
            'N' : len(exercises['irtDiff'])}
#print exercises
#print exercises_r
print kc_stats
print "starting diff:",kc_stats['avg']-kc_stats['sd']

sys.path.append('/home/uande18/code/adaptivelearningservice')
import als.da_irt.irtRecommendations as rec
from als.da_irt.skillProbability import studentSkill

parser = argparse.ArgumentParser(description='simulate some students')
parser.add_argument('mults', nargs='*', type=float)
parser.add_argument('--minErr', nargs='*', type=float, default=[0.0])
parser.add_argument('--errs', nargs='*', type=float, 
                    default = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5])
parser.add_argument('--N', type=int, default = 1)
args = parser.parse_args()

errs = args.errs
trialsPerErr = args.N
student_resp = lambda e: int(np.random.random() + 1 - e)

recommender = rec.Recommendations()
# minErr = args.minErr*kc_stats['sd']

output_fields = ['errRate', 'initialErr', 'minErr', 'mastered',
          'prob', 'tries', 'skill', 'skill_err']
out_str = ','.join(['{' + key + '}' for key in output_fields])
output = { key : None for key in output_fields }

for em in args.minErr:
    minErr = em*kc_stats['sd']
    print "minErr mult: {0:.2f} ...".format(em)
    for im in args.mults:
        if im < em:
            continue
        output_file = open('studentSimulator_mult{0:.1f}_min{1:.2f}.csv'.\
                           format(im, em), 'w')
        output_file.write(','.join([x for x in output_fields]) + '\n')
        print 'beginning initial err mult: {0:.1f} ...'.format(im)
        for err in errs:
            print 'running err: {0:.2f}'.format(err),
            output['errRate'] = err
            output['minErr'] = minErr
            output['initialErr'] = ks_stats['sd']*im
            for i in range(trialsPerErr):
                st = studentSkill(-1, kc_stats['avg']-kc_stats['sd'],
                                  kc_stats['sd']*im)
                first_item = recommender.firstItemLogic(
                    exercises, kc_stats)
                # print "first_item:",first_item
                first_ans = student_resp(err)

                st.updateSkillProbability(first_ans, first_item.irtDiff)
                st.theta_err = max(st.theta_err, minErr)
                mastery = recommender.kcPrediction.predictFromStats(st, kc_stats)

                tries = 0

                while (mastery[0] == False) and (tries < 100):
                    next_item = recommender.nextItemLogic(exercises, st)
                    next_ans = student_resp(err)
                    try:
                        st.updateSkillProbability(next_ans, next_item.irtDiff)
                    except AttributeError:
                        # print "easier items not found"
                        break
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


