import re
import random
from math import sqrt
from collections import Counter, defaultdict


def pearson(v1, v2):
    sum1, sum2 = sum(v1), sum(v2)
    sum1sq, sum2sq = sum(pow(v, 2) for v in v1), sum(pow(v, 2) for v in v2)
    psum = sum(v[0] * v[1] for v in zip(v1, v2))
    num = psum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1sq - pow(sum1, 2) / len(v1)) * (sum2sq - pow(sum2, 2) / len(v1)))
    if den == 0:
        return 0
    return 1 - num / den


def get_xiami_likes():
    pattern = re.compile('"?(.*?)"?,' * 3 + '(\d)')
    cnt = 0
    for line in open('target.csv', 'r'):
        likes = pattern.findall(line)
        if not likes:
            continue
        cnt += 1
        if cnt == 10000:
            break
        yield likes[0]


def count_likes(likes):
    records = defaultdict(lambda: defaultdict(int))
    artists = defaultdict(int)
    artists2cal = []
    likes_len = 0
    for like in likes:
        account = like[0]
        artist = like[1]
        song_name = like[2]
        song_rank = int(like[3])
        records[account][artist] += 1
        artists[artist] += 1
        likes_len += 1
    for artist, cnt in artists.items():
        frac = float(cnt) * 100000 / likes_len
        if frac < 60:
            continue
        artists2cal.append(artist)
    return artists2cal, records


def kcluster(artists2cal, records, distance=pearson, k=5):
    ranges = [(min(records[record][artist] for record in records),
               max(records[record][artist] for record in records)) for artist in artists2cal]
    clusters = [tuple(random.random() * (max_val - min_val) + min_val for min_val, max_val in ranges) for cycle in range(k)]
    lastmatches = None
    for i in range(100):
        bestmatches = defaultdict(lambda: [])
        for record in records:
            nearly_d = 2
            bestmatch = None
            for cluster in clusters:
                d = distance([records[record][artist] for artist in artists2cal], cluster)
                if d < nearly_d:
                    bestmatch = cluster
                    nearly_d = d
            bestmatches[bestmatch].append(record)

        if lastmatches == bestmatches:
            break
        lastmatches = bestmatches

        for i, cluster in enumerate(clusters):
            avgs = [0.0, ] * len(artists2cal)
            if len(bestmatches[cluster]) > 0:
                avg_cluster = tuple(sum(
                    records[record][artist] for record in bestmatches[cluster]) / len(bestmatches[cluster]) for artist in artists2cal)
                clusters[i] = avg_cluster
    return bestmatches


if __name__ == '__main__':
    artists2cal, _records = count_likes(get_xiami_likes())
    print (sorted(artists2cal))
    for cluster, records in kcluster(artists2cal, _records).items():
        print (sorted(records))
