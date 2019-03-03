import plotly.graph_objs as go

def multi_axes(df, columns, main_col=None):
    if main_col is not None:
        assert(main_col in df.columns)
        if main_col not in columns:
            columns.insert(0, main_col)
        else:
            a = columns.index(main_col)
            columns[0],columns[a] = columns[a], columns[0]
    
    data = []
    layout = go.Layout(
        title='bit',
        width=800
    )
    
    xaxis = df.index
    anchor = "x1"
    if len(columns) > 2:
        anchor = "free"
    
    ycount = 0
    for col in columns:
        ycount += 1
        wid = 1
        if ycount == 1:
            wid = 2
        data.append(
            go.Scatter(
                x = xaxis,
                y = df[col],
                name = col,
                xaxis = "x1",
                yaxis = "y" + str(ycount),
                line = dict(
                    width = wid,
                )
            )
        )

    off = 0
    yinc = 0.05
    while ycount > 1:
        layout.update({
            "yaxis"+str(ycount):{
                "anchor" : anchor,
                "overlaying": "y1",
                "side": "right",
                "position": 0.75+ off*yinc
            }
        })
        off += 1.0
        ycount -= 1
        
    return data, layout
