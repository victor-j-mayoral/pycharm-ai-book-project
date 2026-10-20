from datetime import datetime
import logging


# GDPR-compliant data pipeline
class PrivacyCompliantPipeline:

    def __init__(self):
        self.consent_db = ConsentManager()
        self.audit_logger = AuditLogger()
        
    def process_user_data(self, user_id, data):
        # Check consent
        consent = self.consent_db.get_consent(user_id)
        if not consent.has_permission('ml_training'):
            return None
        # Log access
        self.audit_logger.log_access(
            user_id=user_id,
            purpose='model_training',
            timestamp=datetime.now(),
            data_types=['purchase_history', 'browsing_behavior']
        )
         # Process with purpose limitation
        processed = self.extract_permitted_features(data, consent)
        
        return processed

         
    def handle_deletion_request(self, user_id):
        # Remove from training data
        self.remove_from_datasets(user_id)
        # Document deletion
        deletion_record = {
            'user_id': user_id,
            'timestamp': datetime.now(),
            'datasets_affected': self.find_affected_datasets(user_id),
            'models_requiring_update': self.find_affected_models(user_id)
        }
         # Schedule model retraining
        self.schedule_retraining(deletion_record['models_requiring_update'])
        
        return deletion_record


class ConsentManager:

    def __init__(self):
        # A dictionary to store user consents
        # Format: {user_id: {purpose: consent_status}}
        self.consent_records = {}

    def get_consent(self, user_id, purpose):
        """
        Check if a user has granted consent for a specific purpose.

        Args:
            user_id (str): The unique identifier of the user.
            purpose (str): The purpose for which consent is being checked.

        Returns:
            bool: True if consent is granted, False otherwise.
        """
        # Check if the user exists and has consent for the given purpose
        if user_id in self.consent_records:
            return self.consent_records[user_id].get(purpose, False)
        return False

    def grant_consent(self, user_id, purpose):
        """
        Grant consent for a specific purpose.

        Args:
            user_id (str): The unique identifier of the user.
            purpose (str): The purpose for which consent is being granted.
        """
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}
        self.consent_records[user_id][purpose] = True

    def revoke_consent(self, user_id, purpose):
        """
        Revoke consent for a specific purpose.

        Args:
            user_id (str): The unique identifier of the user.
            purpose (str): The purpose for which consent is being revoked.
        """
        if user_id in self.consent_records:
            self.consent_records[user_id][purpose] = False


class AuditLogger:
    def __init__(self, name: str = "audit", level: int = logging.INFO, log_file: str = None):
        """
        Inicializa un logger para auditorías.

        Args:
            name (str): Nombre del logger.
            level (int): Nivel de registro (INFO, DEBUG, etc.).
            log_file (str): Ruta del archivo donde se guardarán los logs (opcional).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Evitar duplicar handlers si ya existen
        if not self.logger.handlers:
            # Configurar un handler para la consola
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # Configurar un handler para archivo (opcional)
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

    def log_access(self, user: str, purpose: str, ts: str, data_types: str):
        """
        Registra un acceso a datos con un propósito específico.

        Args:
            user (str): Usuario que realiza la acción.
            purpose (str): Propósito para el cual se registra el acceso.
            ts (str): Marca de tiempo de la acción.
            data_types (str): Tipos de datos accedidos.
        """
        self.logger.info(
            f"user={user} purpose={purpose} ts={ts} data_types={data_types}"
        )