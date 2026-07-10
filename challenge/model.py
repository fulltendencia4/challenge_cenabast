import pandas as pd
import numpy as np
import joblib

from typing import Tuple, Union, List
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder


class ReplenishmentModel:

    def __init__(self):
        self._model = None
        self._gtin_encoder = LabelEncoder()
        self._known_gtins = []
        self._feature_columns = []
        self._global_mean = 5.0

    def preprocess(self, data: pd.DataFrame, target_column: str = None) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        df = data.copy()
        
        if 'tipo_movimiento' in df.columns:
            df = df[df['tipo_movimiento'] == 'S'].copy()
        
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values(['gtin', 'fecha']).reset_index(drop=True)
        
        # Features temporales
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['dia_mes'] = df['fecha'].dt.day
        df['mes'] = df['fecha'].dt.month
        df['semana'] = df['fecha'].dt.isocalendar().week.astype(int)
        df['es_fin_de_semana'] = (df['dia_semana'] >= 5).astype(int)
        df['trimestre'] = df['fecha'].dt.quarter
        
        # Codificar gtin
        all_gtins = sorted(df['gtin'].unique())
        if target_column is not None:
            self._known_gtins = all_gtins
            self._gtin_encoder.fit(self._known_gtins)
        
        if len(self._known_gtins) > 0:
            df['gtin_encoded'] = self._gtin_encoder.transform(df['gtin'])
        else:
            df['gtin_encoded'] = 0
        
        # Lag features por producto
        df['consumo_7d'] = df.groupby('gtin')['cantidad'].transform(
            lambda x: x.shift(1).rolling(7, min_periods=1).mean()
        )
        df['consumo_30d'] = df.groupby('gtin')['cantidad'].transform(
            lambda x: x.shift(1).rolling(30, min_periods=1).mean()
        )
        df['consumo_anterior'] = df.groupby('gtin')['cantidad'].shift(1)
        
        # Llenar NaN
        for col in ['consumo_7d', 'consumo_30d', 'consumo_anterior']:
            df[col] = df[col].fillna(df.groupby('gtin')['cantidad'].transform('mean'))
            df[col] = df[col].fillna(self._global_mean)
        
        self._feature_columns = ['gtin_encoded', 'dia_semana', 'dia_mes', 'mes', 'semana',
                                  'es_fin_de_semana', 'trimestre', 'consumo_7d', 'consumo_30d', 'consumo_anterior']
        
        features = df[['gtin'] + self._feature_columns + ['fecha']].copy()
        
        if target_column is not None:
            target = df[[target_column]].copy()
            return features, target
        else:
            return features

    def fit(self, features: pd.DataFrame, target: pd.DataFrame) -> None:
        numeric_features = features[self._feature_columns]
        self._model = GradientBoostingRegressor(
            n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
        )
        self._model.fit(numeric_features, target.values.ravel())
        self._global_mean = float(target.values.mean())

    def predict(self, features: pd.DataFrame) -> List[dict]:
        if self._model is None:
            predictions = np.full(len(features), self._global_mean)
        else:
            numeric_features = features[self._feature_columns]
            predictions = self._model.predict(numeric_features)
        
        predictions = np.maximum(predictions, 0)
        
        result = []
        for i, pred in enumerate(predictions):
            fecha = features.iloc[i]['fecha'] if 'fecha' in features.columns else str(i)
            result.append({
                'fecha': str(fecha),
                'cantidad': float(pred)
            })
        return result

    def save(self, path: str) -> None:
        joblib.dump({
            'model': self._model,
            'gtin_encoder': self._gtin_encoder,
            'known_gtins': self._known_gtins,
            'feature_columns': self._feature_columns,
            'global_mean': self._global_mean
        }, path)

    def load(self, path: str) -> None:
        data = joblib.load(path)
        self._model = data['model']
        self._gtin_encoder = data['gtin_encoder']
        self._known_gtins = data['known_gtins']
        self._feature_columns = data['feature_columns']
        self._global_mean = data['global_mean']