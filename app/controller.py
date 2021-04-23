import logging
from app.config import config
#from app.factory.get_data import GetDataModelClass
#from app.factory.clean_data import CleanDataClass
#from app.factory.build_features import FeatureEngineeringClass
#from app.models.train_models import ModelTrainingClass
#from app.models.predict_models import PredictModelClass


class MainControllerCass:
    def __init__(self):
        self.logger = logging.getLogger(f'{config.LOGGER_NAME}')

    def ml_pipeline_controller(self):

        ml_pipeline = dict(import_data=False,
                           clean_data=False,
                           features_eng=False,
                           train_model=True,
                           predict_results=True)

        if ml_pipeline['import_data']:
            self.logger.info("# IMPORT RAW DATA #")
            # Import raw data
            get_data = GetDataModelClass()
            get_data.import_raw_data()
            
        if ml_pipeline['clean_data']:
            self.logger.info("# CLEAN DATA #")
            # Clean data set
            clean_data = CleanDataClass()
            clean_data.data_cleaning_process()

        if ml_pipeline['features_eng']:
            self.logger.info("# FEATURE ENGINEERING #")
            # Engineer required features
            feature_eng = FeatureEngineeringClass()
            feature_eng.feature_engineering()

        if ml_pipeline['train_model']:
            self.logger.info("# MODEL TRAINING #")
            # Train model
            train_model_instance = ModelTrainingClass()
            train_model_instance.model_training()

        if ml_pipeline['predict_results']:
            self.logger.info("# PREDICT RESULTS #")
            # Predict results
            predict_instance = PredictModelClass()
            predict_instance.predict_results()
