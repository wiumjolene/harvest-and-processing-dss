import plotly.graph_objects as go
#import plotly.offline as offline


class Visualize:
    def scatter_plot(self,x_series, y_series):
        fig=go.Figure(data=go.Scatter(x=x_series,y=y_series,mode='markers'))
        fig.update_traces(marker=dict(size=16))
        fig.show()
        return fig
