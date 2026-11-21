"""LeetCode Connect — curated practice problems linked to each course.

A static, offline catalogue of real LeetCode problems. The frontend links out to
leetcode.com; solved marks are tracked per learner in the PracticeSolved table.
"""
from __future__ import annotations

_URL = "https://leetcode.com/problems/"


def _p(slug: str, title: str, difficulty: str, topic: str) -> dict:
    return {"slug": slug, "title": title, "difficulty": difficulty, "topic": topic, "url": _URL + slug + "/"}


PROBLEMS: dict[str, list[dict]] = {
    "dsa": [
        _p("two-sum", "Two Sum", "Easy", "arrays"),
        _p("best-time-to-buy-and-sell-stock", "Best Time to Buy and Sell Stock", "Easy", "arrays"),
        _p("valid-parentheses", "Valid Parentheses", "Easy", "stacks"),
        _p("merge-two-sorted-lists", "Merge Two Sorted Lists", "Easy", "linked-lists"),
        _p("binary-search", "Binary Search", "Easy", "searching"),
        _p("maximum-subarray", "Maximum Subarray", "Medium", "arrays"),
        _p("product-of-array-except-self", "Product of Array Except Self", "Medium", "arrays"),
        _p("3sum", "3Sum", "Medium", "arrays"),
        _p("group-anagrams", "Group Anagrams", "Medium", "hashing"),
        _p("number-of-islands", "Number of Islands", "Medium", "graphs"),
        _p("course-schedule", "Course Schedule", "Medium", "graphs"),
        _p("climbing-stairs", "Climbing Stairs", "Easy", "dynamic-programming"),
        _p("coin-change", "Coin Change", "Medium", "dynamic-programming"),
        _p("longest-increasing-subsequence", "Longest Increasing Subsequence", "Medium", "dynamic-programming"),
        _p("invert-binary-tree", "Invert Binary Tree", "Easy", "trees"),
        _p("validate-binary-search-tree", "Validate Binary Search Tree", "Medium", "trees"),
        _p("kth-smallest-element-in-a-bst", "Kth Smallest Element in a BST", "Medium", "trees"),
        _p("word-search", "Word Search", "Medium", "recursion"),
    ],
    "cyber": [
        _p("number-of-1-bits", "Number of 1 Bits", "Easy", "bit-manipulation"),
        _p("single-number", "Single Number", "Easy", "bit-manipulation"),
        _p("counting-bits", "Counting Bits", "Easy", "bit-manipulation"),
        _p("reverse-bits", "Reverse Bits", "Easy", "bit-manipulation"),
        _p("sum-of-two-integers", "Sum of Two Integers", "Medium", "bit-manipulation"),
    ],
    "ml": [
        _p("convert-binary-number-in-a-linked-list-to-integer", "Binary Linked List to Integer", "Easy", "basics"),
        _p("running-sum-of-1d-array", "Running Sum of 1d Array", "Easy", "arrays"),
        _p("find-pivot-index", "Find Pivot Index", "Easy", "arrays"),
        _p("matrix-diagonal-sum", "Matrix Diagonal Sum", "Easy", "matrices"),
    ],
    "ds": [
        _p("mean-of-array-after-removing-some-elements", "Mean After Removing Elements", "Easy", "statistics"),
        _p("running-sum-of-1d-array", "Running Sum of 1d Array", "Easy", "arrays"),
        _p("find-the-highest-altitude", "Find the Highest Altitude", "Easy", "prefix-sums"),
    ],
    "ai": [
        _p("maze-ii", "The Maze II", "Medium", "search"),
        _p("shortest-path-in-binary-matrix", "Shortest Path in Binary Matrix", "Medium", "search"),
        _p("word-ladder", "Word Ladder", "Hard", "search"),
    ],
    "chain": [
        _p("design-hashmap", "Design HashMap", "Easy", "hashing"),
        _p("find-the-duplicate-number", "Find the Duplicate Number", "Medium", "hashing"),
    ],
    "dl": [
        _p("matrix-block-sum", "Matrix Block Sum", "Medium", "matrices"),
        _p("convolution", "Image Smoother", "Easy", "matrices"),
    ],
    "quantum": [
        _p("number-complement", "Number Complement", "Easy", "bit-manipulation"),
        _p("hamming-distance", "Hamming Distance", "Easy", "bit-manipulation"),
    ],
}


def for_course(course_id: str) -> list[dict]:
    return list(PROBLEMS.get(course_id, []))


def all_slugs() -> set[str]:
    return {p["slug"] for ps in PROBLEMS.values() for p in ps}
