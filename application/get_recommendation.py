import pandas as pd
from load_model import load_models
from load_features import load_features
from datetime import timedelta
import datetime
from hashlib import md5

def get_recomendation(id, time, limit=10, user_features, model):
    end_time = time + timedelta(hours=1)
    user_info = ['user_id', 'gender', 'age', 'country', 'city', 'os', 'source', 'user_rate']
    X = user_features[(user_features['user_id']==id)]
    users_post = X['post_id'].unique()
    Y = user_features[~(user_features['user_id'] == id)]
    Y = Y[~(Y['post_id'].isin(users_post))]
    Y = Y[(pd.to_datetime(Y['timestamp']) >= time) & (pd.to_datetime(Y['timestamp']) < end_time)].copy()
    if len(Y)==0:
        print('Для данного пользователя нет рекомендованных постов за это время.')
    
    Y = Y.drop(user_info, axis=1)
    Y['user_id'] = id
    for col in user_info:
        Y[col] = X[X['user_id'] == id][col][0]
        
    Y = Y[user_features.columns]   

    assert all(Y[user_features.columns].columns == user_features.columns)
    Y_train = Y.drop('target', axis=1)
    Y_train = Y_train.drop(['user_id', 'post_id', 'exp_group', 'text', 'timestamp'], axis=1)
    Y['prob'] = model.predict_proba(Y_train)[:, 1]
    Y['pred'] = model.predict(Y_train)
    posts = Y[Y['pred'] == 1].sort_values(by='prob', ascending=False)['post_id'][:limit].to_list()
    return posts

'''Реализуйте функцию, которая по user_id пользователя будет определять, в какую группу попал пользователь (не используйте exp_group из таблички с информацией про пользователей). Для этого используйте одну из хэш-функций (например md5 из библиотеки hashlib), используйте соль. Сами параметры разбиения (конкретное значение соли, проценты для разбиения 50 на 50) вынесите для удобства в константы вашего решения (обычно при развитии сервиса сами настройки переезжают в «админку», но пока у нас будет попроще).'''

def get_exp_group(user_id: int, salt='recomendation_testing_a/b_1', n_groups=2)-> str:
    hash_value = int(md5((str(user_id) + salt).encode()).hexdigest(), 16)
    if hash_value % n_groups==0:
        return 'control'
    return 'test'

'''Вынесите в две отдельные функции построение рекомендаций двумя моделями (из второго и из третьего блока), чтобы можно было удобно вызывать их. Модели, которые вы загружаете, будут называться соответственно model_control, model_test.'''

def model_control(user_id, time):
    model = control_model
    user_features = user_features
    posts = get_recomendation(user_id, time, limit=10, user_features, model)
    return posts

def model_test(user_id, time):
    model = test_model
    user_features = user_features_2
    posts = get_recomendation(user_id, time, limit=10, user_features, model)
    return posts