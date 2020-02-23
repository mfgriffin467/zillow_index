# -*- coding: utf-8 -*-
"""tree_modelling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1chABXrH8sqpGBydBTUN5eDssiLT321kO

# Index modelling
"""

# from google.colab import drive
#drive.mount('/7Park_Data')
#drive.mount('/content/gdrive', force_remount=True)
#path = "/content/gdrive/My Drive/7Park Project/7Park_Data/"
#path = "/content/gdrive/My Drive/7Park_Data/"
path = "./"

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import math
import scipy
import matplotlib.pyplot as plt
import re
from scipy.cluster import hierarchy as hc
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import sklearn.model_selection as ms
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.metrics import r2_score
import graphviz
import IPython
from sklearn.tree import export_graphviz


#Display preferences
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 200)

import warnings
warnings.filterwarnings('ignore')
# %matplotlib inline

# Commented out IPython magic to ensure Python compatibility.
# Functions


def draw_tree(t, df, size=10, ratio=0.6, precision=0):
    s=export_graphviz(t, out_file=None, feature_names=df.columns, filled=True,
                      special_characters=True, rotate=True, precision=precision)
    IPython.display.display(graphviz.Source(re.sub('Tree {',
       f'Tree {{ size={size}; ratio={ratio}', s)))


def rf_feat_importance(m, df):
    return pd.DataFrame({'cols':df.columns, 'imp':m.feature_importances_}
                       ).sort_values('imp', ascending=False)

def forest_optimise(df_train,y_train,df_val,y_val,params):
  # ---------------------
  # Run grid search based on input parametrs
  # Use optimal parameters to train larger random forest of X estimators 
  # Output training and validation R^2 score, feature importance 
  # Add keep columns functonality
  # ---------------------

  rf = RandomForestRegressor()
  #default_params = {'n_estimators':[50], 'max_features' : ['sqrt','log2',0.1,0.2,0.5], 'min_samples_leaf' : [2,5,10,20,50,100,200]}
  search_rf = ms.GridSearchCV(rf, param_grid=params, cv=3, return_train_score=True, n_jobs=-1)
  print("Train times:")
#   %time search_rf.fit(df_train,y_train)
  grid_results = pd.DataFrame(search_rf.cv_results_).sort_values('mean_test_score', ascending=False).head()
  print(search_rf.best_params_)
  print("----------------")

  best_rf = RandomForestRegressor(max_features = search_rf.best_params_['max_features'], min_samples_leaf = search_rf.best_params_['min_samples_leaf'], n_estimators = 200, n_jobs = -1)
  print("Optimal model training time:")
#   %time best_rf.fit(df_train,y_train)
  print("----------------")
  print("Training R^2 score: ", best_rf.score(df_train,y_train))
  print("Validation R^2 score: ", best_rf.score(df_val,y_val))

  feat_imp = rf_feat_importance(best_rf, df_train)
  feat_imp.plot('cols', 'imp', 'barh', figsize=(10,10), legend=False)

  return grid_results, feat_imp, best_rf


def gbm_optimise(df_train,y_train,df_val,y_val,params):
  # ---------------------
  # Run grid search based on input parametrs
  # Use optimal parameters to train larger random forest of X estimators 
  # Output training and validation R^2 score, feature importance 
  # Add keep columns functonality
  # ---------------------

  gbm = GradientBoostingRegressor()
  search_gbm = ms.GridSearchCV(gbm, param_grid=params, cv=3, return_train_score=True)
  print("Train times:")
#   %time search_gbm.fit(df_train,y_train)
  grid_results = pd.DataFrame(search_gbm.cv_results_).sort_values('mean_test_score', ascending=False).head()
  print(search_gbm.best_params_)
  print("----------------")

  best_gbm = GradientBoostingRegressor(max_features = search_gbm.best_params_['max_features'], max_depth = search_gbm.best_params_['max_depth'], n_estimators = search_gbm.best_params_['n_estimators'], learning_rate = search_gbm.best_params_['learning_rate'])
  print("Optimal model training time:")
