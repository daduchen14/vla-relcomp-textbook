#!/usr/bin/env python3
"""把极小 BDDL S-expression 解析成嵌套列表。"""

from collections import deque


def parse_one(tokens: deque[str]):
    token = tokens.popleft()
    if token != "(":
        return token
    result = []
    while tokens and tokens[0] != ")":
        result.append(parse_one(tokens))
    if not tokens:
        raise ValueError("缺少右括号")
    tokens.popleft()
    return result


def parse(text: str):
    spaced = text.replace("(", " ( ").replace(")", " ) ")
    tokens = deque(spaced.split())
    expression = parse_one(tokens)
    if tokens:
        raise ValueError("顶层表达式之后仍有 token")
    return expression


if __name__ == "__main__":
    sample = "(:goal (And (On tomato_2 porcelain_bowl_1)))"
    tree = parse(sample)
    predicate = tree[1][1]
    print("tree", tree)
    print("relation", predicate[0])
    print("target", predicate[1])
    print("reference", predicate[2])
