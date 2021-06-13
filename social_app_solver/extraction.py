import os
import shutil
import json
import pandas as pd
import datetime
import sys


def extract_fb_data(folder=None):
    if folder == None:
        folder = "/Users/murtazavahanvaty/OneDrive - Cornerstone Capabilities/Personal/social-app/facebook-vahanvaty"
    subfolders = [f.path for f in os.scandir(folder) if f.is_dir()]
    fb_data={}
    for sub in subfolders:
        len_folder_string = 99
        fb_data[f"{sub[len_folder_string:]}"] = {}
        if 'messages' in sub:
            sub_subfolders = [f.path for f in os.scandir(sub) if f.is_dir()]
            for ssub in sub_subfolders:
                fb_data[f"{sub[len_folder_string:]}"][f"{ssub[len_folder_string+9:]}"] = {}
                try:
                    for f in os.listdir(ssub): 
                        if f == ".ipynb_checkpoints":
                            continue
                        with open(f'{ssub}/{f}') as file:
                            data = json.load(file)
                            length = +len(sub[len_folder_string:])
                            fb_data[f"{sub[len_folder_string:]}"][f"{ssub[len_folder_string+9:]}"][f"{file.name[length:-5]}"] = data
                except (IsADirectoryError, UnicodeDecodeError) as e:
                    print(sub, ssub, f, e)
        else:
            try:
                for f in os.listdir(sub): 
            #         src = os.path.join(sub, f)
            #         dst = os.path.join(folder, f)
            #         shutil.move(src, dst)
                    if f == ".ipynb_checkpoints":
                        continue
                    try:
                        with open(f'{sub}/{f}') as file:
                            data = json.load(file)
                            length = len_folder_string+len(sub[len_folder_string:])+1
                            fb_data[f"{sub[len_folder_string:]}"][f"{file.name[length:-5]}"] = data
                    except IsADirectoryError as e:
                        print(sub, f, e)
            except (IsADirectoryError, ValueError) as e:  # includes simplejson.decoder.JSONDecodeError
                print(sub, f, e)
    
    return fb_data

def get_video_show_page_time_spent_df(fb_data):
    df = pd.json_normalize(fb_data["about_you"]["viewed"]['viewed_things'][0]['children'][0]['entries'])
    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))
    return df

def get_address_book_df(fb_data):
    df = pd.json_normalize(fb_data["about_you"]["your_address_books"]["address_book"]["address_book"])
    df['details'] = df["details"].apply(lambda x: x[0]['contact_point'])
    df['created_timestamp'] = df['created_timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%m/%d/%Y'))
    df['updated_timestamp'] = df['updated_timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%m/%d/%Y'))
    return df
    
def get_news_feed_posts_df(fb_data):
    df = pd.json_normalize(fb_data['about_you']['viewed']['viewed_things'][2]['entries'])
    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.date.fromtimestamp(x))
    df['name'] = df["data.name"].str.rstrip("'s post'")
    return df

def get_ad_interactions(fb_data):
    # return fb_data['ads_and_businesses']["advertisers_you've_interacted_with"]["history"]
    df = pd.json_normalize(fb_data['ads_and_businesses']["advertisers_you've_interacted_with"]["history"])
    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%m/%d/%Y'))
    return df

def get_ad_interests(fb_data):
    ad_interests = fb_data['ads_and_businesses']['ads_interests']["topics"]
    return ad_interests

def get_off_facebook_activity_df(fb_data):
    df = pd.json_normalize(fb_data['ads_and_businesses']['your_off-facebook_activity']['off_facebook_activity'])
    # df['timestamp'] = df['events'].apply(lambda x: x[''])
    # df['timestamp'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))
    return df

def get_top_friend_engagements(fb_data):
    # Filter comments for people engagements and rank
    pass