from typing import List


def print_decorator(func):
    def run_deco(*args, **kwargs):
        result = func(*args, **kwargs)
        print(result)
        return result
    return run_deco


nums = list(map(lambda x: int(x), open('nums.txt').read().split()))
print(nums, sum(nums), len(nums))