#   %time best_gbm.fit(df_train,y_train)
  print("----------------")
  print("Training R^2 score: ", best_gbm.score(df_train,y_train))
  print("Validation R^2 score: ", best_gbm.score(df_val,y_val))

  feat_imp = rf_feat_importance(best_gbm, df_train)
  feat_imp.plot('cols', 'imp', 'barh', figsize=(10,10), legend=False)

  return grid_results, feat_imp, best_gbm

"""## Read in consolidated datasets"""

template = pd.read_csv(path + 'template.csv',parse_dates=['date']) 
finance = pd.read_csv(path + 'Financial/finance_data.csv',parse_dates=['date'])
geo = pd.read_csv(path + 'Geo/US.csv')
acs = pd.read_csv(path + 'ACS Data/ACS_master_raw4.csv',parse_dates=['date'])
econ = pd.read_feather(path + 'Economic_Employment/all_economic_data')
housing = pd.read_feather(path + 'Housing Supply/combined_housing_permit')
society = pd.read_csv(path + 'Homicide_Hospitals_Schools/Schools_Hospitals_Crime.csv',parse_dates=['date'])
politics = pd.read_feather(path + 'Political Data/political_results')
weather = pd.read_feather(path + 'Weather/weather_state')
crime = pd.read_feather(path + 'FBI Data/crime_results')
eviction = pd.read_feather(path + 'Eviction Data/eviction_results')
air = pd.read_csv(path + 'Air Traffic/air_df_for_merge.csv',parse_dates=['date'])

finance.drop(['target'],axis=1, inplace=True)    
acs.drop(['Unnamed: 0','Unnamed: 0.1','CountyName','target','STATE', 'STCOUNTYFP'],axis=1, inplace=True)
geo.drop(['Country','City','State','State_Abbrv','County','Code'],axis=1, inplace=True)
econ.drop(['CountyName','STATE','STCOUNTYFP','GeoFIPS','target','year'],axis=1, inplace=True)
society.drop(['CountyName','STATE','STCOUNTYFP','target','year','Unnamed: 0'],axis=1, inplace=True)
housing.drop(['CountyName','target','STATE','STCOUNTYFP','year'],axis=1, inplace=True)
politics.drop(['STATE','CountyName','STCOUNTYFP','year','target'],axis=1, inplace=True)
weather.drop(['RegionName','target','zip','STCOUNTYFP','year'],axis=1, inplace=True)
crime.drop(['CountyName','target','STATE','STCOUNTYFP','year','fips_state_county'],axis=1, inplace=True)
eviction.drop(['CountyName','target','STATE','STCOUNTYFP','year'],axis=1, inplace=True)
air.drop(['Unnamed: 0'],axis=1, inplace=True)

finance.rename(columns=lambda x: 'fin_'+x, inplace = True)
acs.rename(columns=lambda x: 'acs_'+x, inplace = True)
econ.rename(columns=lambda x: 'econ_'+x, inplace = True)
housing.rename(columns=lambda x: 'house_'+x, inplace = True)
society.rename(columns=lambda x: 'society_'+x, inplace = True)
politics.rename(columns=lambda x: 'politics_'+x, inplace = True)
weather.rename(columns=lambda x: 'weather_'+x, inplace = True)
crime.rename(columns=lambda x: 'crime_'+x, inplace = True)
eviction.rename(columns=lambda x: 'evic_'+x, inplace = True)
air.rename(columns=lambda x: 'air_'+x, inplace = True)

acs.acs_date = acs.acs_date + pd.DateOffset(months=24)
crime.crime_date = crime.crime_date + pd.DateOffset(months=24)
econ.econ_date = econ.econ_date + pd.DateOffset(months=12)
eviction.evic_date = econ.econ_date + pd.DateOffset(months=12)

# print(finance.shape)
# print(geo.shape)
# print(acs.shape)
# print(econ.shape)
# print(housing.shape)
# print(society.shape)
# print(politics.shape)
# print(crime.shape)
# print(eviction.shape)
# print(air.shape)

"""## Merge datasets"""

