#importing required libyary start
from datetime import datetime as dt
from operator import index
from tkinter.messagebox import NO

import dash
from matplotlib.pyplot import gray
import pandas as pd
import plotly.express as px
import yfinance as yf
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
# model
from model import prediction
#importing required libyary end

def get_stock_price_fig(df):
    fig = px.line(df, x="Date", y=["Close", "Open"],
                  title="Closing and Opening Price vs Date")
    return fig


def get_more(df):
    df["EWA_20"] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df, x="Date", y="EWA_20",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode="lines+markers")
    return fig

#declaring dash app and adding stylesheet to application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'StockFlix'
server = app.server

#Navigation css
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "5rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",

}

#styling css for tabs
tab_selected_style = {
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px',
    'border-radius': '15px',
}
tabs_styles = {
    'height': '44px',
    'align-items': 'center'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'background':  '# 242134',
    'background': '-webkit-linear-gradient(to right,  # 9E9AB4, #242134)',
    'background': 'linear-gradient(to right,  # 9E9AB4, #242134)'

}

#Ploty Logo
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

# navigation search bar HTML code 
search_bar = dbc.Row(
    [
        dbc.Col(dcc.Input(type="text", id="dropdown_tickers", placeholder="Search")),
        dbc.Col(
            html.Button(
                "Search", className="btn btn-outline-primary filteBTN", n_clicks=0, id="submit"
            ),
            width="auto",
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

#Navigation html
sidebar = html.Div(
    [

        dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        # Use row and col to control vertical alignment of logo / brand
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(src=PLOTLY_LOGO, height="30px")),
                                dbc.Col(dbc.NavbarBrand(
                                    "StockFlix", className="ms-2")),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        style={"textDecoration": "none"},
                    ),
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                    dbc.Collapse(
                        search_bar,
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                    ),
                ]
            ),
            color="dark",
            dark=True,
        )
        # html.H2("StocyFy", className="display-4"),
        # html.Hr(),
        # html.P(
        #     "Enter Stock Name", className="lead"
        # ),
        # dbc.Nav(
        #     [
        #         # dbc.Input("Home", href="/", active="exact"),
        #         dbc.Input(id="dropdown_tickers", placeholder="Type something...", type="text"),
        #         dbc.Button("Search", outline=True, href="/page-1", color="success", id='submit', className="me-1"),
        #         dbc.NavLink("Stock Price", href="/page-2", active="exact", id="stock"),
        #         dbc.NavLink("Indicators", href="/page-3", active="exact", id="indicators"),
        #         dbc.NavLink("Forecast", href="/page-4", active="exact", id="forecast"),
        #     ],
        #     vertical=True,
        #     pills=True,
        # ),
    ],
    # style=SIDEBAR_STYLE,
)

#jumbotron for date range picker html code start here
jumbotron = html.Div(
    dbc.Container(
        [
            html.Div([
                html.H4("Start Date",  className="label label-default m-2"),
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=dt(1995, 8, 5),
                    max_date_allowed=dt.now(),
                    initial_visible_month=dt.now().date(),
                ),

                html.H4("End Date", className="label label-default m-2"),
                dcc.DatePickerSingle(
                    id='my-date-picker-single1',
                    min_date_allowed=dt(1995, 8, 5),
                    max_date_allowed=dt.now(),
                    initial_visible_month=dt.now().date(),
                ),

                html.Button(
                    "Stock Price",  className="btn btn-info BTNstyle", n_clicks=0, id="stock"
                ),
                html.Button(
                    "Indicators", className="btn btn-warning BTNstyle", id="indicators"),

            ], className="date d-flex justify-content-center"),

            html.Hr(className="my-2"),

        ],
        fluid=True,
        className="py-3",
    ),
    className=" jumbotron p-3 rounded-3 jumbotron",
)
#jumbotron for date range picker html code end here

#jumbotron for prediction tab htmlm start here
jumbotron1 = html.Div(
    dbc.Container(
        [      # forcast button and input for number of days
            html.Div([
                dbc.Input(id="n_days", type="text", value = '',
                          placeholder="number of days"),
                html.Button("Forecast", className="btn btn-info BTNstyle",
                            id="forecast")
            ], className="d-flex justify-content-center"),

            html.Hr(className="my-2"),

            #slider HTML 
            html.Div(
                dcc.Slider(0, 50, step=None, marks=None,
                tooltip={"placement": "bottom", "always_visible": True},
                value=0, id="days", updatemode='drag')
            )

        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 jumbotron rounded-3",
)
#jumbotron for prediction tab html end here

# main page content html start here
content = html.Div(id="page-content", children=[
    dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='Stock Details', value='tab-1-example-graph', selected_style=tab_selected_style, style=tab_style,
                children=[
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Img(id="logo"),  #stock company logo
                                    html.P(id="ticker"),
                                ], className="header"
                            ),
                            html.Div(id="description",  # searched stock code description
                                     className="description_ticker"),
                            
                        ], className="content contentStyle"
                    )
                ]),

        dcc.Tab(label='Stock Price', value='tab-2-example-graph', selected_style=tab_selected_style, style=tab_style,
                children=[
                    jumbotron,
                    html.Div([], id="graphs-content"),  #stock price graph content
                    html.Div([], id="main-content")]  #indicator graph content
                ),
        dcc.Tab(label='Stock Prediction', value='tab-3-example-graph', selected_style=tab_selected_style, style=tab_style,
                children=[
                    jumbotron1,
                    html.Div([], id="forecast-content")  # prediction graph content
                ]
                ),
    ], ),
], style=CONTENT_STYLE)
# main page content html end here

