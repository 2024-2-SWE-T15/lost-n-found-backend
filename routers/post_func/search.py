import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fuzzywuzzy import fuzz, process

from fastapi import APIRouter, HTTPException, Depends, Query

from sqlalchemy.orm import Session

from modules.utils import haversineDistance, models2df, modelDict

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from ..dependencies import loadUser


load_dotenv("config/.env")

router = APIRouter(prefix='/search', tags=['Post-Search'])

@router.get('/')
async def searchPost(postSchemaSearch: mysql_schema.PostSchemaSearch = Query(None),
                     db: Session = Depends(mysql_db.getDB)):
  weights = [float(os.getenv('FIRST_WEIGHT')), 
             float(os.getenv('SECOND_WEIGHT')), 
             float(os.getenv('THIRD_WEIGHT'))]
  OTHER_WEIGHT = float(os.getenv('OTHER_WEIGHT'))
  
  if postSchemaSearch.coordinates ^ postSchemaSearch.distance:
    raise HTTPException(status_code=400, detail='Coordinates and distance must be provided together')
  
  post_df = models2df(mysql_crud.search.get(db, postSchemaSearch))
  tag_matches_df = models2df(mysql_crud.tag_match.all(db))


  if postSchemaSearch.coordinates and postSchemaSearch.distance:
    post_df = post_df[post_df.apply(
      lambda row: haversineDistance(row['coordinates'], postSchemaSearch.coordinates) <= postSchemaSearch.distance, axis=1
    )]
  
  if postSchemaSearch.query:
    title_score_df = pd.DataFrame(process.extract(postSchemaSearch.query, post_df['title'].tolist(), scorer=fuzz.partial_token_sort_ratio, limit=len(post_df)),
                                  columns=['title', 'title_score']).drop_duplicates()
    description_score_df = pd.DataFrame(process.extract(postSchemaSearch.query, post_df['description'].tolist(), scorer=fuzz.partial_token_sort_ratio, limit=len(post_df)),
                                        columns=['description', 'description_score']).drop_duplicates()
    tag_score_df = pd.DataFrame(mysql_crud.hashtag.fuzzyMatch(db, postSchemaSearch.query, excepts=postSchemaSearch.tags), columns=['tag_name', 'hashtag_score'])
    
    tag_matched_score_df = pd.merge(tag_matches_df, tag_score_df, on='tag_name')
    tag_matched_score_df['rank'] = tag_matched_score_df.groupby('post_id').cumcount()
    tag_matched_score_df['weighted_hashtag_score'] = tag_matched_score_df.apply(
      lambda row: row['hashtag_score'] * weights[row['rank']] if row['rank'] < len(weights) else row['hashtag_score'] * OTHER_WEIGHT, axis=1
    )
    final_tag_matched_score_df = tag_matched_score_df.groupby('post_id')['weighted_hashtag_score'].sum().reset_index()
  
  if postSchemaSearch.tags:
    hit_tag_matches_df = tag_matches_df.copy()
    hit_tag_matches_df.drop(hit_tag_matches_df[hit_tag_matches_df.apply(
      lambda row: True if not row['tag_name'] in postSchemaSearch.tags else False, axis=1
    )].index, inplace=True)
    hit_tag_matches_df['rank'] = hit_tag_matches_df.groupby('post_id').cumcount()
    hit_tag_matches_df['hit_score'] = hit_tag_matches_df.apply(
      lambda row: 100 * weights[row['rank']] if row['rank'] < len(weights) else 100 * OTHER_WEIGHT, axis=1
    )
    final_hit_tag_matches_df = hit_tag_matches_df.groupby('post_id')['hit_score'].sum().reset_index()
  
  
  post_data_df = post_df
  if postSchemaSearch.query:
    post_data_df = post_data_df.merge(title_score_df, on='title').merge(description_score_df, on='description').merge(final_tag_matched_score_df, left_on='id', right_on='post_id').drop(columns='post_id')
  
  if postSchemaSearch.tags:
    post_data_df = post_data_df.merge(final_hit_tag_matches_df, left_on='id', right_on='post_id').drop(columns='post_id')
  
  
  post_data_df['total_score'] =(post_data_df['title_score']**2 * float(os.getenv('TITLE_WEIGHT')) + \
                                post_data_df['description_score']**2 * float(os.getenv('DESCRIPTION_WEIGHT')) + \
                                post_data_df['weighted_hashtag_score']**2 * float(os.getenv('TAG_WEIGHT'))) if postSchemaSearch.query else 0  + \
                                post_data_df['hit_score']**2 * float(os.getenv('TAG_HIT_WEIGHT'))
  post_data_df.drop(columns=['title_score', 'description_score', 'weighted_hashtag_score'], inplace=True) if postSchemaSearch.query else None
  
  post_data_df = post_data_df.sort_values(by='total_score', ascending=False).head(postSchemaSearch.limit if postSchemaSearch.limit else 10)
  
  return post_data_df.to_dict(orient='records')