df = pd.merge(finance, geo, how='left', left_on = 'fin_RegionName', right_on = 'ZIP')
df = df.merge(acs, how='left', left_on=['fin_RegionName','fin_date'], right_on=['acs_RegionName','acs_date'])
df = df.merge(econ, how='left', left_on=['fin_RegionName','fin_date'], right_on=['econ_RegionName','econ_date'])
df = df.merge(society, how='left', left_on=['fin_RegionName','fin_date'], right_on=['society_RegionName','society_date'])
df = df.merge(housing, how='left', left_on=['fin_RegionName','fin_date'], right_on=['house_RegionName','house_date'])
df = df.merge(politics, how='left', left_on=['fin_RegionName','fin_date'], right_on=['politics_RegionName','politics_date'])
df = df.merge(weather, how='left', left_on=['fin_STATE'], right_on=['weather_STATE'])
df = df.merge(crime, how='left', left_on=['fin_RegionName','fin_date'], right_on=['crime_RegionName','crime_date'])
df = df.merge(eviction, how='left', left_on=['fin_RegionName','fin_date'], right_on=['evic_RegionName','evic_date'])
df = df.merge(air[['air_YoY % Change', 'air_Total Enplanements']], how='left', left_index=True ,right_index=True)

df.drop(["fin_target_interpolate"], axis = 1, inplace = True)
template.drop(['CountyName', 'target', 'STATE', 'STCOUNTYFP', 'year'], axis = 1, inplace = True)
df = df.merge(template, how='left', left_on=['fin_RegionName','fin_date'], right_on=['RegionName','date'])

#df = df.merge(air, how='left', left_on=['fin_CountyName','fin_date','fin_STATE'], right_on=['air_CountyName','air_date','air_STATE'])

# Fix dates
df.drop(['fin_date', 'fin_STATE','fin_CountyName','acs_date','acs_year','econ_date','econ_Date_x','econ_Date_y','econ_RegionName','econ_target_interpolate','house_RegionName','house_date', 'RegionName',
         'politics_date','politics_RegionName','weather_STATE','crime_RegionName','crime_date','evic_date','evic_RegionName','evic_target_interpolate','society_RegionName','society_date', 'crime_target_interpolate'],axis=1, inplace=True)
df['year'] = pd.DatetimeIndex(df['date']).year
df['month'] = pd.DatetimeIndex(df['date']).month
startdate = pd.Timestamp('2010-09-01')
df['trend'] = (df['date'] - startdate).dt.days
df.set_index('date', inplace=True)
df.head()

"""# Imputation"""

# Use interpolate target, apply logs and drop blanks
df["target_lag_12m"] = df.groupby(["fin_RegionName"]).target_interpolate.shift(periods = 12)
df["target_lag_24m"] = df.groupby(["fin_RegionName"]).target_interpolate.shift(periods = 24)
df['target_lag_12m_YoY'] = df.target_lag_12m/df.target_lag_24m -1

df = df[~df.target_interpolate.isna()]
df.target_interpolate = np.log(df.target_interpolate)

# Define tree dataset with blanks as -999 and randomised input column
df_tree = df.fillna(-999)
df_tree['random_col'] = np.random.randint(0,1000,size=(len(df_tree), 1))
df_tree.reset_index(inplace=True)
df_tree.drop(['date'], axis=1, inplace= True)

# Define OLS dataset with region zips only
# df_ols = pd.get_dummies(df.fin_RegionName, drop_first=True)
# df_ols['year'] = df_ols.index.year
# df_ols['month'] = df_ols.index.month
# df_ols.reset_index(drop=True, inplace=True)
# print(df_ols.shape)

# Define GLM dataset 
df_linear = df.fillna(0)

"""# Dataset splits"""

#Generate tree data splits

df_train_tree = df_tree[df_tree.year.isin([2013,2014,2015,2016])].drop(['target_interpolate'],axis=1)
df_val_tree = df_tree[df_tree.year == 2017].drop(['target_interpolate'],axis=1)
df_test_tree = df_tree[df_tree.year == 2018].drop(['target_interpolate'],axis=1)
df_test_19_tree = df_tree[df_tree.year == 2019].drop(['target_interpolate'],axis=1)

