import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from modules.utils import haversineDistance, models2Array, models2df, mergeDF, modelDict

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from .alert import send_alert

FIRST_MATCH_RATE = float(os.getenv('FIRST_MATCH_RATE'))
SECOND_MATCH_RATE = float(os.getenv('SECOND_MATCH_RATE'))
OTHER_MATCH_RATE = float(os.getenv('OTHER_MATCH_RATE'))

FIRST_SUGGEST_DISTANCE = float(os.getenv('FIRST_SUGGEST_DISTANCE'))
SECOND_SUGGEST_DISTANCE = float(os.getenv('SECOND_SUGGEST_DISTANCE'))
THIRD_SUGGEST_DISTANCE = float(os.getenv('THIRD_SUGGEST_DISTANCE'))
FOURTH_SUGGEST_DISTANCE = float(os.getenv('FOURTH_SUGGEST_DISTANCE'))
OTHER_SUGGEST_DISTANCE = float(os.getenv('OTHER_SUGGEST_DISTANCE'))

async def suggestion(altered_posts: list[str], is_lost=True):
  SessionLocal = mysql_db.initDB()
  db: Session = SessionLocal()
  try:
    post_df = models2df(mysql_crud.post.search(db, mysql_model.Post(valid=True)))
    tag_matches_df = models2df(mysql_crud.tag_match.all(db))
    
    post_df = post_df[post_df['id'].isin(altered_posts)]
    tag_matches_df = mergeDF([tag_matches_df, post_df[['id', 'coordinates', 'is_lost', 'match_rank']]], on_list=[('post_id', 'id')], drop_list=['id'])
    
    lost_tags = tag_matches_df[tag_matches_df['is_lost'] == True].groupby('post_id').agg({'tag_name': list, 
                                                                                          'coordinates': lambda x: x.iloc[0], 
                                                                                          'match_rank': lambda x: x.iloc[0]}).reset_index()
    found_tags = tag_matches_df[tag_matches_df['is_lost'] == False].groupby('post_id').agg({'tag_name': list, 
                                                                                            'coordinates': lambda x: x.iloc[0]}).reset_index()
    if is_lost:
      lost_tags = lost_tags[lost_tags['post_id'].isin(altered_posts)]
    else:
      found_tags = found_tags[found_tags['post_id'].isin(altered_posts)]
    
    if lost_tags.empty or found_tags.empty:
      return
    
    def calculate_match_rate(lost_tags, found_tags):
      matched_tags = [tag for tag in lost_tags if tag in found_tags]
      match_rate = len(matched_tags) / len(found_tags) if found_tags else 0
      return match_rate
    
    def match_rate_condition(match_rank):
      if match_rank // 2 == 0:
        return FIRST_MATCH_RATE
      elif match_rank // 2 == 1:
        return SECOND_MATCH_RATE
      else:
        return OTHER_MATCH_RATE
      
    def match_distance(match_rank):
      if (match_rank-1) // 2 == 0:
        return FIRST_SUGGEST_DISTANCE
      elif (match_rank-1) // 2 == 1:
        return SECOND_SUGGEST_DISTANCE
      elif (match_rank-1) // 2 == 2:
        return THIRD_SUGGEST_DISTANCE
      elif (match_rank-1) // 2 == 3:
        return FOURTH_SUGGEST_DISTANCE
      else:
        return OTHER_SUGGEST_DISTANCE
    
    score_df = pd.merge(lost_tags, found_tags, how='cross', suffixes=('_lost', '_found'))
    score_df.drop(score_df[
      score_df.apply(lambda row: haversineDistance(row['coordinates_lost'], row['coordinates_found']) > match_distance(row['match_rank']), axis=1)
    ].index, inplace=True)
    
    score_df['match_rate'] = score_df.apply(lambda row: calculate_match_rate(row['tag_name_lost'], row['tag_name_found']), axis=1)
    score_df.drop(score_df[
      score_df.apply(lambda row: row['match_rate'] < match_rate_condition(row['match_rank']), axis=1)
    ].index, inplace=True)
    
    # alert user
    target_df = score_df[['post_id_lost']]
    receivers = {}
    for _, row in target_df.iterrows():
      post = mysql_crud.post.get(db, row)
      user = mysql_crud.user.get(db, mysql_model.User(id=post.user_id))
      if user and user.email:
        if user.id not in receivers:
          receivers[user.id] = (user, [])
        
        receivers[user.id][1].append((post.id, post.title, post.update_time if post.update_time else post.create_time))
    
    for _, (user, posts) in receivers.items():
      for post in posts:
        send_alert(user.email, user.nickname, post)
    
  finally:
    db.close()
