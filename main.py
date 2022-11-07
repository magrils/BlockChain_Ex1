import requests
import numpy as np
import sys

parm = {'calls': 0}


def print_block(block):
    print(f"getting block -")
    print(
        # f"\nhash:{block['hash']}\n"
        f"height:{block['height']}\n"
        f"time:{block['time']}\n"
        # f"prev_block:{block['prev_block']}\n"
        # f"next_block:{block['next_block']}\n"
        # f"block_index:{block['block_index']}\n"
    )


def get_block(height: int, count_call=True):
    if count_call:
        parm['calls'] += 1


    # api-endpoint
    URL = f"https://blockchain.info/block-height/{height}"

    # format given here
    my_format = "json"

    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'format': my_format}

    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=PARAMS)

    # extracting data in json format
    data = r.json()

    blocks = data["blocks"]
    if len(blocks) > 0:
        block = blocks[0]
        # print_block(block)
    else:
        print(f"the requested block [{height}] is unavailable")

    return blocks[0] if len(blocks) > 0 else None


def get_latest_block():
    parm['calls'] += 1


    # api-endpoint
    URL = f"https://blockchain.info/latestblock"

    # format given here
    my_format = "json"

    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'format': my_format}

    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=PARAMS)

    # extracting data in json format
    data = r.json()

    height = data["height"]
    time = data["time"]
    # print(f"getting latest block")
    # print(f"height: {height}, time: {time}")
    return {'height': height, 'time': time}


def bisect(lo, hi, target: int):
    output = lo - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        block = get_block(mid)
        block_height = block["height"]
        block_time = block["time"]

        if block_time >= target:
            hi = mid - 1
        else:
            output = block_height
            lo = mid + 1

    return output


def find_boundaries(diff: int, target_time: int, MAX_ITER: int, max_height: int):
    block = get_block(diff)
    # lower bound for search
    lo_time = block["time"]
    lo_height = diff
    # upper bound for search
    hi_time = block["time"]
    hi_height = diff

    # try and decrement lower boundary by factors of Diff
    i = MAX_ITER
    while i > 0 and lo_time > target_time:
        i -= 1
        lo_height -= diff // MAX_ITER
        lo_time = get_block(lo_height)["time"]

    # try and increment higher boundary by factors of Diff
    i = MAX_ITER
    while i > 0 and hi_time < target_time and hi_height < max_height:
        i -= 1
        hi_height = min(max_height, hi_height + (diff // MAX_ITER))
        hi_time = get_block(hi_height)["time"]

    # if time at boundary is not small enough - set it to 0
    if lo_time > target_time:
        lo_height = 0
    # if time at boundary is not large enough - set it to height of latest block
    if hi_time < target_time:
        hi_height = max_height

    return lo_height, hi_height


def find_block_prior_to(timestamp: int, diff_type="fixed"):
    GENESIS_TIME = 1231006505
    MAX_ITER = 3
    if timestamp <= GENESIS_TIME:
        return "there are no blocks prior to the Genesis Block"
    latest_block = get_latest_block()
    if timestamp > latest_block["time"]:
        return f"as of now, the latest block prior to time:{timestamp}" \
               f"\nis block of height: {latest_block['height']}"

    # general fixed estimate number of blocks between genesis-block and desired block
    fixed_avg = 600  # 10 Minutes
    fixed_diff = (timestamp - GENESIS_TIME) // fixed_avg


    # current live estimate number of blocks between genesis-block and desired block
    curr_avg = (latest_block["time"] - GENESIS_TIME) // latest_block["height"]
    curr_diff = (timestamp - GENESIS_TIME) // curr_avg


    diff = fixed_diff if diff_type == "fixed" else fixed_avg
    lo, hi = find_boundaries(diff, timestamp, MAX_ITER, latest_block["height"])
    height = bisect(lo, hi, timestamp)

    return f"The latest block prior to time:{timestamp}" \
           f"\nis block of height: {height}"


def tests():
    max_height = 762153
    max_time = 1667842321
    size = 50
    counters = {"fixed_avg":0, "curr_avg":0, "bisect":0}
    failed_samples = []
    samples = np.random.randint(max_height+1, size= size)
    i = 0
    try:
        for sample in samples:

            block = get_block(sample,count_call=False)
            timestamp = block["time"]
            timestamp += 1


            height = find_block_prior_to(timestamp)
            if height != sample:
                failed_samples.append(sample)
            counters["fixed_avg"] += parm['calls']
            parm['calls'] = 0

            height = find_block_prior_to(timestamp, diff_type="curr")
            if height != sample:
                failed_samples.append(sample)
            counters["curr_avg"] += parm['calls']
            parm['calls'] = 0


            height = bisect(0, max_height, timestamp)
            if height != sample:
                failed_samples.append(sample)
            counters["bisect"] += parm['calls']
            parm['calls'] = 0

            i += 1
            print(i)

        print(f"\nstats:")
        print(f"fixed avg- calls: {counters['fixed_avg']},\tcalls/sample: {counters['fixed_avg']/size}")
        print(f"curr avg- calls: {counters['curr_avg']},\tcalls/sample: {counters['curr_avg']/size}")
        print(f"bisect- calls: {counters['bisect']},\tcalls/sample: {counters['bisect']/size}")
        print(f"\nfails: {failed_samples}")


    except Exception as e:
        print(e)
        print(f"call counts: {counters}")
        print(f"failed samples: {failed_samples}")


if __name__ == '__main__':
    timestamp = int(sys.argv[1])
    ans = find_block_prior_to(timestamp)
    print(ans)


