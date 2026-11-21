"""End-of-course mini-projects — one or two capstones per course.

Static catalogue. Learner submissions are stored in the ProjectSubmission table.
"""
from __future__ import annotations


def _mp(pid: str, title: str, brief: str, skills: list[str], est: str) -> dict:
    return {"id": pid, "title": title, "brief": brief, "skills": skills, "est": est}


PROJECTS: dict[str, list[dict]] = {
    "quantum": [
        _mp("q-teleport", "Build a Quantum Teleportation Demo",
            "Use the circuit builder to teleport a qubit state across three qubits, then explain each step with a measurement table.",
            ["entanglement", "measurement", "Bell states"], "2–3 hrs"),
        _mp("q-coin", "Quantum Coin-Flip Game",
            "Create a Hadamard-based fair coin and a biased-coin variant, and chart the measured distribution over 1000 shots.",
            ["superposition", "sampling"], "1–2 hrs"),
    ],
    "ml": [
        _mp("ml-classifier", "Train a Mini Image/Flower Classifier",
            "Train a small classifier on a toy dataset, tune two hyper-parameters, and report accuracy with a confusion matrix.",
            ["classification", "evaluation"], "3–4 hrs"),
        _mp("ml-regression", "Predict House Prices",
            "Fit a regression model, visualise the loss landscape, and explain which features matter most.",
            ["regression", "features"], "2–3 hrs"),
    ],
    "ds": [
        _mp("ds-dashboard", "Build a Data Story Dashboard",
            "Clean a small dataset, compute summary statistics, and present three insights with charts.",
            ["statistics", "visualisation"], "2–3 hrs"),
    ],
    "ai": [
        _mp("ai-solver", "Build a Maze-Solving Agent",
            "Implement BFS and A* on a grid maze and compare the paths and nodes expanded.",
            ["search", "heuristics"], "2–3 hrs"),
        _mp("ai-nqueens", "Solve N-Queens Visually",
            "Use backtracking to place N queens and animate the search tree.",
            ["backtracking"], "1–2 hrs"),
    ],
    "dsa": [
        _mp("dsa-visualizer", "Build Your Own Sorting Visualiser",
            "Animate three sorting algorithms side by side and chart comparisons vs swaps.",
            ["sorting", "complexity"], "2–3 hrs"),
        _mp("dsa-router", "Shortest-Path Route Finder",
            "Model a small map as a graph and find the shortest route with Dijkstra, explaining each relaxation.",
            ["graphs", "Dijkstra"], "3–4 hrs"),
    ],
    "cyber": [
        _mp("cy-cipher", "Break a Classical Cipher",
            "Implement a Caesar/Vigenère cracker using letter-frequency analysis and decode a given message.",
            ["ciphers", "frequency analysis"], "2–3 hrs"),
    ],
    "chain": [
        _mp("bc-ledger", "Build a Tiny Blockchain",
            "Create a chain of hashed blocks, add proof-of-work mining, and show how tampering breaks the chain.",
            ["hashing", "proof-of-work"], "3–4 hrs"),
    ],
    "dl": [
        _mp("dl-digits", "Train a Digit Recognizer",
            "Build a small neural network for handwritten digits, visualise the first-layer filters, and report accuracy.",
            ["neural networks", "convolutions"], "3–4 hrs"),
    ],
}


def for_course(course_id: str) -> list[dict]:
    return list(PROJECTS.get(course_id, []))


def find(project_id: str) -> tuple[str, dict] | tuple[None, None]:
    for cid, items in PROJECTS.items():
        for p in items:
            if p["id"] == project_id:
                return cid, p
    return None, None