breakpoint()

# df_train_ols = df_ols[df_ols.year.isin([2013,2014,2015,2016])]#.drop(['year'],axis=1)
# df_val_ols = df_ols[df_ols.year == 2017]#.drop(['year'],axis=1)
# df_test_ols = df_ols[df_ols.year == 2018]#.drop(['year'],axis=1)
# df_test_19_ols = df_ols[df_ols.year == 2019]#.drop(['year'],axis=1)

# items_to_delete = list(df_train_ols.loc[:, (df_train_ols == 0).all(axis=0)].columns)
# df_train_ols.drop(items_to_delete, axis = 1, inplace = True)
# df_val_ols.drop(items_to_delete, axis = 1, inplace = True)
# df_test_ols.drop(items_to_delete, axis = 1, inplace = True)
# df_test_19_ols.drop(items_to_delete, axis = 1, inplace = True)

# y_train = df[df.year.isin([2013,2014,2015,2016])]['target_interpolate'].ravel()
# y_val = df[df.year == 2017]['target_interpolate'].ravel()
# y_test = df[df.year == 2018]['target_interpolate'].ravel()
# y_test_19 = df[df.year == 2019]['target_interpolate'].ravel()

 
"""# OLS modelling"""

# df_comb_train = pd.concat([df_train_ols,df_val_ols],axis=0)
# y_comb_train = np.concatenate((y_train, y_val),axis=0)

# df_comb_19_train = pd.concat([df_train_ols,df_val_ols,df_test_ols],axis=0)
# y_comb_19_train = np.concatenate((y_train, y_val, y_test),axis=0)

# ols_train = LinearRegression(n_jobs=-1,fit_intercept = True)
# ols_train.fit(df_train_ols,y_train)

# ols_comb = LinearRegression(n_jobs=-1,fit_intercept = True)
# ols_comb.fit(df_comb_train,y_comb_train)

# ols_comb_19 = LinearRegression(n_jobs=-1,fit_intercept = True)
# ols_comb_19.fit(df_comb_19_train,y_comb_19_train)

# print(ols_train.score(df_train_ols,y_train))
# print(ols_train.score(df_val_ols,y_val))
# print(ols_comb.score(df_test_ols,y_test))
# print(ols_comb_19.score(df_test_19_ols,y_test_19))

# print(r2_score(ols_train.predict(df_train_ols),y_train))
# print(r2_score(ols_train.predict(df_val_ols),y_val))

