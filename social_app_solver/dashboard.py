import streamlit as st
import os
st. set_page_config(layout="wide")
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
from simpletransformers.classification import ClassificationModel
from social_app_solver.extraction import *

st.title('My Facebook Data')
dir_path = os.getcwd()
# Move extraction to the home page where you can upload data file or use login to access saved file
fb_data = extract_fb_data()
classification_categories = pd.read_csv(f'{dir_path}/classification_categories.csv', index_col=0)

# run classifier
model = ClassificationModel("bert", f"{dir_path}/outputs", use_cuda=False)
# save file for future


def display_news_feed_posts_data(fb_data):
    chart_data = get_news_feed_posts_df(fb_data)
    count = chart_data.groupby('timestamp').agg('count')
    st.line_chart(count)
    post_predictions, post_raw_outputs = model.predict(chart_data['name'].to_list())
    chart_data['primary_category_cat'] = post_predictions
    chart_data = chart_data.merge(classification_categories, on='primary_category_cat', how='left')
    posts = chart_data.groupby('primary_category').agg('count').reset_index()
    fig = px.pie(posts, values=posts.timestamp, names=posts.primary_category, color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig)

    st.write('Lets check out your facebook newsfeed activity')
        
    option_data = st.date_input(
    'Chose a date to filter',
    value = [chart_data['timestamp'].min(),chart_data['timestamp'].max()])

    option_category = st.multiselect('See posts from a particular category', options = chart_data['primary_category'].unique())
    option_page = st.multiselect('See posts from a particular person/page', options = chart_data['name'].unique())


    st.title(f"Between {option_data[0].strftime('%m/%d/%Y')} & {option_data[1].strftime('%m/%d/%Y')} your newsfeed showed you these posts")
    if (len(option_page) == 0) & (len(option_category) == 0):
        filtered_df = chart_data[(chart_data.timestamp >= option_data[0]) & (chart_data.timestamp <= option_data[1])]
    elif (len(option_category) == 0):
        filtered_df = chart_data[(chart_data.timestamp >= option_data[0]) & (chart_data.timestamp <= option_data[1]) & (chart_data.name.isin(option_page))]
    elif (len(option_page) == 0):
        filtered_df = chart_data[(chart_data.timestamp >= option_data[0]) & (chart_data.timestamp <= option_data[1]) & (chart_data.primary_category.isin(option_category))]
    else:
        filtered_df = chart_data[(chart_data.timestamp >= option_data[0]) & (chart_data.timestamp <= option_data[1]) & (chart_data.primary_category.isin(option_category)) & (chart_data.primary_category_cat.isin(option_category))]
    fig = go.Figure(data=[go.Table(
    header=dict(values=list(["Date","Post name", "URL"]),fill_color='paleturquoise',align='center', font_size=20),
    cells=dict(values=[filtered_df.timestamp, filtered_df.name, filtered_df["data.uri"]],fill_color='lavender',align=['center' ,'center', 'left'], font_size=20, height=30))], layout=go.Layout(
        title=go.layout.Title(text="These are the posts you saw in your newsfeed")
    ))
    fig.update_layout(width=1500, height=650)
    st.write(fig)
        

def display_address_book(fb_data):
    # https://plotly.com/python/table/
    df = get_address_book_df(fb_data)
    fig = go.Figure(data=[go.Table(
    header=dict(values=list(["Name","Details"]),fill_color='paleturquoise',align='center', font_size=20),
    cells=dict(values=[df.name, df.details],fill_color='lavender',align='center', font_size=20, height=30))], layout=go.Layout(
        title=go.layout.Title(text="Information about your friends and family in facebook")
    ))
    fig.update_layout(width=1500, height=650)

    st.write(fig)

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)
query_params = st.experimental_get_query_params()
tabs = ["Home", "News Feed Posts", "Address Book"]
if "tab" in query_params:
    active_tab = query_params["tab"][0]
else:
    active_tab = "Home"

if active_tab not in tabs:
    st.experimental_set_query_params(tab="Home")
    active_tab = "Home"

li_items = "".join(
    f"""
    <li class="nav-item">
        <a class="nav-link{' active' if t==active_tab else ''}" href="/?tab={t}">{t}</a>
    </li>
    """
    for t in tabs
)
tabs_html = f"""
    <ul class="nav nav-tabs">
    {li_items}
    </ul>
"""

st.markdown(tabs_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if active_tab == "Home":
    st.write("Welcome to my lovely page!")
    st.write("Feel free to sample what kind of data Facebook collects about you")
    st.write("Here's a video of how you can download data off Facebook")
    st.video('https://youtu.be/FVsvrFAWDTM')
    
elif active_tab == "News Feed Posts":
    display_news_feed_posts_data(fb_data)
elif active_tab == "Address Book":
    display_address_book(fb_data)
else:
    st.error("Something has gone terribly wrong.")


# import altair as alt

# from urllib.error import URLError

# @st.cache
# def get_UN_data():
#     AWS_BUCKET_URL = "https://streamlit-demo-data.s3-us-west-2.amazonaws.com"
#     df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
#     return df.set_index("Region")

# try:
#     df = get_UN_data()
#     countries = st.multiselect(
#         "Choose countries", list(df.index), ["China", "United States of America"]
#     )
#     if not countries:
#         st.error("Please select at least one country.")
#     else:
#         data = df.loc[countries]
#         data /= 1000000.0
#         st.write("### Gross Agricultural Production ($B)", data.sort_index())

#         data = data.T.reset_index()
#         data = pd.melt(data, id_vars=["index"]).rename(
#             columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
#         )
#         chart = (
#             alt.Chart(data)
#             .mark_area(opacity=0.3)
#             .encode(
#                 x="year:T",
#                 y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
#                 color="Region:N",
#             )
#         )
#         st.altair_chart(chart, use_container_width=True)
# except URLError as e:
#     st.error(
#         """
#         **This demo requires internet access.**

#         Connection error: %s
#     """
#         % e.reason
#     )