#application layout and main body
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    sidebar,
    content
], className='body')


#callback start here

#stock code search callback start here
@ app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
], [
    Input("submit", "n_clicks")
], [
    State("dropdown_tickers", "value")
])
def update_data(n, val):
    if n is None:
        return "Hey there! Please enter a legitimate stock code to get details.", \
               None, None, None, None, None
    if val is None:
        return "Hey there! Please enter a legitimate stock code to get details.", \
               "https://thumbs.dreamstime.com/z/stock-market-vector-forex-symbol-bull-growing-white-background-eps-177327586.jpg", \
               "StockFlix", None, None, None

    ticker = yf.Ticker(val)
    inf = ticker.info
    df = pd.DataFrame().from_dict(inf, orient="index").T
    # df[["logo_url", "shortName", "longBusinessSummary"]]
    # , df['shortName'].values[0], None, None, None
    return df["longBusinessSummary"].values[0], df['logo_url'].values[0], df['shortName'].values[0], None, None, None

#stock code search callback end here

#stock price callback start here

@ app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input("my-date-picker-single", "date"),
    Input("my-date-picker-single1", "date"),
], [
    State("dropdown_tickers", "value")
])
def stock_price(n, start_date, end_date, val):
    if n is None:
        return [""]
    elif val is None:
        raise PreventUpdate
    elif start_date is not None:
        df = yf.download(val, str(start_date), str(end_date))
    else:
        df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]
#stock price callback end here

#stock indicator callback start here
@ app.callback([
    Output("main-content", "children")
], [
    Input("indicators", "n_clicks"),
    Input("my-date-picker-single", "date"),
    Input("my-date-picker-single1", "date"),
], [
    State("dropdown_tickers", "value")
])
def indicators(n, start_date, end_date, val):
    if n is None or val is None:
        return [""]
    if start_date is None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]
#stock indicator callback ends here


#stock prediction callback start here
@ app.callback([
    Output("forecast-content", "children")
], [
    Input("forecast", "n_clicks"),
], [
    State("n_days", "value"),
    State("days", "value"),
    State("dropdown_tickers", "value")
])
def forecast(n, days, n_days, val):
    if days is '':
        days = None

    if days is not None:
       n_days = days

    if n is None:
        return [""]
    if val is None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)  #calling stock prediction model
    return [dcc.Graph(figure=fig)]           #returnig predition to graph

#stock prediction callback ends here

#callback end here

if __name__ == "__main__":
    app.run_server(debug=False)


# view =  html.Div(
#     [
#         html.Div(
#             [
#                 html.P("Welcome to the Stock Dash App!", className="start"),
#                 html.Div([
#                     html.P("Input stock code: "),
#                     html.Div([
#                         dcc.Input(id="dropdown_tickers", type="text"),
#                         html.Button("Submit", id="submit"),
#                     ], className="form")
#                 ], className="input-place"),
#                 html.Div([
#                     dcc.DatePickerRange(id="my-date-picker-range",
#                                         min_date_allowed=dt(1995, 8, 5),
#                                         max_date_allowed=dt.now(),
#                                         initial_visible_month=dt.now().date()),
#                 ], className="date"),
#                 html.Div([
#                     html.Button("Stock Price",
#                                 className="stock-btn", id="stock"),
#                     html.Button(
#                         "Indicators", className="indicators-btn", id="indicators"),
#                     dcc.Input(id="n_days", type="text",
#                               placeholder="number of days"),
#                     html.Button("Forecast", className="forecast-btn",
#                                 id="forecast")
#                 ], className="buttons"),
#             ], className="nav"
#         ),
#         html.Div(
#             [
#                 html.Div(
#                     [
#                         html.Img(id="logo"),
#                         html.P(id="ticker"),
#                     ], className="header"
#                 ),
#                 html.Div(id="description", className="description_ticker"),
#                 html.Div([], id="graphs-content"),
#                 html.Div([], id="main-content"),
#                 html.Div([], id="forecast-content")
#             ], className="content"
#         ),
#     ], className="container"
# )


# PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
# app = dash.Dash(
#     __name__,
#     external_stylesheets=[
#       #   "https://fonts.googleapis.com/css2?family=Roboto&display=swap"
#     ]
# )