"""## LASSO modelling on residuals from spyder"""
# =============================================================================
# 
# residuals = pd.read_csv(path + 'Residual Modeling/residuals.csv', parse_dates=['date'])
# df_intermediate = df.reset_index().copy()
# df_lasso = df_intermediate.merge(residuals, how='left', left_on = ['fin_RegionName','date'], right_on = ['RegionName','date'], indicator = False)
# 
# df_lasso = df_lasso.sort_values(axis = 0, by = ["RegionName", "date"])
# df_lasso.set_index(["RegionName", "date"], inplace = True)
# 
# for var_name in list((df_lasso.isna().sum() != 0).index):
#   if var_name != "year" and var_name != "lagged_12" and var_name != "residuals" and var_name != "target_interpolate":
#     df_lasso[var_name] = df_lasso[var_name] - df_lasso.groupby('RegionName')[var_name].shift(periods = 12)
# 
# df_lasso = df_lasso[df_lasso["year"] >= 2014]
# 
# for var_name in list((df_lasso.isna().sum() != 0).index):
#   if var_name != "year" and var_name != "lagged_12" and var_name != "residuals" and var_name != "target_interpolate":
#     df_lasso[var_name] = df_lasso[var_name].fillna(df_lasso.groupby('year')[var_name].transform('mean'))
#     df_lasso[var_name] = df_lasso[var_name].fillna(df_lasso[var_name].mean())
# 
# df_lasso = df_lasso[~df_lasso.target_interpolate.isna()]
# df_lasso = df_lasso[df_lasso.residuals.abs() < .50]
# print(df_lasso.head())
# 
# df_lasso.dropna(axis = 1, how = "any", inplace = True)
# 
# y_train_lasso = df_lasso[df_lasso.year.isin([2015,2016])]['residuals'].ravel()
# y_val_lasso = df_lasso[df_lasso.year == 2017]['residuals'].ravel()
# y_test_lasso = df_lasso[df_lasso.year == 2018]['residuals'].ravel()
# y_test_19_lasso = df_lasso[df_lasso.year == 2019]['residuals'].ravel()
# 
# df_train_lasso = df_lasso[df_lasso.year.isin([2015,2016])].drop(['target_interpolate', 'residuals'],axis=1)
# df_train_lasso = df_train_lasso.loc[:, df_train_lasso.columns.str.startswith('econ')]
# df_val_lasso = df_lasso[df_lasso.year == 2017].drop(['target_interpolate', 'residuals'],axis=1)
# df_val_lasso = df_val_lasso.loc[:, df_val_lasso.columns.str.startswith('econ')]
# df_test_lasso = df_lasso[df_lasso.year == 2018].drop(['target_interpolate', 'residuals'],axis=1)
# df_test_lasso = df_test_lasso.loc[:, df_test_lasso.columns.str.startswith('econ')]
# df_test_19_lasso = df_lasso[df_lasso.year == 2019].drop(['target_interpolate', 'residuals'],axis=1)
# df_test_19_lasso = df_test_19_lasso.loc[:, df_test_19_lasso.columns.str.startswith('econ')]
# 
# def rmse(x,y): return math.sqrt(((x-y)**2).mean())
# 
# lasso = Lasso(normalize=False, fit_intercept = True)
# lasso.set_params(alpha=12, normalize=False, fit_intercept = True)
# lasso.fit(df_train_lasso, y_train_lasso)
# print(lasso.score(df_train_lasso, y_train_lasso))
# 
# res = [lasso.score(df_val_lasso, y_val_lasso), lasso.score(df_test_lasso, y_test_lasso), lasso.score(df_test_19_lasso, y_test_19_lasso)]
# print(res)
# 
# =============================================================================
"""## Tree modelling on residuals from spyder"""

residuals = pd.read_csv(path + 'Residual Modeling/residuals.csv', parse_dates=['date'])
df_intermediate = df.reset_index().drop(["target_interpolate"], axis = 1)
df_residuals = df_intermediate.merge(residuals, how='left', left_on = ['fin_RegionName','date'], right_on = ['RegionName','date'], indicator = True)
df_residuals.drop(['_merge'], axis=1, inplace= True)

# Define tree dataset with blanks as -999 and randomised input column
df_tree_resi = df_residuals.fillna(-999)
df_tree_resi['random_col'] = np.random.randint(0,1000,size=(len(df_tree), 1))
df_tree_resi['year'] = pd.DatetimeIndex(df_tree_resi['date']).year

df_tree_resi.drop(['date','RegionName'], axis=1, inplace= True)

df_train_tree_resi = df_tree_resi[df_tree_resi.year.isin([2015,2016])].drop(['target_interpolate','residuals'],axis=1)
df_val_tree_resi = df_tree_resi[df_tree_resi.year == 2017].drop(['target_interpolate','residuals'],axis=1)
df_test_tree_resi = df_tree_resi[df_tree_resi.year == 2018].drop(['target_interpolate','residuals'],axis=1)
df_test_19_tree_resi = df_tree_resi[df_tree_resi.year == 2019].drop(['target_interpolate','residuals'],axis=1)

y_train_resi = df_tree_resi[df_tree_resi.year.isin([2015,2016])]['residuals'].ravel()
y_val_resi = df_tree_resi[df_tree_resi.year == 2017]['residuals'].ravel()
y_test_resi = df_tree_resi[df_tree_resi.year == 2018]['residuals'].ravel()
y_test_19_resi = df_tree_resi[df_tree_resi.year == 2019]['residuals'].ravel()

breakpoint()

