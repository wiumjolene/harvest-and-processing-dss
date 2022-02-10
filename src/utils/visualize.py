import plotly.graph_objects as go
import plotly.offline as offline
import plotly.express as px
import os


class Visualize:
    def scatter_plot(self, x_series, y_series, names, 
                        filename_html, offline_plot=True,
                        ):
        fig=go.Figure(data=go.Scatter(x=x_series,
                        y=y_series,
                        mode='markers',
                        marker=dict(size=16),
                        #legendgroup=legend,
                        #color=legend,
                        text=names))
        
        if offline_plot:
            offline.plot(fig, filename=filename_html)

        else:
            fig.show()
       
        return 


    def scatter_plot2(self, df, filename, colour, title):

        repdir=os.path.join('reports','figures')

        if not os.path.exists(repdir):
            os.makedirs(repdir)

        filename_html=os.path.join(repdir,f"genetic_algorithm_{filename}.html")

        if 'indiv_id' in df.columns:
            # Check if not tests use actual data
            df=df.rename(columns={"obj1": "km.kg", "obj2": "total_dev"})
            fig = px.scatter(df, x="km.kg", y="total_dev", color=colour,
                            hover_data=['indiv_id'], title=title)

        else:
            # Check if tests use obj1 and obj2
            fig = px.scatter(df, x="obj1", y="obj2", color=colour,
                            hover_data=['id'], title=title)

        fig.update_traces(marker=dict(size=16))

        fig.show()
        fig.write_html(filename)
       
        return 