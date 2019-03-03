import pandas as pd
import plotly.graph_objs as go

def size_dist(bins:"bins", 
              dx:"domain x", dy:"domain y"):
    green5 = [
            "#edf8fb",
            "#b2e2e2",
            "#66c2a4",
            "#2ca25f",
            "#006d2c"
            ]
    red5 = [
            "#fee5d9",
            "#fcae91",
            "#fb6a4a",
            "#de2d26",
            "#a50f15"
            ]
    bb = [ 
            bins['buy'].sum(),
            bins['buy_1'].sum(),
            bins['buy_5'].sum(),
            bins['buy_25'].sum(),
            bins['buy_50'].sum()
    ]
    ss = [ 
            abs(bins['sell'].sum()),
            abs(bins['sell_1'].sum()),
            abs(bins['sell_5'].sum()),
            abs(bins['sell_25'].sum()),
            abs(bins['sell_50'].sum())
    ]

    b, s = [] , []
    for i in range(len(bb)-1):
        b.append(bb[i] - bb[i+1])
        s.append(ss[i] - ss[i+1])
    b.append(bb[-1])
    s.append(ss[-1])
    
    b.reverse()
    green5.reverse()
    
    return go.Pie(
        values = b+s,
        sort=False,
        direction="clockwise",
        title = dict(
            text='Trade Size Dist.',
            position='bottom center'
        ),
        textinfo="none",
        hoverinfo="label+value",
        labels=[
            "Buy size > 50 XBT",
            "Buy size > 25 XBT",
            "Buy size > 5 XBT",
            "Buy size > 1 XBT",
            "Buy size > 0 XBT",
            "Sell size > 0 XBT",
            "Sell size > 1 XBT",
            "Sell size > 5 XBT",
            "Sell size > 25 50 XBT",
            "Sell size > 50 XBT"
        ],
        domain = {
            'x':dx,
            'y':dy
        },
        marker=dict(colors=green5+red5)
    ), bb[0], ss[0]


def buy_n_sell(level:"Trade size range", bins:"df", 
            dx:"domain x", dy:"domain y"):
    suf= ["0","1","5","25","50"]
    if level >= len(suf) or level < 0:
        raise ("Fasle level")
    
    left = suf[level]
    right = suf[level]
    vol_sell, vol_buy = None, None
    
    if level == (len(suf) - 1):
        vol_sell = abs(bins['sell_'+left])
        vol_buy = bins['buy_'+left]
    else:
        right = suf[level+1]
        vol_sell = abs(bins['sell_'+left] - bins['sell_'+right])
        vol_buy = bins['buy_'+left] - bins['buy_'+right]

    return go.Pie(
        labels = ['sell', 'buy'],
        values = [vol_sell, vol_buy],
        title = dict(
            text="["+left+", "+right+")",
            position='bottom center'
        ),
        textinfo="none",
        domain = {
            'x':dx,
            'y':dy
        },
        marker=dict(colors=colors)  
    )