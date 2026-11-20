"""Summarize NS-2 old wired trace format for packets reaching node 2."""
import argparse
import json
import statistics
from pathlib import Path


def analyze(path, destination='2'):
    sent, received = {}, {}
    for line in Path(path).read_text().splitlines():
        parts = line.split()
        if len(parts) < 12 or parts[4] != 'cbr':
            continue
        event, when, source, target = parts[:4]
        packet_id = parts[11]
        if event == '+' and source == '0':
            sent.setdefault(packet_id, (float(when), int(parts[5])))
        if event == 'r' and target == destination:
            received.setdefault(packet_id, (float(when), int(parts[5])))
    arrivals = sorted(received.values())
    delays = [(received[k][0]-v[0])*1000 for k, v in sent.items() if k in received]
    interval = max(.001, arrivals[-1][0]-arrivals[0][0]) if arrivals else 1
    differences = [abs(delays[i]-delays[i-1]) for i in range(1, len(delays))]
    return dict(sent=len(sent), received=len(received),
                loss_pct=round(100*(len(sent)-len(received))/max(1, len(sent)), 3),
                mean_delay_ms=round(statistics.mean(delays), 3) if delays else None,
                mean_delay_variation_ms=round(statistics.mean(differences), 3) if differences else 0,
                throughput_mbps=round(sum(x[1] for x in arrivals)*8/interval/1e6, 3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace')
    args = parser.parse_args()
    print(json.dumps(analyze(args.trace), indent=2))
