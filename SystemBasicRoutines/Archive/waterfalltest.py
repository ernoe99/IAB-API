import plotly.graph_objects as go
import packaging

fig = go.Figure(go.Waterfall(
    name="20", orientation="v",
    measure=["relative", "relative", "relative", "relative", "relative", "total"],
    x=["Sales", "Consulting", "Net revenue", "Purchases", "Other expenses", "Profit before tax"],
    textposition="outside",
    text=["+60", "+80", "", "-40", "-20", "Total"],
    y=[60, 80, 0, -40, -20, 0],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
))

fig.update_layout(
    title="Profit and loss statement 2018",
    showlegend=True
)

fig.show()

fig = go.Figure()

fig.add_trace(go.Waterfall(
    x=[["2016", "2017", "2017", "2017", "2017", "2018", "2018", "2018", "2018"],
       ["initial", "q1", "q2", "q3", "total", "q1", "q2", "q3", "total"]],
    # measure=["absolute", "relative", "relative", "relative", "total", "relative", "relative", "relative", "total"],
    y=[1, 2, 3, -1, None, 1, 2, -4, None],
    base=1000
))

fig.add_trace(go.Waterfall(
    x=[["2016", "2017", "2017", "2017", "2017", "2018", "2018", "2018", "2018"],
       ["initial", "q1", "q2", "q3", "total", "q1", "q2", "q3", "total"]],
    measure=["absolute", "relative", "relative", "relative", "total", "relative", "relative", "relative", "total"],
    y=[1.1, 2.2, 3.3, -1.1, None, 1.1, 2.2, -4.4, None],
    base=1000
))

fig.update_layout(
    waterfallgroupgap=0.5,
)

fig.show()
