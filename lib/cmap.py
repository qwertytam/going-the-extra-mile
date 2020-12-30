# -*- coding: utf-8 -*-
"""Colour Map


"""

import pandas as pd
import seaborn as sns
from matplotlib import colors as clrs

n_markers = 256
palette = sns.color_palette(palette="coolwarm", n_colors=n_markers)
palette = [clrs.to_hex(p) for p in palette]
palette = pd.DataFrame(palette)
palette.to_csv('cmaps.csv', index=False, header=False)