#Fit spyder residuals
params = {'n_estimators':[10], 'max_features' : [0.5], 'min_samples_leaf' : [1]}
#params = {'n_estimators':[50], 'max_features' : ['sqrt','log2',0.1,0.5,1], 'min_samples_leaf' : [5,10,20,50,100]}
grid_results_residual2, feat_imp_residual2, rf_residual2 = forest_optimise(df_train_tree_resi,y_train_resi,df_val_tree_resi,y_val_resi,params)

feat_imp_residual2.head(20)

print(r2_score(rf_residual2.predict(df_test_tree_resi),y_test_resi))
print(r2_score(rf_residual2.predict(df_test_19_tree_resi),y_test_19_resi))

###############################################################################################33

# Final model as composite



"""# Simple OLS residuals"""

residuals_train = y_train - ols_train.predict(df_train_ols)
residuals_val = y_val - ols_train.predict(df_val_ols)

# fit tree
dec_tree = RandomForestRegressor(n_estimators=1, max_depth=3, bootstrap=False, n_jobs=-1)
dec_tree.fit(df_train_tree,residuals_train)
draw_tree(dec_tree.estimators_[0], df_train_tree, precision=2)

#params = {'n_estimators':[30], 'max_features' : ['sqrt','log2',0.1,0.5], 'min_samples_leaf' : [2,5,10,20,50]}
params = {'max_features': ['sqrt'], 'min_samples_leaf': [20], 'n_estimators': [100]}
grid_results_residuals, feat_imp_residuals, best_rf_residuals = forest_optimise(df_train_tree,residuals_train,df_val_tree,residuals_val,params)


#best_rf = RandomForestRegressor(max_features=0.5, min_samples_leaf=20, n_estimators=30, n_jobs=-1)
#best_rf.fit(df_train_tree,residuals_train)

feat_imp = rf_feat_importance(best_rf_residuals, df_train_tree)
feat_top = feat_imp.head(40)
feat_top.plot('cols', 'imp', 'barh', figsize=(10,10), legend=False)

feat_imp['category'] = feat_imp['cols'].str[0:3]
feat_imp.groupby('category').sum().sort_values('imp', ascending=False)

feat_imp[feat_imp.cols == 'random_col']

# Final model as composite

prediction_train = ols_train.predict(df_train_ols) + best_rf_residuals.predict(df_train_tree)
prediction_val = ols_train.predict(df_val_ols) + best_rf_residuals.predict(df_val_tree)
prediction_test = ols_comb.predict(df_test_ols) + best_rf_residuals.predict(df_test_tree)
prediction_test_19 = ols_comb_19.predict(df_test_19_ols) + best_rf_residuals.predict(df_test_19_tree)

print(r2_score(prediction_train,y_train))
print(r2_score(prediction_val,y_val))
print(r2_score(prediction_test,y_test))
print(r2_score(prediction_test_19,y_test_19))

"""## Tree modelling (pure, no OLS)"""

params = {'n_estimators':[10], 'max_features' : ['sqrt','log2',0.1,0.2,0.5], 'min_samples_leaf' : [2,5,10,20]}
#params = {'max_features': [0.5], 'min_samples_leaf': [20], 'n_estimators': [10]}
grid_results_all, feat_imp_all, pure_rf = forest_optimise(df_train_tree,y_train,df_val_tree,y_val,params)

feat_imp_all['category'] = feat_imp_all['cols'].str[0:3]
feat_imp_all.groupby('category').sum()

"""## No rental variables, tree model"""

#non_rent = feat_imp_all[feat_imp_all.imp>0.005].cols

non_rent = df_train_tree.columns.drop(list(df_train_tree.filter(regex='rent')))

df_train_tree_nonrent = df_train_tree[non_rent] 
df_val_tree_nonrent =  df_val_tree[non_rent]
df_test_tree_nonrent =  df_test_tree[non_rent]

params = {'n_estimators':[10], 'max_features' : ['sqrt','log2',0.1,0.2,0.5], 'min_samples_leaf' : [2,5,10,20,30,50]}
#{'max_features': 'sqrt', 'min_samples_leaf': 20, 'n_estimators': 30}
grid_results_top, feat_imp_top, rt_top = forest_optimise(df_train_tree_nonrent,y_train,df_val_tree_nonrent,y_val,params)

