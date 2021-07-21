# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 17:02:57 2021

@author: Zach

Document containing the different board themes for the chess progrum.

The colors are structured in this order:

    light square
    dark square
    light square highlight
    dark square highlight
    light square last move highlight
    dark square last move highlight

"""

# TODO:  Add more themes for custom board colors.
themes = dict(
    blue = (
        (214, 221, 229),
        (82, 133, 180),
        (253, 187, 115),
        (255, 129, 45),
        (116, 194, 229),
        (32, 154, 215),
    ),

    bw = (
        (255, 255, 255),
        (100, 100, 100),
        (140, 236, 146),
        (30, 183, 37),
        (116, 194, 229),
        (32, 154, 215),
    ),

    yellow = (
        (247, 241, 142),
        (244, 215, 4),
        (253, 187, 115),
        (255, 129, 45),
        (116, 194, 229),
        (32, 154, 215),
    ),
)
