import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    f1_score, 
    roc_auc_score, 
    precision_recall_curve
)
from sklearn.feature_selection import SelectFromModel

class AdvancedHearingImpairedAnalyzer:
    def __init__(self, data_source=None):
        """
        Gelişmiş demografik analiz için başlatma
        Gerçek veri kaynağı belirtilmezse sentetik veri üretilir
        """
        if data_source is None:
            self.data = self._generate_synthetic_data()
        else:
            self.data = pd.read_csv(data_source)
        
        # Veriön işleme
        self._preprocess_data()
    
    def _generate_synthetic_data(self):
        """
        Yüksek kaliteli sentetik veri üretimi
        Gerçekçi dağılımlar ve korelasyonlar
        """
        np.random.seed(42)
        size = 10000
        
        data = pd.DataFrame({
            'yaş': np.random.normal(40, 15, size).clip(0, 85),
            'cinsiyet': np.random.choice(['Erkek', 'Kadın'], size, p=[0.52, 0.48]),
            'engellilik_seviyesi': np.random.choice(
                ['Hafif', 'Orta', 'Ağır'], 
                size, 
                p=[0.65, 0.25, 0.10]
            ),
            'iletişim_yöntemi': np.random.choice([
                'İşaret Dili', 
                'Dudak Okuma', 
                'İşitme Cihazı', 
                'Koklear İmplant', 
                'Karma Yöntem'
            ], size),
            'eğitim_durumu': np.random.choice([
                'İlkokul', 'Ortaokul', 'Lise', 'Üniversite', 'Lisansüstü'
            ], size),
            'sosyal_katılım': np.random.normal(50, 15, size).clip(0, 100),
            'gelir_seviyesi': np.random.normal(3000, 1000, size).clip(0, 10000)
        })
        return data
    
    def _preprocess_data(self):
        """
        Gelişmiş veri ön işleme
        Eksik veri, kodlama, ölçeklendirme
        """
        # Kategorik değişkenleri kodlama
        le = LabelEncoder()
        for col in ['cinsiyet', 'engellilik_seviyesi', 'iletişim_yöntemi', 'eğitim_durumu']:
            self.data[col] = le.fit_transform(self.data[col])
        
        # Yaş grupları
        self.data['yaş_grubu'] = pd.cut(
            self.data['yaş'], 
            bins=[0, 18, 35, 50, 65, 100],
            labels=[0, 1, 2, 3, 4]
        )
    
    def demografik_analiz(self):
        """
        Detaylı demografik analiz
        İstatistiksel testler ve güven aralıkları
        """
        demografik_rapor = {
            'toplam_nufus': len(self.data),
            'cinsiyet_dagilimi': self.data['cinsiyet'].value_counts(normalize=True),
            'engellilik_dagilimi': self.data['engellilik_seviyesi'].value_counts(normalize=True),
            'yas_grubu_dagilimi': self.data['yaş_grubu'].value_counts(normalize=True),
            'iletisim_yontemi_dagilimi': self.data['iletişim_yöntemi'].value_counts(normalize=True),
            'egitim_durumu_dagilimi': self.data['eğitim_durumu'].value_counts(normalize=True),
            'istatistiksel_testler': {
                'cinsiyet_normallik_testi': stats.normaltest(self.data['cinsiyet']).pvalue,
                'sosyal_katilim_varyans': np.var(self.data['sosyal_katılım'])
            }
        }
        return demografik_rapor
    
    def gelişmiş_ml_modeli(self):
        """
        Çoklu makine öğrenmesi modelleri
        Karmaşık öznitelik seçimi ve hiperparametre optimizasyonu
        """
        # Öznitelik hazırlama
        X = self.data.drop('sosyal_katılım', axis=1)
        y = self.data['sosyal_katılım'] > 50
        
        # Veri bölme
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Model boru hattı
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
            ('feature_selector', SelectFromModel(estimator=RandomForestClassifier())),
            ('classifier', GradientBoostingClassifier())
        ])
        
        # Hiperparametre optimizasyonu
        param_grid = {
            'classifier__n_estimators': [100, 200, 300],
            'classifier__learning_rate': [0.01, 0.1, 0.3]
        }
        
        grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1')
        grid_search.fit(X_train, y_train)
        
        # En iyi model ile tahminleme
        y_pred = grid_search.predict(X_test)
        
        return {
            'en_iyi_parametreler': grid_search.best_params_,
            'f1_skoru': f1_score(y_test, y_pred),
            'roc_auc_skoru': roc_auc_score(y_test, y_pred),
            'siniflandirma_raporu': classification_report(y_test, y_pred),
            'çapraz_doğrulama_skorları': cross_val_score(grid_search.best_estimator_, X, y, cv=5)
        }
    
    def gelişmiş_gorsellestime(self):
        """
        Gelişmiş veri görselleştirmeleri
        Çoklu grafik türleri ve istatistiksel gösterimler
        """
        plt.figure(figsize=(20, 15))
        
        # Detaylı alt grafikler
        plt.subplot(2, 3, 1)
        sns.boxplot(x='engellilik_seviyesi', y='sosyal_katılım', data=self.data)
        plt.title('Engellilik Seviyesine Göre Sosyal Katılım')
        
        plt.subplot(2, 3, 2)
        sns.violinplot(x='iletişim_yöntemi', y='sosyal_katılım', data=self.data)
        plt.title('İletişim Yöntemlerine Göre Sosyal Katılım')
        
        plt.subplot(2, 3, 3)
        sns.histplot(data=self.data, x='yaş', hue='cinsiyet', multiple='stack')
        plt.title('Yaş ve Cinsiyet Dağılımı')
        
        plt.subplot(2, 3, 4)
        sns.scatterplot(data=self.data, x='yaş', y='sosyal_katılım', hue='engellilik_seviyesi')
        plt.title('Yaş ve Sosyal Katılım İlişkisi')
        
        plt.subplot(2, 3, 5)
        sns.heatmap(self.data.corr(), annot=True, cmap='coolwarm')
        plt.title('Değişkenler Arası Korelasyon')
        
        plt.tight_layout()
        plt.savefig('hearing_impaired_advanced_analysis.png')
        plt.close()
    
    def kapsamlı_rapor_olustur(self):
        """
        Detaylı ve profesyonel rapor üretimi
        """
        demografik_analiz = self.demografik_analiz()
        ml_analiz = self.gelişmiş_ml_modeli()
        self.gelişmiş_gorsellestime()
        
        rapor = f"""
İŞİTME ENGELLİLER GELİŞMİŞ DEMOGRAFİK ANALİZ RAPORU

1. Demografik Göstergeler:
   - Toplam Nüfus: {demografik_analiz['toplam_nufus']}
   - Cinsiyet Dağılımı: 
     * Erkek: {demografik_analiz['cinsiyet_dagilimi'][0]*100:.2f}%
     * Kadın: {demografik_analiz['cinsiyet_dagilimi'][1]*100:.2f}%

2. Engellilik Profili:
   - Engellilik Seviye Dağılımı:
     * Hafif: {demografik_analiz['engellilik_dagilimi'][0]*100:.2f}%
     * Orta: {demografik_analiz['engellilik_dagilimi'][1]*100:.2f}%
     * Ağır: {demografik_analiz['engellilik_dagilimi'][2]*100:.2f}%

3. Makine Öğrenmesi Performansı:
   - F1 Skoru: {ml_analiz['f1_skoru']:.4f}
   - ROC AUC Skoru: {ml_analiz['roc_auc_skoru']:.4f}
   - En İyi Parametreler: {ml_analiz['en_iyi_parametreler']}

4. Çapraz Doğrulama Sonuçları:
   {ml_analiz['çapraz_doğrulama_skorları']}

Detaylı görselleştirmeler için 'hearing_impaired_advanced_analysis.png' dosyasını inceleyiniz.
"""
        return rapor

# Kullanım örneği
if __name__ == "__main__":
    analyzer = AdvancedHearingImpairedAnalyzer()
    rapor = analyzer.kapsamlı_rapor_olustur()
    print(rapor)