params = {'n_estimators':[10], 'max_features' : ['sqrt'], 'min_samples_leaf' : [20]}
#{'max_features': 'sqrt', 'min_samples_leaf': 20, 'n_estimators': 30}
grid_results_top, feat_imp_top, rt_top = forest_optimise(df_train_tree_nonrent,y_train,df_val_tree_nonrent,y_val,params)

feat_imp_top.head(100)

"""## Consolidated model"""

to_keep = feat_imp_all[feat_imp_all.imp>0.005].cols

df_train_tree2 = df_train_tree[to_keep] 
df_val_tree2 =  df_val_tree[to_keep]
df_test_tree2 =  df_test_tree[to_keep]

params = {'n_estimators':[30], 'max_features' : ['sqrt','log2',0.1,0.2,0.5], 'min_samples_leaf' : [2,5,10,20,30,50]}
#{'max_features': 'sqrt', 'min_samples_leaf': 20, 'n_estimators': 30}
grid_results_top, feat_imp_top, rt_top = forest_optimise(df_train_tree2,y_train,df_val_tree2,y_val,params)

corr = np.round(scipy.stats.spearmanr(df_train_tree2).correlation, 4)
corr_condensed = hc.distance.squareform(1-corr)
z = hc.linkage(corr_condensed, method='average')
fig = plt.figure(figsize=(10,12))
dendrogram = hc.dendrogram(z, labels=df_train_tree2.columns, orientation='left', leaf_font_size=16)
plt.show()

to_keep_manual = ['target_lag_12m','target_lag_24m',
                  'Longitude','Latitude','fin_STCOUNTYFP',
                  'econ_Local_Weekly_Wages','acs_median_rent_cty','econ_Scenic_sightseeing_transportation','econ_Social_assistance','econ_Unclassified_Quarterly_Wages','econ_Per_capita_income',
                  'acs_asian_pop_cty',
                  'econ_Other_information_services',
                  'econ_Private_households',
                 'acs_commuters_by_public_transportation_cty','acs_walked_to_work_cty','acs_commute_60_89_mins_cty',
                  'politics_third_party'
                  ]

df_keep_manual = df[to_keep_manual]
df_train_tree3 = df_train_tree[to_keep_manual] 
df_val_tree3 = df_val_tree[to_keep_manual]
df_test_tree3 =  df_test_tree[to_keep_manual]

#params = {'n_estimators':[30], 'max_features' : ['sqrt','log2',0.1,0.2,0.5], 'min_samples_leaf' : [2,5,10,20]}
params = {'max_features': [0.5], 'min_samples_leaf': [20], 'n_estimators': [30]}
grid_results_manual, feat_imp_manual, rf_manual = forest_optimise(df_train_tree3,y_train,df_val_tree3,y_val,params)

rf_final = RandomForestRegressor(n_jobs=-1,max_features=0.5, min_samples_leaf=20, n_estimators=200)

#df_train_tree2 = df_train_tree[to_keep] 
#df_val_tree2 =  df_val_tree[to_keep]
#df_test_tree2 =  df_test_tree[to_keep]

#Test1 performance
rf_final.fit(pd.concat([df_train_tree2,df_val_tree2],axis=0),y_comb_train)
rf_final_pred = rf_final.predict(df_test_tree2)
print(r2_score(rf_final_pred,y_test))

#Test 2019 performance

#params = {'n_estimators': [30,50,80], 'max_depth':[5,8], 'learning_rate': [0.05,0.1,0.2], 'max_features' : ['sqrt','log2',0.1,0.5], 'subsample': [0.8]}
params = {'n_estimators': [50], 'max_depth':[5], 'learning_rate': [0.05], 'max_features' : [0.5], 'subsample': [0.8]}
grid_results_gbm, feat_imp_gbm , manual_gbm = gbm_optimise(df_train_tree3,y_train,df_val_tree3,y_val,params)

