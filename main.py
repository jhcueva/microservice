from config.config import Config
from src.scrapper import AttestationMicroservice

if __name__ == '__main__':
    scrapper = AttestationMicroservice(
    methodName='test_sign_in',
    user_name=Config().CAQH_USER_NAME,
    password=Config().CAQH_USER_PASSWORD,
    image_name='test'
    )
    scrapper.setUp()
    scrapper.test_review_and_attest()
